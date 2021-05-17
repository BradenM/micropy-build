#!/usr/bin/env python3

"""micropy-build

Docker Entrypoint for
micropy-build Dockerfiles

Free for Whomever
Braden Mars

"""

import argparse
import os
import shutil
import subprocess as subproc
from pathlib import Path
from typing import Sequence

# Micropython Firmware Repo Path
MICROPY_ROOT = Path("/micropython")
MICROPY_NAME = os.environ.get("INPUT_NAME", "micropython")


# Port Container is building for
PORT = os.environ.get("INPUT_PORT", "esp32")
PORT_ROOT = os.environ.get("INPUT_PORT_ROOT", (MICROPY_ROOT / "ports"))
PORT_PATH = Path(PORT_ROOT) / PORT

# Board Settings
BOARD = os.environ.get("INPUT_BOARD", "GENERIC")

# Extra Modules
EXTRA_MODULES_PATH = Path("/pymodules")


def rglob_binaries(path: Path, glob: str, exclusions: Sequence[str]):
    files = path.rglob(glob)
    for f in files:
        if not any(set(f.parts) & set(exclusions)):
            yield f


def copy_artifacts(dest, binary=MICROPY_NAME, **kwargs):
    """Find and copy build artifacts to path

    Args:
        dest (os.PathLike): Path to copy artifacts to.
        binary (str): Name of Firmware (unix executable).
    """
    print("\n-- Copying Artifacts To %s --\n" % dest)
    print("[DEBUG] Search Path:", PORT_PATH)
    print("[DEBUG] Binary Name:", binary)
    dest = Path(dest).absolute()
    dest.mkdir(exist_ok=True, parents=True)
    exclusions = ('CMakeFiles', 'bootloader', 'partition_table', 'esp-idf',)
    binaries = list(rglob_binaries(PORT_PATH, "*.bin", exclusions))
    binaries.extend(list(rglob_binaries(PORT_PATH, binary, exclusions)))
    print("\n[Found Artifacts]\n", "\n".join(str(p) for p in binaries), "\n")
    for f in binaries:
        f_dest = shutil.copy2(f, dest)
        print("[Copied] %s ==> %s" % (f.name, str(f_dest)))
    print("Done!")


def load_extra_modules():
    for module_path in EXTRA_MODULES_PATH.iterdir():
        dest = PORT_PATH / "modules" / module_path.name
        shutil.rmtree(dest, ignore_errors=True)
        print(f"Copying: {module_path.name} => {dest}")
        if(module_path.is_dir()):
            shutil.copytree(str(module_path), str(dest))
        else:
            shutil.copy2(str(module_path), str(dest))
    print("Extra frozen modules copied!")


def exec_cmd(*args):
    print('Executing:', *args)
    proc = subproc.run(args)
    proc.check_returncode()


def build(do_copy=True, **kwargs):
    print("Building Port!")
    load_extra_modules()
    exec_cmd("make", "-j4", "-C", str(PORT_PATH),
             f"BOARD={BOARD}", "TARGET=app")
    print('Done!')
    if do_copy:
        copy_artifacts('/artifacts')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Micropy-Build Docker Entrypoint.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(help="Command to execute.")

    cp_parser = subparsers.add_parser(
        "copy",
        help="Copy build Artifacts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cp_parser.add_argument(
        "-d", "--dest", help="Path to copy artifacts to.", default="/artifacts"
    )
    cp_parser.add_argument(
        "-b",
        "--binary",
        help="Name of Binary Executable to Look for.",
        default=MICROPY_NAME,
    )
    cp_parser.set_defaults(func=copy_artifacts)

    build_parser = subparsers.add_parser(
        "build", help="Rebuild a port.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    build_parser.add_argument('-c', '--copy', help="Perform Copy after building.", default=True)
    build_parser.set_defaults(func=build)

    args = parser.parse_args()
    if not args.func:
        parser.print_help()
    else:
        args.func(**vars(args))
