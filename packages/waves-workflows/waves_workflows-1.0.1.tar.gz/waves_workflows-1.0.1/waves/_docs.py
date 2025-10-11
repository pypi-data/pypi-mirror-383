"""Internal API module implementing the ``docs`` subcommand behavior.

Should raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow the CLI implementation
to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""

import argparse
import pathlib
import sys

_exclude_from_namespace = set(globals().keys())


def get_parser() -> argparse.ArgumentParser:
    """Return a 'no-help' parser for the docs subcommand.

    :return: parser
    """
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "-p",
        "--print-local-path",
        action="store_true",
        help=(
            "Print the path to the locally installed documentation index file. "
            "As an alternative to the docs sub-command, open index.html in a web browser "
            "(default: %(default)s)"
        ),
    )

    return parser


def main(documentation_index: pathlib.Path, print_local_path: bool = False) -> None:
    """Open the package HTML documentation in the system default web browser or print documentation index path.

    :param print_local_path: Flag to print the local path to terminal instead of calling the default web browser

    :raises RuntimeError: if the installed documentation path is not found
    :raises RuntimeError: if a web browser fails to open
    """
    if print_local_path:
        if documentation_index.exists():
            print(documentation_index, file=sys.stdout)
        else:
            # This should only be reached if the package installation structure doesn't match the assumptions in
            # _settings.py. It is used by the Conda build tests as a sign-of-life that the assumptions are correct.
            raise RuntimeError("Could not find package documentation HTML index file")
    else:
        import webbrowser

        success = webbrowser.open(str(documentation_index))
        if not success:
            raise RuntimeError(
                "Could not open a web browser. Is your system default browser set? Are you working over SSH? "
                "Try running ``waves docs --print-local-path`` and opening the reported path directly."
            )


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
