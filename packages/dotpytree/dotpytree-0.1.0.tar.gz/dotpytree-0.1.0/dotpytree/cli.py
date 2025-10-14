import argparse
from pathlib import Path
from .core import OutlinePrinter


def main():
    parser = argparse.ArgumentParser(
        description="Print Python file/class/function tree."
    )
    parser.add_argument("target", help="Python file or folder to analyze")
    parser.add_argument("--no-emoji", action="store_true", help="Disable emoji output")
    parser.add_argument(
        "--show-args", action="store_true", help="Show function arguments"
    )
    args = parser.parse_args()

    printer = OutlinePrinter(show_args=args.show_args, use_emoji=not args.no_emoji)
    printer.print_outline(Path(args.target))


if __name__ == "__main__":
    main()
