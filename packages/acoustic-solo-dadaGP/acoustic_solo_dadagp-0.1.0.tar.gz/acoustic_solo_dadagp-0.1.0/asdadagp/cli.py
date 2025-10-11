#!/usr/bin/env python3
"""
Command-line interface for acoustic-solo-dadaGP package.

This CLI provides tools for processing Guitar Pro files, converting them to tokens,
and back to Guitar Pro format, specifically designed for acoustic solo guitar music.
"""

import argparse
import sys
from pathlib import Path

from .decoder import asdadagp_decode
from .encoder import asdadagp_encode
from .processor import get_string_tunings, tracks_check


def validate_file_path(file_path: str, must_exist: bool = True) -> str:
    """Validate and return absolute file path."""
    path = Path(file_path).resolve()

    if must_exist and not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return str(path)


def encode_command(args):
    """Encode a Guitar Pro file to tokens."""
    try:
        input_file = validate_file_path(args.input_file)
        output_file = args.output_file

        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Encoding {input_file} to {output_file}")
        print(f"Artist token: {args.artist}")

        asdadagp_encode(input_file, output_file, args.tuning, args.artist)

        print(f"Successfully encoded to {output_file}")

    except Exception as e:
        print(f"Error during encoding: {e}", file=sys.stderr)
        sys.exit(1)


def decode_command(args):
    """Decode tokens back to a Guitar Pro file."""
    try:
        input_file = validate_file_path(args.input_file)
        output_file = args.output_file

        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Decoding {input_file} to {output_file}")

        asdadagp_decode(input_file, output_file)

        print(f"Successfully decoded to {output_file}")

    except Exception as e:
        print(f"Error during decoding: {e}", file=sys.stderr)
        sys.exit(1)


def process_command(args):
    """Process tokens with various options."""
    try:
        input_file = validate_file_path(args.input_file)

        # Read tokens from file
        with open(input_file, "r") as f:
            tokens = f.read().split("\n")

        print(f"Processing tokens from {input_file}")

        tunings = get_string_tunings(tokens)

        processed_tokens = tracks_check(tokens, args.merge_tracks)

        if args.measures:
            from .processor import measures_playing_order, tokens_to_measures

            # Convert tokens to TokenMeasure objects with repeat analysis
            token_measures = tokens_to_measures(processed_tokens)
            measures = []
            for tm in token_measures:
                measures.append(tm.tokens)

            # Get the actual playing order considering repeats and alternatives
            playing_order = measures_playing_order(token_measures)

            # Create output structure
            output_data = {
                "tokens": {i: token for i, token in enumerate(processed_tokens)},
                # "measure_order": measure_order,
                "measures": measures,
                "playing_order": playing_order,
                "tuning": tunings,
            }
        else:

            output_data = processed_tokens

        # Output results
        # if args.output_file:
        output_file = args.output_file
        if not output_file.endswith(".json") and args.measures:
            raise ValueError(
                "Output file must be a .json file when using --measures option"
            )
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            if isinstance(output_data, dict):
                import json

                json.dump(output_data, f, indent=2)
            else:
                f.write("\n".join(output_data))

        print(f"Processed tokens saved to {output_file}")

    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)


def info_command(args):
    """Display information about a Guitar Pro file or token file."""
    try:
        input_file = validate_file_path(args.input_file)

        if input_file.endswith((".gp3", ".gp4", ".gp5", ".gpx")):
            # Guitar Pro file
            import guitarpro as gp

            song = gp.parse(input_file)

            print(f"Guitar Pro File: {input_file}")
            print(f"Title: {song.title}")
            print(f"Artist: {song.artist}")
            print(f"Album: {song.album}")
            print(f"Tracks: {len(song.tracks)}")
            print(f"Measures: {len(song.measureHeaders)}")
            print(f"Tempo: {song.tempo} BPM")

            print("\nTracks:")
            for i, track in enumerate(song.tracks):
                track_type = "Percussion" if track.isPercussionTrack else "Guitar"
                print(f"  {i+1}. {track.name} ({track_type})")
                if hasattr(track, "strings") and track.strings:
                    tunings = [str(string.value) for string in track.strings]
                    print(f"     Tuning: {', '.join(tunings)}")

        else:
            # Token file
            with open(input_file, "r") as f:
                tokens = f.read().split("\n")

            print(f"Token File: {input_file}")
            print(f"Total tokens: {len(tokens)}")

            if tokens:
                print(f"Artist: {tokens[0] if tokens[0] else 'Unknown'}")

                # Count token types
                token_types = {}
                for token in tokens:
                    if ":" in token:
                        token_type = token.split(":")[0]
                        token_types[token_type] = token_types.get(token_type, 0) + 1

                print("\nToken types:")
                for token_type, count in sorted(token_types.items()):
                    print(f"  {token_type}: {count}")

    except Exception as e:
        print(f"Error getting file info: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="acoustic-solo-dadaGP - Process Guitar Pro files for acoustic solo guitar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode a Guitar Pro file to tokens
  asdadagp encode input.gp5 output.txt --artist "John Doe"
  
  # Decode tokens back to Guitar Pro
  asdadagp decode input.txt output.gp5
  
  # Process tokens with track merging
  asdadagp process input.txt --merge-tracks --output processed.txt
  
  # Split tokens into measures
  asdadagp split-measures input.txt output.json
  
  # Get information about a file
  asdadagp info input.gp5
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Encode command
    encode_parser = subparsers.add_parser(
        "encode", help="Encode Guitar Pro file to tokens"
    )
    encode_parser.add_argument(
        "input_file", help="Input Guitar Pro file (.gp3, .gp4, .gp5, .gpx)"
    )
    encode_parser.add_argument("output_file", help="Output token file")
    encode_parser.add_argument(
        "--artist",
        required=False,
        default="Unknown",
        help="Artist name for the token file",
    )
    encode_parser.add_argument(
        "--tuning",
        default=False,
        action="store_true",
        help="Append tuning to note tokens, otherwise tunings are in the header only",
    )
    encode_parser.set_defaults(func=encode_command)

    # Decode command
    decode_parser = subparsers.add_parser(
        "decode", help="Decode tokens to Guitar Pro file"
    )
    decode_parser.add_argument("input_file", help="Input token file")
    decode_parser.add_argument("output_file", help="Output Guitar Pro file")
    decode_parser.set_defaults(func=decode_command)

    # Process command
    process_parser = subparsers.add_parser(
        "process", help="Process tokens with various options"
    )
    process_parser.add_argument("input_file", help="Input tokens txt file")
    process_parser.add_argument("output_file", help="Output json/txt file")
    # process_parser.add_argument(
    #     "--output-file", "-o", help="Output file (default: stdout)"
    # )
    process_parser.add_argument(
        "--merge-tracks",
        action="store_true",
        default=False,
        help="Merge all tracks into one, otherwise keep only the first track and discard additional tracks",
    )
    process_parser.add_argument(
        "--measures",
        action="store_true",
        default=False,
        help="Spit tokens into measures and output the measures playing order according to repeats",
    )

    process_parser.set_defaults(func=process_command)

    # Info command
    info_parser = subparsers.add_parser("info", help="Display information about a file")
    info_parser.add_argument("input_file", help="Input file (Guitar Pro or token file)")
    info_parser.set_defaults(func=info_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
