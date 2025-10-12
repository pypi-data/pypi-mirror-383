# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CLI for managing connector builder evaluations.

Usage:
    poe evals run                                      # Run all evaluations
    poe evals run --connector source-jsonplaceholder   # Run for specific connector
    poe evals run --connector source-starwars --connector source-rickandmorty  # Run for multiple connectors
    poe evals run --dataset-prefix weekly-evals        # Use custom dataset prefix
    poe evals report <exp_id>                          # Generate report for a specific experiment

Requirements:
    - OpenAI API key (OPENAI_API_KEY in a local '.env')
    - Phoenix API key (PHOENIX_API_KEY in a local '.env')
    - Phoenix collector endpoint (PHOENIX_COLLECTOR_ENDPOINT in a local '.env')
"""

import argparse
import asyncio
import logging

from dotenv import load_dotenv
from phoenix.client import Client

from .phoenix_run import main as run_evals_main
from .summary import generate_markdown_summary


load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_command(args: argparse.Namespace) -> None:
    """Run evaluations."""
    connectors = args.connectors
    dataset_prefix = args.dataset_prefix
    if connectors:
        logger.info(f"Running evaluations for connectors: {', '.join(connectors)}")
    else:
        logger.info("Running evaluations...")
    logger.info(f"Using dataset prefix: {dataset_prefix}")
    asyncio.run(run_evals_main(connectors=connectors, dataset_prefix=dataset_prefix))


def report_command(args: argparse.Namespace) -> None:
    """Generate report for a specific experiment."""
    experiment_id = args.experiment_id
    logger.info(f"Generating report for experiment: {experiment_id}")

    try:
        # Fetch the experiment
        client = Client()
        experiment = client.experiments.get_experiment(experiment_id=experiment_id)
        logger.info(f"Successfully fetched experiment: {experiment_id}")

        # Generate markdown summary
        summary_path = generate_markdown_summary(experiment, experiment_id)

        if summary_path:
            logger.info(f"✓ Report generated successfully at: {summary_path}")
        else:
            logger.error("Failed to generate report")

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manage connector builder evaluations",
        prog="evals",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Run subcommand
    run_parser = subparsers.add_parser(
        "run",
        help="Run all evaluations",
    )
    run_parser.add_argument(
        "--connector",
        dest="connectors",
        action="append",
        help="Filter by connector name (can be specified multiple times)",
    )
    run_parser.add_argument(
        "--dataset-prefix",
        dest="dataset_prefix",
        default="builder-connectors",
        help="Prefix for the Phoenix dataset name (default: builder-connectors)",
    )
    run_parser.set_defaults(func=run_command)

    # Report subcommand
    report_parser = subparsers.add_parser(
        "report",
        help="Generate report for a specific experiment",
    )
    report_parser.add_argument(
        "experiment_id",
        help="Experiment ID to generate report for",
    )
    report_parser.set_defaults(func=report_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
