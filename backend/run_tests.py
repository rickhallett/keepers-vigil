#!/usr/bin/env python3
"""
Convenience script to run the agentic testing framework.

Usage:
    python run_tests.py                          # Run all personas
    python run_tests.py --personas explorer      # Run specific persona
    python run_tests.py --strategy rules         # Use rule-based strategy (no LLM for decisions)
    python run_tests.py --analyze-only           # Only analyze existing sessions
    python run_tests.py --list-personas          # List available personas
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from testing.runner import main

if __name__ == "__main__":
    sys.exit(main())
