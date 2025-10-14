import argparse
import json
import sys
from typing import Optional

from .config import Intelli3Config
from .builder import PipelineBuilder


def build_parser() -> argparse.ArgumentParser:
    """
    Create the CLI argument parser for intelli3text.

    Returns:
        argparse.ArgumentParser: Configured parser.
    """
    parser = argparse.ArgumentParser(
        prog="intelli3text",
        description="Process a source (URL/file) and return JSON; optional PDF export."
    )
    parser.add_argument(
        "source",
        help="URL or file path (.pdf, .docx, .txt)."
    )
    parser.add_argument(
        "--export-pdf",
        dest="export_pdf",
        help="Path to write the PDF report (optional)."
    )
    parser.add_argument(
        "--lid-primary",
        default="fasttext",
        choices=["fasttext", "cld3"],
        help="Primary language detector strategy (default: fasttext)."
    )
    parser.add_argument(
        "--lid-fallback",
        default="none",
        choices=["cld3", "none"],
        help="Optional fallback language detector (default: none)."
    )
    parser.add_argument(
        "--nlp-size",
        default="lg",
        choices=["lg", "md", "sm"],
        help="Preferred spaCy model size (falls back md→sm→blank)."
    )
    parser.add_argument(
        "--cleaners",
        default="ftfy,clean_text,pdf_breaks",
        help="Comma-separated cleaners chain (default: ftfy,clean_text,pdf_breaks)."
    )
    parser.add_argument(
        "--json-out",
        dest="json_out",
        help="Write the JSON output to this file (optional)."
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-error console output."
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """
    Entry point for the intelli3text CLI.

    Args:
        argv: Optional explicit argv list; defaults to sys.argv[1:].

    Returns:
        int: Process exit code (0 = success, non-zero = error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        cfg = Intelli3Config(
            cleaners=[c.strip() for c in args.cleaners.split(",") if c.strip()],
            lid_primary=args.lid_primary,
            lid_fallback=None if args.lid_fallback == "none" else args.lid_fallback,
            nlp_model_pref=args.nlp_size,
            export={"pdf": {"path": args.export_pdf, "include_global_normalized": True}}
            if args.export_pdf
            else None,
        )

        pipeline = PipelineBuilder(cfg).build()
        result = pipeline.process(args.source)

        if args.json_out:
            with open(args.json_out, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            if not args.quiet:
                sys.stderr.write(f"[ok] JSON written to: {args.json_out}\n")
        else:
            # Write to stdout so it can be piped: intelli3text "URL" > out.json
            json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            sys.stdout.flush()

        if args.export_pdf and not args.quiet:
            sys.stderr.write(f"[ok] PDF written to: {args.export_pdf}\n")

        return 0

    except KeyboardInterrupt:
        sys.stderr.write("\n[error] Interrupted by user.\n")
        return 130  # 128 + SIGINT
    except Exception as e:
        # Print error to stderr and return non-zero exit code
        sys.stderr.write(f"[error] {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
