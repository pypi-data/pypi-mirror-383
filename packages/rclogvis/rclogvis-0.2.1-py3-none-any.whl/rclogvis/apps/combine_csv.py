#
#   2025 Fabian Jankowski
#   Combine CSV telemetry files.
#

import argparse

import pandas as pd


def parse_args():
    """
    Parse the commandline arguments.

    Returns
    -------
    args: populated namespace
        The commandline arguments.
    """

    parser = argparse.ArgumentParser(
        description="Combine telemetry CSV files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "files", type=str, nargs="+", help="Telemetry CSV files to combine."
    )

    args = parser.parse_args()

    return args


#
# MAIN
#


def main():
    # handle command line arguments
    args = parse_args()

    df_total = pd.concat([pd.read_csv(item) for item in args.files], ignore_index=True)

    df_total.to_csv("total.csv", index=False)


if __name__ == "__main__":
    main()
