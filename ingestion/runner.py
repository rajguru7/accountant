"""
Ingestion Runner - Main execution controller for SFIS data ingestion
Processes financial data files using configured drivers
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from ingestion.config_loader import ConfigLoader
from ingestion.drivers.csv_importer import GenericCSVImporter


class IngestionRunner:
    """
    Main controller for running data ingestion across multiple sources
    """

    def __init__(self, config_dir: str, data_dir: str, output_dir: str):
        """
        Initialize the ingestion runner

        Args:
            config_dir: Directory containing YAML configuration files
            data_dir: Directory containing source data files
            output_dir: Directory to write Beancount output files
        """
        self.config_dir = config_dir
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.config_loader = ConfigLoader()

    def run_all(self) -> None:
        """
        Run ingestion for all configured sources
        """
        print(f"Loading configurations from: {self.config_dir}")
        configs = self.config_loader.load_all_from_directory(self.config_dir)

        print(f"Found {len(configs)} configuration(s)")

        for config in configs:
            self.run_single(config)

    def run_single(self, config: dict[str, Any]) -> None:
        """
        Run ingestion for a single source configuration

        Args:
            config: Configuration dictionary for the source
        """
        institution = config.get("institution", "Unknown")
        driver_type = config.get("driver")

        print(f"\nProcessing: {institution}")
        print(f"Driver: {driver_type}")

        # Validate configuration
        if not self.config_loader.validate(config):
            print(f"  ERROR: Invalid configuration for {institution}")
            return

        # Find matching files
        file_pattern = config["file_pattern"]
        matching_files = self._find_matching_files(file_pattern)

        if not matching_files:
            print(f"  No files found matching pattern: {file_pattern}")
            return

        print(f"  Found {len(matching_files)} file(s)")

        # Process based on driver type
        if driver_type == "csv":
            self._process_csv(config, matching_files)
        elif driver_type == "pdf":
            print("  WARNING: PDF driver not yet implemented")
        elif driver_type == "api":
            print("  WARNING: API driver not yet implemented")
        else:
            print(f"  ERROR: Unknown driver type: {driver_type}")

    def _find_matching_files(self, pattern: str) -> list[Path]:
        """
        Find files matching the given pattern in the data directory

        Args:
            pattern: Glob pattern for matching files

        Returns:
            List of matching file paths
        """
        data_path = Path(self.data_dir)
        return list(data_path.glob(pattern))

    def _process_csv(self, config: dict[str, Any], files: list[Path]) -> None:
        """
        Process CSV files using GenericCSVImporter

        Args:
            config: Configuration for the CSV importer
            files: List of CSV files to process
        """
        importer = GenericCSVImporter(config)

        all_transactions = []
        for file_path in files:
            print(f"  Processing: {file_path.name}")
            try:
                transactions = importer.parse(str(file_path))
                all_transactions.extend(transactions)
                print(f"    Imported {len(transactions)} transaction(s)")
            except Exception as e:
                print(f"    ERROR: {e}")

        if all_transactions:
            self._write_output(config, all_transactions, importer)

    def _write_output(
        self,
        config: dict[str, Any],
        transactions: list[dict[str, Any]],
        importer: GenericCSVImporter,
    ) -> None:
        """
        Write transactions to Beancount output file

        Args:
            config: Source configuration
            transactions: List of parsed transactions
            importer: Importer instance for conversion
        """
        institution = config["institution"].replace(" ", "_").lower()
        output_file = Path(self.output_dir) / f"{institution}_import.bean"

        # Convert to Beancount format
        beancount_entries = importer.to_beancount(transactions)

        # Write to file
        os.makedirs(self.output_dir, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"; Imported transactions from {config['institution']}\n")
            f.write(f"; Total transactions: {len(transactions)}\n\n")
            for entry in beancount_entries:
                f.write(entry)
                f.write("\n\n")

        print(f"  Output written to: {output_file}")
        print(f"  Total: {len(transactions)} transaction(s)")


def main():
    """Main entry point for the ingestion runner"""
    parser = argparse.ArgumentParser(description="SFIS Ingestion Runner - Import financial data")
    parser.add_argument(
        "--config-dir",
        default="ingestion/config",
        help="Directory containing YAML configuration files",
    )
    parser.add_argument(
        "--data-dir", default="data", help="Directory containing source data files to import"
    )
    parser.add_argument(
        "--output-dir", default="ledger/includes", help="Directory to write Beancount output files"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("SFIS Ingestion Runner")
    print("=" * 70)

    runner = IngestionRunner(
        config_dir=args.config_dir, data_dir=args.data_dir, output_dir=args.output_dir
    )

    try:
        runner.run_all()
        print("\n" + "=" * 70)
        print("Ingestion complete!")
        print("=" * 70)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
