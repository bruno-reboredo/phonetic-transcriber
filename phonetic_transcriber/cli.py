"""Command line interface for the phonetic transcriber application."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Dict, Iterable

from .english import EnglishIPATranscriber


def _load_lexicon_file(path: Path) -> Dict[str, str]:
    """Load a tab-separated ``word\tipa`` lexicon file."""

    if not path.exists():
        raise FileNotFoundError(f"Lexicon file not found: {path}")
    lexicon: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "\t" not in stripped:
                raise ValueError(
                    f"Expected a tab-separated entry on line {line_number} of {path}"
                )
            word, ipa = stripped.split("\t", 1)
            lexicon[word.lower()] = ipa
    return lexicon


def _read_text_from_paths(paths: Iterable[Path]) -> str:
    parts = []
    for path in paths:
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Transcribe English text into the International Phonetic Alphabet (IPA)."
        )
    )
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--text",
        "-t",
        help="Text to transcribe. When omitted, data is read from stdin.",
    )
    source_group.add_argument(
        "--file",
        "-f",
        action="append",
        type=Path,
        help="Path to a text file to transcribe. Can be provided multiple times.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional file to write the IPA transcription to. Prints to stdout by default.",
    )
    parser.add_argument(
        "--extra-lexicon",
        "-x",
        type=Path,
        help=(
            "Additional tab-separated lexicon file to extend the built-in pronunciation list."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    extra_lexicon: Dict[str, str] | None = None
    if args.extra_lexicon:
        try:
            extra_lexicon = _load_lexicon_file(args.extra_lexicon)
        except (FileNotFoundError, ValueError) as exc:  # pragma: no cover - defensive
            parser.error(str(exc))

    transcriber = EnglishIPATranscriber(extra_lexicon=extra_lexicon)

    if args.text is not None:
        text = args.text
    elif args.file:
        text = _read_text_from_paths(args.file)
    else:
        if sys.stdin.isatty():
            print("Enter text to transcribe. Press Ctrl-D (Unix) or Ctrl-Z (Windows) when done.")
        text = sys.stdin.read()

    ipa = transcriber.transcribe_text(text)

    if args.output:
        args.output.write_text(ipa, encoding="utf-8")
    else:
        print(ipa)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
