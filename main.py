#!/usr/bin/env python3
"""Crosshair Overlay - Main entry point."""

import sys
import os

# Add the project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.application import main

if __name__ == "__main__":
    sys.exit(main())