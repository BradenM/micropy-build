#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""micropy-build

Docker Entrypoint for
micropy-build Dockerfiles

Free for Whomever
Braden Mars

"""

import argparse
import os
import shutil
from pathlib import Path

# Micropython Firmware Repo Path
MICROPY_ROOT = Path("/micropython")
MICROPY_NAME = os.environ.get("INPUT_NAME", "micropython")


# Port Container is building for
PORT = os.environ.get("INPUT_PORT", "esp32")
PORT_ROOT = os.environ.get("INPUT_PORT_ROOT", (MICROPY_ROOT / "ports"))
PORT_PATH = PORT_ROOT / PORT


def copy_artifacts(dest, binary=MICROPY_NAME, **kwargs):
    """Find and copy build artifacts to path

    Args:
        dest (os.PathLike): Path to copy artifacts to.
        binary (str): Name of Firmware (unix executable).
    """
    print(f"\n-- Copying Artifacts to {dest} --\n")
    dest = Path(dest).absolute()
    dest.mkdir(exist_ok=True, parents=True)
    binaries = list(PORT_PATH.rglob("*.bin"))
    binaries.extend(list(PORT_PATH.rglob(binary)))
    print("[Found Artifacts]\n", "\n".join(str(p) for p in binaries), "\n")
    for f in binaries:
        f_dest = shutil.copy2(f, dest)
        print(f"[Copied] {f.name} ==> {f_dest}")
    print("Done!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Micropy-Build Docker Entrypoint.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(help="Command to execute.")

    cp_parser = subparsers.add_parser(
        "copy",
        help="Copy build Artifacts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    cp_parser.add_argument(
        '-d', '--dest', help="Path to copy artifacts to.",
        default="/artifacts", type=Path)
    cp_parser.add_argument(
        '-b', '--binary',
        help='Name of Binary Executable to Look for.',
        default=MICROPY_NAME)
    cp_parser.set_defaults(func=copy_artifacts)

    args = parser.parse_args()
    if not args.func:
        parser.print_help()
    else:
        args.func(**vars(args))
