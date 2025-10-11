import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from bella_companion.simulations import (
    generate_data,
    generate_figures,
    run_beast,
    summarize_logs,
)


def main():
    load_dotenv(Path(os.getcwd()) / ".env")

    parser = argparse.ArgumentParser(
        prog="bella",
        description="Companion tool with experiments and evaluation for Bayesian Evolutionary Layered Learning Architectures (BELLA) BEAST2 package.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "sim-data", help="Generate synthetic simulation datasets."
    ).set_defaults(func=generate_data)

    subparsers.add_parser(
        "sim-run", help="Run BEAST2 analyses on simulation datasets."
    ).set_defaults(func=run_beast)

    subparsers.add_parser(
        "sim-summary", help="Summarize BEAST2 log outputs for simulations."
    ).set_defaults(func=summarize_logs)

    subparsers.add_parser(
        "sim-figures", help="Generate plots and figures from simulation results."
    ).set_defaults(func=generate_figures)

    args = parser.parse_args()
    args.func()
