#!/usr/bin/env python3
"""
Simple deployment entry point.

This is a convenience script that provides easy access to the deployment system.
You can either use this script directly or use the full deploy/deploy_script.py
with more advanced options.

Examples:
    python deploy.py                           # Deploy to development
    python deploy.py staging                   # Deploy to staging
    python deploy.py production --dry-run      # Dry run for production
    python deploy.py staging --assets ./assets # Deploy with assets
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Main entry point that delegates to the full deployment script."""

    # Path to the main deployment script
    script_path = Path(__file__).parent / "deploy" / "deploy_script.py"

    # If no arguments provided, default to development with current build
    if len(sys.argv) == 1:
        args = ["--env", "development", "--source", "./build"]
    else:
        args = sys.argv[1:]

        # If first argument is an environment name without --env flag, add it
        if args[0] in ["development", "staging", "production"] and "--env" not in args:
            args = ["--env"] + args

    # Build the command
    cmd = [sys.executable, str(script_path)] + args

    print(f"🚀 Running: {' '.join(cmd)}")

    # Execute the deployment script
    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n❌ Deployment cancelled")
        sys.exit(1)


if __name__ == "__main__":
    main()
