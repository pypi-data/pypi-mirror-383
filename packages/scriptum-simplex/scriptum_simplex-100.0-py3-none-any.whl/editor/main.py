#!/usr/bin/env python3
"""
Main entry point for the Scriptum Simplex application.
"""

import sys
import os

# No path manipulation needed - we're already in the correct directory structure

from .controller import Controller


def main():
    """Main function to start the Scriptum Simplex application."""
    try:
        # Create and run the application
        app = Controller()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
