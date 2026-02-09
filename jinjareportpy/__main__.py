"""Entry point for running jinjareportpy as a module.

Usage:
    python -m jinjareportpy                     # Show help
    python -m jinjareportpy --help              # Show help
    python -m jinjareportpy config show         # Show configuration
    python -m jinjareportpy demo                # Generate demo report
    python -m jinjareportpy demo --format corporate  # Demo with corporate format
    python -m jinjareportpy formats             # List available formats
    python -m jinjareportpy invoice -n INV-001  # Create an invoice
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
