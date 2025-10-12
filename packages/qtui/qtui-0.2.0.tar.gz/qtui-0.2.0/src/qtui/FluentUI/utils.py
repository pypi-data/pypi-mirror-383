import importlib.resources
import subprocess
import sys

import PySide6 as RefMod

__all__ = ["qt_tool_wrapper", "rcc"]


def qt_tool_wrapper(qt_tool: str, args: list[str], libexec: bool = False):
    # listed as an entrypoint in setup.py
    lib_dir = importlib.resources.files(RefMod)
    if libexec and sys.platform != "win32":
        exe = lib_dir / "Qt" / "libexec" / qt_tool
    else:
        exe = lib_dir / qt_tool

    cmd = [str(exe)] + args
    returncode = subprocess.call(cmd)
    if returncode != 0:
        command = " ".join(cmd)
        print(f"'{command}' returned {returncode}", file=sys.stderr)


def rcc(args: list[str]):
    if "--binary" not in args:
        args.extend(["-g", "python"])
    qt_tool_wrapper("rcc", args, True)
