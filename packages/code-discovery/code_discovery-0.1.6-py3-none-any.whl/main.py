"""Main entry point for Code Discovery."""

import argparse
import sys
from pathlib import Path
from core.orchestrator import Orchestrator


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Code Discovery - Automatic API Discovery System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in current directory
  python -m src.main

  # Run on specific repository
  python -m src.main --repo-path /path/to/repo

  # Dry run (don't commit)
  python -m src.main --dry-run

  # Use custom config
  python -m src.main --config /path/to/config.yml
        """,
    )

    parser.add_argument(
        "--repo-path",
        type=str,
        help="Path to the repository to analyze (default: current directory)",
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (default: .codediscovery.yml)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run discovery without committing changes",
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Output path for OpenAPI spec (overrides config)",
    )

    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        help="Output format for OpenAPI spec (overrides config)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Code Discovery 0.1.6",
    )

    args = parser.parse_args()

    try:
        # Create orchestrator
        orchestrator = Orchestrator(
            repo_path=args.repo_path,
            config_path=args.config,
        )

        # Override config if CLI args provided
        if args.dry_run:
            orchestrator.config.config["api_discovery"]["vcs"]["auto_commit"] = False
            orchestrator.config.config["api_discovery"]["external_api"]["enabled"] = False

        if args.output:
            orchestrator.config.config["api_discovery"]["openapi"]["output_path"] = args.output

        if args.format:
            orchestrator.config.config["api_discovery"]["openapi"]["output_format"] = args.format

        # Run discovery
        success = orchestrator.run()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(130)

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

