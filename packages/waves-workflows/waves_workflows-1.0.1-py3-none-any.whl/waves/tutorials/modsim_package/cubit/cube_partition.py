"""Partition the simple cube geometry created by ``cube_geometry.py``."""

import argparse
import pathlib
import shutil
import sys

import cubit


def main(input_file: pathlib.Path, output_file: pathlib.Path) -> None:
    """Partition the simple cube geometry created by ``cube_geometry.py``.

    This script partitions a simple Cubit model with a single cube part.

    **Feature labels:**

    * ``top``: +Y surface
    * ``bottom``: -Y surface
    * ``left``: -X surface
    * ``right``: +X surface
    * ``front``: +Z surface
    * ``back``: -Z surface

    :param str input_file: The Cubit model file created by ``cube_geometry.py``. Will be stripped of the extension
        and ``.cub`` will be used.
    :param str output_file: The output file for the Cubit model. Will be stripped of the extension and ``.cub`` will be
        used.

    :returns: writes ``output_file``.cub
    """
    input_file = input_file.with_suffix(".cub")
    output_file = output_file.with_suffix(".cub")

    # Avoid modifying the contents or timestamp on the input file.
    # Required to get conditional re-builds with a build system such as GNU Make, CMake, or SCons
    if input_file != output_file:
        shutil.copyfile(input_file, output_file)

    cubit.init(["cubit", "-noecho", "-nojournal", "-nographics", "-batch"])
    cubit.cmd("new")
    cubit.cmd("reset")

    cubit.cmd(f"open '{output_file}'")

    cubit.cmd("nodeset 1 add surface 5")
    cubit.cmd("nodeset 1 name 'top'")
    cubit.cmd("sideset 1 add surface 5")
    cubit.cmd("sideset 1 name 'top'")

    cubit.cmd("nodeset 2 add surface 3")
    cubit.cmd("nodeset 2 name 'bottom'")
    cubit.cmd("sideset 2 add surface 3")
    cubit.cmd("sideset 2 name 'bottom'")

    cubit.cmd("nodeset 3 add surface 4")
    cubit.cmd("nodeset 3 name 'left'")
    cubit.cmd("sideset 3 add surface 4")
    cubit.cmd("sideset 3 name 'left'")

    cubit.cmd("nodeset 4 add surface 6")
    cubit.cmd("nodeset 4 name 'right'")
    cubit.cmd("sideset 4 add surface 6")
    cubit.cmd("sideset 4 name 'right'")

    cubit.cmd("nodeset 5 add surface 1")
    cubit.cmd("nodeset 5 name 'front'")
    cubit.cmd("sideset 5 add surface 1")
    cubit.cmd("sideset 5 name 'front'")

    cubit.cmd("nodeset 6 add surface 2")
    cubit.cmd("nodeset 6 name 'back'")
    cubit.cmd("sideset 6 add surface 2")
    cubit.cmd("sideset 6 name 'back'")

    cubit.cmd(f"save as '{output_file}' overwrite")


def get_parser() -> argparse.ArgumentParser:
    """Return the command-line interface parser."""
    script_name = pathlib.Path(__file__)
    # Set default parameter values
    default_input_file = script_name.with_suffix(".cub").name.replace("_partition", "_geometry")
    default_output_file = script_name.with_suffix(".cub").name

    prog = f"python {script_name.name} "
    cli_description = (
        "Partition the simple cube geometry created by ``cube_geometry.py`` "
        "and write an ``output_file``.cub Cubit model file."
    )
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=pathlib.Path,
        default=default_input_file,
        help=(
            "The Cubit model file created by ``cube_geometry.py``. "
            "Will be stripped of the extension and ``.cub`` will be used, e.g. ``input_file``.cub "
            "(default: %(default)s"
        ),
    )
    parser.add_argument(
        "--output-file",
        type=pathlib.Path,
        default=default_output_file,
        help=(
            "The output file for the Cubit model. "
            "Will be stripped of the extension and ``.cub`` will be used, e.g. ``output_file``.cub "
            "(default: %(default)s"
        ),
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    sys.exit(
        main(
            input_file=args.input_file,
            output_file=args.output_file,
        )
    )
