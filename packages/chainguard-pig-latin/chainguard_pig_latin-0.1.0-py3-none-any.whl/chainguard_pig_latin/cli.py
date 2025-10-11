"""
Command-line interface for Chainguard Pig Latin.
"""

import sys
import argparse
from .converter import to_pig_latin


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Convert text to Pig Latin",
        prog="pig-latin"
    )

    parser.add_argument(
        "text",
        nargs="*",
        help="Text to convert to Pig Latin. If not provided, reads from stdin."
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    args = parser.parse_args()

    if args.text:
        # Convert text from arguments
        text = " ".join(args.text)
        print(to_pig_latin(text))
    else:
        # Read from stdin
        try:
            for line in sys.stdin:
                print(to_pig_latin(line.rstrip('\n')))
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == "__main__":
    main()
