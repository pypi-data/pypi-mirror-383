"""Command-line interface for path-link.

Provides three commands:
1. print - Print resolved paths as JSON
2. validate - Run validators and report results
3. gen-static - Generate static dataclass file
"""

import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

from path_link import ProjectPaths, write_dataclass_file, validate_or_raise
from path_link.builtin_validators import StrictPathValidator
from path_link.validation import PathValidationError
from path_link.url_factory import ProjectUrls
from path_link.url_model import ValidationMode
from path_link.url_static import write_url_dataclass_file


def cmd_print(args: argparse.Namespace) -> int:
    """Print resolved paths as JSON."""
    try:
        if args.source == "pyproject":
            paths = ProjectPaths.from_pyproject()
        elif args.source == "config":
            # Default to .paths file in current directory
            config_file = args.config if args.config else ".paths"
            paths = ProjectPaths.from_config(config_file)
        else:
            print(f"Unknown source: {args.source}", file=sys.stderr)
            return 1

        # Convert paths to dict and serialize Path objects as strings
        paths_dict = paths.to_dict()
        serializable = {k: str(v) for k, v in paths_dict.items()}

        print(json.dumps(serializable, indent=2))
        return 0

    except Exception as e:
        print(f"Error loading paths: {e}", file=sys.stderr)
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Run validators and report results."""
    try:
        # Load paths
        if args.source == "pyproject":
            paths = ProjectPaths.from_pyproject()
        elif args.source == "config":
            config_file = args.config if args.config else ".paths"
            paths = ProjectPaths.from_config(config_file)
        else:
            print(f"Unknown source: {args.source}", file=sys.stderr)
            return 1

        # Run validation
        if args.strict:
            # Strict mode: require common paths exist
            validator = StrictPathValidator(
                required=["base_dir"], must_be_dir=["base_dir"], allow_symlinks=False
            )

            if args.raise_on_error:
                # Raise exception on validation failure
                validate_or_raise(paths, validator)
                print("✅ All paths valid (strict mode)")
                return 0
            else:
                # Just print results
                result = validator.validate(paths)
                if result.ok():
                    print("✅ All paths valid (strict mode)")
                    return 0
                else:
                    print("❌ Validation failed:", file=sys.stderr)
                    for error in result.errors():
                        print(
                            f"  ERROR [{error.code}] {error.field}: {error.message}",
                            file=sys.stderr,
                        )
                    for warning in result.warnings():
                        print(
                            f"  WARN [{warning.code}] {warning.field}: {warning.message}",
                            file=sys.stderr,
                        )
                    return 1
        else:
            # Basic mode: just check that paths can be loaded
            print("✅ Paths loaded successfully")
            paths_dict = paths.to_dict()
            print(f"   Loaded {len(paths_dict)} paths")
            return 0

    except PathValidationError as e:
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_gen_static(args: argparse.Namespace) -> int:
    """Generate static dataclass file."""
    try:
        # Determine output path
        if args.out:
            output_path = Path(args.out)
        else:
            # Default to src/project_paths/project_paths_static.py
            output_path = None  # write_dataclass_file uses default

        # Generate static model
        if output_path:
            print(f"Generating static model at: {output_path}")
        else:
            print("Generating static model at default location")

        write_dataclass_file(output_path=output_path)
        print("✅ Static model generated successfully")
        return 0

    except Exception as e:
        print(f"Error generating static model: {e}", file=sys.stderr)
        return 1


def cmd_print_urls(args: argparse.Namespace) -> int:
    """Print resolved URLs as JSON."""
    try:
        # Determine validation mode
        mode = ValidationMode(args.mode.lower()) if hasattr(args, "mode") and args.mode else ValidationMode.LENIENT

        # Load URLs based on source
        if args.src == "pyproject":
            urls = ProjectUrls.from_pyproject(mode=mode)
        elif args.src == "dotenv":
            config_file = args.config if hasattr(args, "config") and args.config else ".urls"
            urls = ProjectUrls.from_config(config_file, mode=mode)
        elif args.src == "all":
            urls = ProjectUrls.from_merged(mode=mode)
        else:
            print(f"Unknown source: {args.src}", file=sys.stderr)
            return 1

        # Convert URLs to dict
        urls_dict = urls.to_dict()

        # Output based on format
        if args.format == "json":
            print(json.dumps(urls_dict, indent=2))
        else:  # table format
            print(f"URLs (mode: {mode.value}, source: {args.src}):")
            for key, value in sorted(urls_dict.items()):
                print(f"  {key}: {value}")

        return 0

    except Exception as e:
        print(f"Error loading URLs: {e}", file=sys.stderr)
        return 1


def cmd_validate_urls(args: argparse.Namespace) -> int:
    """Validate URLs and report results."""
    try:
        # Determine validation mode
        mode = ValidationMode(args.mode.lower()) if hasattr(args, "mode") and args.mode else ValidationMode.LENIENT

        # Load URLs based on source
        if args.src == "pyproject":
            urls = ProjectUrls.from_pyproject(mode=mode)
        elif args.src == "dotenv":
            config_file = args.config if hasattr(args, "config") and args.config else ".urls"
            urls = ProjectUrls.from_config(config_file, mode=mode)
        elif args.src == "all":
            urls = ProjectUrls.from_merged(mode=mode)
        else:
            print(f"Unknown source: {args.src}", file=sys.stderr)
            return 1

        # If we got here, all URLs are valid
        urls_dict = urls.to_dict()
        print(f"✅ All {len(urls_dict)} URLs valid (mode: {mode.value})")
        return 0

    except Exception as e:
        print(f"❌ URL validation failed: {e}", file=sys.stderr)
        return 1


def cmd_gen_static_urls(args: argparse.Namespace) -> int:
    """Generate static URL dataclass file."""
    try:
        # Determine validation mode
        mode = ValidationMode(args.mode.lower()) if hasattr(args, "mode") and args.mode else ValidationMode.LENIENT

        # Determine output path
        output_path = Path(args.output) if hasattr(args, "output") and args.output else None

        # Generate static model
        if output_path:
            print(f"Generating static URL model at: {output_path} (mode: {mode.value})")
        else:
            print(f"Generating static URL model at default location (mode: {mode.value})")

        write_url_dataclass_file(output_path=output_path, mode=mode)
        return 0

    except Exception as e:
        print(f"Error generating static URL model: {e}", file=sys.stderr)
        return 1


def main() -> NoReturn:
    """Main entry point for ptool CLI."""
    parser = argparse.ArgumentParser(
        prog="pathlink", description="Type-safe project path management tool"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # print command
    print_parser = subparsers.add_parser("print", help="Print resolved paths as JSON")
    print_parser.add_argument(
        "--source",
        choices=["config", "pyproject"],
        default="pyproject",
        help="Path configuration source (default: pyproject)",
    )
    print_parser.add_argument(
        "--config", type=str, help="Path to .paths config file (default: .paths)"
    )

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Run validators and report results"
    )
    validate_parser.add_argument(
        "--source",
        choices=["config", "pyproject"],
        default="pyproject",
        help="Path configuration source (default: pyproject)",
    )
    validate_parser.add_argument(
        "--config", type=str, help="Path to .paths config file (default: .paths)"
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation (check paths exist, no symlinks)",
    )
    validate_parser.add_argument(
        "--raise",
        dest="raise_on_error",
        action="store_true",
        help="Raise exception on validation failure",
    )

    # gen-static command
    gen_static_parser = subparsers.add_parser(
        "gen-static", help="Generate static dataclass file for IDE autocomplete"
    )
    gen_static_parser.add_argument(
        "--out",
        type=str,
        help="Output path for static model (default: src/project_paths/project_paths_static.py)",
    )

    # print-urls command
    print_urls_parser = subparsers.add_parser("print-urls", help="Print resolved URLs")
    print_urls_parser.add_argument(
        "--mode",
        choices=["lenient", "strict"],
        default="lenient",
        help="Validation mode (default: lenient)",
    )
    print_urls_parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format (default: json)",
    )
    print_urls_parser.add_argument(
        "--src",
        choices=["pyproject", "dotenv", "all"],
        default="all",
        help="URL source (default: all - merged from both sources)",
    )
    print_urls_parser.add_argument(
        "--config", type=str, help="Path to .urls config file (default: .urls)"
    )

    # validate-urls command
    validate_urls_parser = subparsers.add_parser(
        "validate-urls", help="Validate URLs and report results"
    )
    validate_urls_parser.add_argument(
        "--mode",
        choices=["lenient", "strict"],
        default="lenient",
        help="Validation mode (default: lenient)",
    )
    validate_urls_parser.add_argument(
        "--src",
        choices=["pyproject", "dotenv", "all"],
        default="all",
        help="URL source (default: all - merged from both sources)",
    )
    validate_urls_parser.add_argument(
        "--config", type=str, help="Path to .urls config file (default: .urls)"
    )

    # gen-static-urls command
    gen_static_urls_parser = subparsers.add_parser(
        "gen-static-urls", help="Generate static URL dataclass file"
    )
    gen_static_urls_parser.add_argument(
        "--mode",
        choices=["lenient", "strict"],
        default="lenient",
        help="Validation mode (default: lenient)",
    )
    gen_static_urls_parser.add_argument(
        "--output",
        type=str,
        help="Output path for static model (default: src/project_paths/project_urls_static.py)",
    )

    args = parser.parse_args()

    # Dispatch to appropriate command handler
    if args.command == "print":
        exit_code = cmd_print(args)
    elif args.command == "validate":
        exit_code = cmd_validate(args)
    elif args.command == "gen-static":
        exit_code = cmd_gen_static(args)
    elif args.command == "print-urls":
        exit_code = cmd_print_urls(args)
    elif args.command == "validate-urls":
        exit_code = cmd_validate_urls(args)
    elif args.command == "gen-static-urls":
        exit_code = cmd_gen_static_urls(args)
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
