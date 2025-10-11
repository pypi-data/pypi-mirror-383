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
        "generate-simulation-data", help="Generate simulated data."
    ).set_defaults(func=generate_data)

    subparsers.add_parser(
        "beast-run-simulations", help="Run BEAST2 on simulated data."
    ).set_defaults(func=run_beast)

    subparsers.add_parser(
        "summarize-simulation-logs", help="Summarize BEAST2 logs for simulations data."
    ).set_defaults(func=summarize_logs)

    subparsers.add_parser(
        "generate-simulation-figures", help="Generate figures for simulations data."
    ).set_defaults(func=generate_figures)

    args = parser.parse_args()
    args.func()
