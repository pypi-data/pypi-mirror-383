"""CLI for AgentBuilder package."""

import argparse
from . import hello

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="AgentBuilder")
    parser.add_argument("--version", action="version", version="0.1.0")
    
    args = parser.parse_args()
    
    # Print hello message
    hello()

if __name__ == "__main__":
    main()