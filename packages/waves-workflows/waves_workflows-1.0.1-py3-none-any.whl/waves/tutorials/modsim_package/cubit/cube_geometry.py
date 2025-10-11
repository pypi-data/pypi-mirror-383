"""Create a simple cube geometry."""

import argparse
import pathlib
import sys

import cubit


def main(output_file: pathlib.Path, width: float, height: float, depth: float) -> None:
    """Create a simple cube geometry.

    This script creates a simple Cubit model with a single cube part.

    :param str output_file: The output file for the Cubit model. Will be stripped of the extension and ``.cub`` will be
        used.
    :param float width: The cube width (X-axis)
    :param float height: The cube height (Y-axis)
    :param float depth: The cube depth (Z-axis)

    :returns: writes ``output_file``.cub
    """
    output_file = output_file.with_suffix(".cub")

    cubit.init(["cubit", "-noecho", "-nojournal", "-nographics", "-batch"])
    cubit.cmd("new")
    cubit.cmd("reset")

    cubit.cmd(f"brick x {width} y {height} z {depth}")
    cubit.cmd(f"move volume 1 x {width / 2} y {height / 2} z {depth / 2} include_merged")

    cubit.cmd(f"save as '{output_file}' overwrite")


def get_parser() -> argparse.ArgumentParser:
    """Return the command-line interface parser."""
    script_name = pathlib.Path(__file__)
    # Set default parameter values
    default_output_file = script_name.with_suffix(".cub").name
    default_width = 1.0
    default_height = 1.0
    default_depth = 1.0

    prog = f"python {script_name.name} "
    cli_description = "Create a simple cube geometry and write an ``output_file``.cub Cubit model file."
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
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
    parser.add_argument(
        "--width",
        type=float,
        default=default_width,
        help="The cube width (X-axis)",
    )
    parser.add_argument(
        "--height",
        type=float,
        default=default_height,
        help="The cube height (Y-axis)",
    )
    parser.add_argument(
        "--depth",
        type=float,
        default=default_depth,
        help="The cube depth (Z-axis)",
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    sys.exit(
        main(
            output_file=args.output_file,
            width=args.width,
            height=args.height,
            depth=args.depth,
        )
    )
