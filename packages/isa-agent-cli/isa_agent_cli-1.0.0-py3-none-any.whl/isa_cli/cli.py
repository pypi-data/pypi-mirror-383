#!/usr/bin/env python3
"""
Entry point for isA Agent CLI command
"""

import asyncio
from .main import main

def cli():
    """Main CLI entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        exit(0)

if __name__ == "__main__":
    cli()