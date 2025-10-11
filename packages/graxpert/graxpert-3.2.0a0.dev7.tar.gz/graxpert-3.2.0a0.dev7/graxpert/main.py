import os
import platform
import sys

# ensure sys.stdout and sys.stderr are not None in PyInstaller environments
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
import argparse
import logging
import multiprocessing
import re
import sys
import faulthandler
import types

from packaging import version

# Must be before all other graxpert imports
try:
    # A load-time check for key external package dependencies. Crash and warn user.
    import tkinter
except ImportError:
    # If it fails, print a helpful message and exit.
    print("ERROR: The required 'tkinter' GUI library is not installed.", file=sys.stderr)
    print("\nPlease install it using your system's package manager.", file=sys.stderr)
    print("  For Debian/Ubuntu: sudo apt-get install python3-tk", file=sys.stderr)
    print("  For Fedora:        sudo dnf install python3-tkinter", file=sys.stderr)
    print("  For Arch Linux:    sudo pacman -S tk", file=sys.stderr)
    print("  For OS-X:          brew install python-tk", file=sys.stderr)
    print("  For Windows:       It should be included with your Python installation by default.", file=sys.stderr)
    sys.exit(1) # Exit with error


from graxpert.ai_model_handling import bge_ai_models_dir, denoise_ai_models_dir, deconvolution_object_ai_models_dir, deconvolution_stars_ai_models_dir, list_local_versions, list_remote_versions
from graxpert.mp_logging import configure_logging
from graxpert.s3_secrets import bge_bucket_name, denoise_bucket_name, deconvolution_object_bucket_name, deconvolution_stars_bucket_name
from graxpert.version import release as graxpert_release
from graxpert.version import version as graxpert_version
from graxpert.resource_utils import temp_cleanup

def collect_available_versions(ai_models_dir, bucket_name):

    try:
        available_local_versions = sorted(
            [v["version"] for v in list_local_versions(ai_models_dir)],
            key=lambda k: version.parse(k),
            reverse=True,
        )
    except Exception as e:
        available_local_versions = ""
        logging.exception(e)
    try:
        available_remote_versions = sorted(
            [v["version"] for v in list_remote_versions(bucket_name)],
            key=lambda k: version.parse(k),
            reverse=True,
        )
    except Exception as e:
        available_remote_versions = ""
        logging.exception(e)

    return (available_local_versions, available_remote_versions)


def bge_version_type(arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$")):
    return version_type(bge_ai_models_dir, bge_bucket_name, arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$"))


def denoise_version_type(arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$")):
    return version_type(denoise_ai_models_dir, denoise_bucket_name, arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$"))


def deconv_obj_version_type(arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$")):
    return version_type(deconvolution_object_ai_models_dir, deconvolution_object_bucket_name, arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$"))


def deconv_stellar_version_type(arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$")):
    return version_type(deconvolution_stars_ai_models_dir, deconvolution_stars_bucket_name, arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$"))


def version_type(ai_models_dir, bucket_name, arg_value, pat=re.compile(r"^\d+\.\d+\.\d+$")):

    available_versions = collect_available_versions(ai_models_dir, bucket_name)
    available_local_versions = available_versions[0]
    available_remote_versions = available_versions[1]

    if not pat.match(arg_value):
        raise argparse.ArgumentTypeError("invalid version, expected format: n.n.n")
    if arg_value not in available_local_versions and arg_value not in available_remote_versions:
        raise argparse.ArgumentTypeError(
            "provided version neither found locally or remotely; available locally: [{}], available remotely: [{}]".format(
                ", ".join(available_local_versions),
                ", ".join(available_remote_versions),
            )
        )
    if not available_local_versions and not available_remote_versions:
        raise argparse.ArgumentTypeError("no AI versions available locally or remotely")
    return arg_value


def ui_main(open_with_file=None):
    import logging
    import tkinter as tk
    from concurrent.futures import ProcessPoolExecutor
    from datetime import datetime
    from inspect import signature
    from tkinter import messagebox

    import requests
    from appdirs import user_config_dir
    from customtkinter import CTk

    from graxpert.application.app import graxpert
    from graxpert.application.app_events import AppEvents
    from graxpert.application.eventbus import eventbus
    from graxpert.localization import _
    from graxpert.mp_logging import initialize_logging, shutdown_logging
    from graxpert.parallel_processing import executor
    from graxpert.preferences import app_state_2_prefs, save_preferences
    from graxpert.resource_utils import resource_photoimage
    from graxpert.ui.application_frame import ApplicationFrame
    from graxpert.ui.styling import style
    from graxpert.ui.ui_events import UiEvents
    from graxpert.version import release, version

    def on_closing(root: CTk, logging_thread):
        app_state_2_prefs(graxpert.prefs, graxpert.cmd.app_state)

        prefs_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")
        save_preferences(prefs_filename, graxpert.prefs)
        try:
            if "cancel_futures" in signature(ProcessPoolExecutor.shutdown).parameters:
                executor.shutdown(cancel_futures=True)  # Python > 3.8
            else:
                executor.shutdown()  # Python <= 3.8

        except Exception as e:
            logging.exception("error shutting down ProcessPoolExecutor")
        shutdown_logging(logging_thread)
        root.destroy()
        logging.shutdown()
        sys.exit(0)

    def check_for_new_version():
        try:
            response = requests.get("https://api.github.com/repos/Steffenhir/GraXpert/releases/latest", timeout=2.5)
            latest_release_date = datetime.strptime(response.json()["created_at"], "%Y-%m-%dT%H:%M:%SZ")

            response_current = requests.get("https://api.github.com/repos/Steffenhir/GraXpert/releases/tags/" + version, timeout=2.5)
            current_release_date = datetime.strptime(response_current.json()["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            current_is_beta = response_current.json()["prerelease"]

            if current_is_beta:
                if current_release_date >= latest_release_date:
                    messagebox.showinfo(
                        title=_("This is a Beta release!"), message=_("Please note that this is a Beta release of GraXpert. You will be notified when a newer official version is available.")
                    )
                else:
                    messagebox.showinfo(
                        title=_("New official release available!"),
                        message=_("This Beta version is deprecated. A newer official release of GraXpert is available at") + " https://github.com/Steffenhir/GraXpert/releases/latest",
                    )

            elif latest_release_date > current_release_date:
                messagebox.showinfo(title=_("New version available!"), message=_("A newer version of GraXpert is available at") + " https://github.com/Steffenhir/GraXpert/releases/latest")
        except:
            logging.warning("Could not check for newest version")

    logging_thread = initialize_logging()

    style()
    root = CTk()

    try:
        if "Linux" == platform.system():
            root.attributes("-zoomed", True)
        else:
            root.state("zoomed")
    except Exception as e:
        root.state("normal")
        logging.warning(e, stack_info=True)

    root.title("GraXpert | Release: '{}' ({})".format(release, version))
    root.iconbitmap()
    root.iconphoto(True, resource_photoimage("Icon.png"))
    # root.option_add("*TkFDialog*foreground", "black")
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, logging_thread))
    root.createcommand("::tk::mac::Quit", lambda: on_closing(root, logging_thread))
    root.minsize(width=800, height=600)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    app = ApplicationFrame(root)
    app.grid(column=0, row=0, sticky=tk.NSEW)
    root.update()
    check_for_new_version()

    if open_with_file and len(open_with_file) > 0:
        eventbus.emit(AppEvents.LOAD_IMAGE_REQUEST, {"filename": open_with_file})
    else:
        eventbus.emit(UiEvents.DISPLAY_START_BADGE_REQUEST)

    root.mainloop()


def parse_args():
    available_bge_versions = collect_available_versions(bge_ai_models_dir, bge_bucket_name)
    available_denoise_versions = collect_available_versions(denoise_ai_models_dir, denoise_bucket_name)
    available_deconv_obj_versions = collect_available_versions(deconvolution_object_ai_models_dir, deconvolution_object_bucket_name)
    available_deconv_stellar_versions = collect_available_versions(deconvolution_stars_ai_models_dir, deconvolution_stars_bucket_name)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-cmd",
        "--command",
        required=False,
        default="background-extraction",
        choices=["background-extraction", "denoising", "deconv-obj", "deconv-stellar"],
        type=str,
        help="Choose the image operation to execute: Background Extraction or Denoising or Deconvolution",
    )
    parser.add_argument("filename", type=str, help="Path of the unprocessed image")
    parser.add_argument("-output", "--output", nargs="?", required=False, type=str, help="Filename of the processed image")
    parser.add_argument(
        "-preferences_file",
        "--preferences_file",
        nargs="?",
        required=False,
        default=None,
        type=str,
        help="Allows GraXpert commandline to run all extraction methods based on a preferences file that contains background grid points",
    )
    parser.add_argument("-gpu", "--gpu_acceleration", type=str, choices=["true", "false"], default=None, help="Set to 'false' in order to disable gpu acceleration during AI inference.")
    parser.add_argument("-v", "--version", action="version", version=f"GraXpert version: {graxpert_version} release: {graxpert_release}")
    parser.add_argument("-cli", "--cli", required=False, action="store_true", help="Deprecated (no longer required)")

    bge_parser = argparse.ArgumentParser("GraXpert Background Extraction", parents=[parser], description="GraXpert, the astronomical background extraction tool")
    bge_parser.add_argument(
        "-ai_version",
        "--ai_version",
        nargs="?",
        required=False,
        default=None,
        type=bge_version_type,
        help='Version of the Background Extraction AI model, default: "latest"; available locally: [{}], available remotely: [{}]'.format(
            ", ".join(available_bge_versions[0]), ", ".join(available_bge_versions[1])
        ),
    )
    bge_parser.add_argument("-correction", "--correction", nargs="?", required=False, default=None, choices=["Subtraction", "Division"], type=str, help="Subtraction or Division")
    bge_parser.add_argument("-smoothing", "--smoothing", nargs="?", required=False, default=None, type=float, help="Strength of smoothing between 0 and 1")
    bge_parser.add_argument("-bg", "--bg", required=False, action="store_true", help="Also save the background model")

    denoise_parser = argparse.ArgumentParser("GraXpert Denoising", parents=[parser], description="GraXpert, the astronomical denoising tool")
    denoise_parser.add_argument(
        "-ai_version",
        "--ai_version",
        nargs="?",
        required=False,
        default=None,
        type=denoise_version_type,
        help='Version of the Denoising AI model, default: "latest"; available locally: [{}], available remotely: [{}]'.format(
            ", ".join(available_denoise_versions[0]), ", ".join(available_denoise_versions[1])
        ),
    )
    denoise_parser.add_argument(
        "-strength",
        "--denoise_strength",
        nargs="?",
        required=False,
        default=None,
        type=float,
        help='Strength of the desired denoising effect, default: "0.5"',
    )
    denoise_parser.add_argument(
        "-batch_size",
        "--ai_batch_size",
        nargs="?",
        required=False,
        default=None,
        type=int,
        help='Number of image tiles which Graxpert will denoise in parallel. Be careful: increasing this value might result in out-of-memory errors. Valid Range: 1..32, default: "4"',
    )

    deconv_obj_parser = argparse.ArgumentParser("GraXpert Deconvolution Object", parents=[parser], description="GraXpert, the astronomical deconvolution tool")
    deconv_obj_parser.add_argument(
        "-ai_version",
        "--ai_version",
        nargs="?",
        required=False,
        default=None,
        type=deconv_obj_version_type,
        help='Version of the Deconvolution Obj AI model, default: "latest"; available locally: [{}], available remotely: [{}]'.format(
            ", ".join(available_deconv_obj_versions[0]), ", ".join(available_deconv_obj_versions[1])
        ),
    )
    deconv_obj_parser.add_argument(
        "-strength",
        "--deconvolution_strength",
        nargs="?",
        required=False,
        default=None,
        type=float,
        help='Strength of the desired deconvolution effect, default: "0.5"',
    )
    deconv_obj_parser.add_argument(
        "-psfsize",
        "--deconvolution_psfsize",
        nargs="?",
        required=False,
        default=None,
        type=float,
        help='Size of the seeing you want to deconvolve, default: "0.3"',
    )
    deconv_obj_parser.add_argument(
        "-batch_size",
        "--ai_batch_size",
        nargs="?",
        required=False,
        default=None,
        type=int,
        help='Number of image tiles which Graxpert will denoise in parallel. Be careful: increasing this value might result in out-of-memory errors. Valid Range: 1..32, default: "4"',
    )

    deconv_stellar_parser = argparse.ArgumentParser("GraXpert Deconvolution Stellar", parents=[parser], description="GraXpert, the astronomical denoising tool")
    deconv_stellar_parser.add_argument(
        "-ai_version",
        "--ai_version",
        nargs="?",
        required=False,
        default=None,
        type=deconv_stellar_version_type,
        help='Version of the Deconvolution Stellar AI model, default: "latest"; available locally: [{}], available remotely: [{}]'.format(
            ", ".join(available_deconv_stellar_versions[0]), ", ".join(available_deconv_stellar_versions[1])
        ),
    )
    deconv_stellar_parser.add_argument(
        "-strength",
        "--deconvolution_strength",
        nargs="?",
        required=False,
        default=None,
        type=float,
        help='Strength of the desired deconvolution effect, default: "0.5"',
    )
    deconv_stellar_parser.add_argument(
        "-psfsize",
        "--deconvolution_psfsize",
        nargs="?",
        required=False,
        default=None,
        type=float,
        help='Size of the seeing you want to deconvolve, default: "0.3"',
    )
    deconv_stellar_parser.add_argument(
        "-batch_size",
        "--ai_batch_size",
        nargs="?",
        required=False,
        default=None,
        type=int,
        help='Number of image tiles which Graxpert will denoise in parallel. Be careful: increasing this value might result in out-of-memory errors. Valid Range: 1..32, default: "4"',
    )

    if "-h" in sys.argv or "--help" in sys.argv:
        if "background-extraction" in sys.argv:
            bge_parser.print_help()
        elif "denoising" in sys.argv:
            denoise_parser.print_help()
        elif "deconv-obj" in sys.argv:
            deconv_obj_parser.print_help()
        elif "deconv-stellar" in sys.argv:
            deconv_stellar_parser.print_help()
        else:
            parser.print_help()
        sys.exit(0)

    args, extras = parser.parse_known_args()

    if args.command == "background-extraction":
        args = bge_parser.parse_args()
    elif args.command == "deconv-obj":
        args = deconv_obj_parser.parse_args()
    elif args.command == "deconv-stellar":
        args = deconv_stellar_parser.parse_args()
    elif args.command == "denoising":
        args = denoise_parser.parse_args()

    return args

def main():
    """Note: this is entered directly via the entry_point definition in setup.py or called from below"""

    multiprocessing.freeze_support()
    faulthandler.enable(sys.__stderr__)

    try:
        # listing available versions might be slow, so only do it if we have command line args
        if len(sys.argv) > 1:
            args = parse_args()
        else:
            # Dummy noarg defs
            args = types.SimpleNamespace(command=None, filename=None)

        # Note: we wait to setup logging until after parsing args, so that --help response doesn't get log framing
        configure_logging()

        if args.command == "background-extraction":
            from graxpert.cmdline_tools import BGECmdlineTool

            logging.info(f"Starting GraXpert CLI, Background-Extraction, version: {graxpert_version} release: {graxpert_release}")
            clt = BGECmdlineTool(args)
            clt.execute()
        elif args.command == "denoising":
            from graxpert.cmdline_tools import DenoiseCmdlineTool

            logging.info(f"Starting GraXpert CLI, Denoising, version: {graxpert_version} release: {graxpert_release}")
            clt = DenoiseCmdlineTool(args)
            clt.execute()
        elif args.command == "deconv-obj":
            from graxpert.cmdline_tools import DeconvObjCmdlineTool

            logging.info(f"Starting GraXpert CLI, Deconvolution Obj, version: {graxpert_version} release: {graxpert_release}")
            clt = DeconvObjCmdlineTool(args)
            clt.execute()
        elif args.command == "deconv-stellar":
            from graxpert.cmdline_tools import DeconvStellarCmdlineTool

            logging.info(f"Starting GraXpert CLI, Deconvolution Stellar, version: {graxpert_version} release: {graxpert_release}")
            clt = DeconvStellarCmdlineTool(args)
            clt.execute()
        else:
            logging.info(f"Starting GraXpert UI, version: {graxpert_version} release: {graxpert_release}")
            ui_main(args.filename)
    finally:
        temp_cleanup()
        logging.shutdown()        


if __name__ == "__main__":
    main()

