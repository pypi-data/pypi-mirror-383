"""Python 2/3 compatible argparse types for input verification."""

import argparse


def positive_float(argument):
    """Type function for argparse - positive floats.

    Abaqus Python 2 and Python 3 compatible argparse type method:
    https://docs.python.org/3.12/library/argparse.html#type.

    :param str argument: string argument from argparse

    :returns: argument
    :rtype: float

    :raises ValueError:

        * The argument can't be cast to float
        * The argument is less than 0.0 in a float comparison
    """
    minimum_value = 0.0
    try:
        argument = float(argument)
    except ValueError as err:
        raise argparse.ArgumentTypeError(f"invalid float value: '{argument}'") from err
    if not argument > minimum_value:
        raise argparse.ArgumentTypeError(f"invalid positive float: '{argument}'")
    return argument
