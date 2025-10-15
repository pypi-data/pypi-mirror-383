#!/usr/bin/env python3
"""
Command-line interface for astroSR.
"""

import argparse
import sys

from . import __version__


def main():
    """Main entry point for the astrosr CLI."""
    parser = argparse.ArgumentParser(
        prog="astrosr",
        description="Astronomical super-resolution with drizzle for wide FOV images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"astrosr {__version__}",
    )

    parser.add_argument(
        "input_files",
        nargs="*",
        help="Input FITS files to process",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output filename (default: drizzled_result.fits)",
        default="drizzled_result.fits",
    )

    parser.add_argument(
        "-p",
        "--pixfrac",
        type=float,
        help="Pixel fraction for drizzling (default: 0.8)",
        default=0.8,
    )

    parser.add_argument(
        "-s",
        "--scale",
        type=float,
        help="Output pixel scale factor (default: 0.5)",
        default=0.5,
    )

    args = parser.parse_args()

    if not args.input_files:
        parser.print_help()
        sys.exit(1)

    # Import here to avoid slow imports when just showing help
    from .drizzle_super_resolution import DrizzleSuperResolution

    try:
        # Initialize the drizzle processor
        drizzler = DrizzleSuperResolution()

        # Process the files
        print(f"Processing {len(args.input_files)} files...")
        drizzler.process_images(
            args.input_files,
            output_filename=args.output,
            pixfrac=args.pixfrac,
            scale=args.scale,
        )

        print(f"Successfully created: {args.output}")
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
