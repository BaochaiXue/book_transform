#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable

SUPPORTED_SUFFIXES = {".pdf", ".epub"}


def extract_pdf_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: pypdf. Install with `pip install pypdf`."
        ) from exc

    reader = PdfReader(str(pdf_path))
    pages_text: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        cleaned = text.strip()
        if cleaned:
            pages_text.append(cleaned)
    return "\n\n".join(pages_text)


def extract_epub_text(epub_path: Path) -> str:
    try:
        import ebooklib
        from ebooklib import epub
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: ebooklib. Install with `pip install ebooklib`."
        ) from exc

    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: beautifulsoup4. Install with `pip install beautifulsoup4`."
        ) from exc

    book = epub.read_epub(str(epub_path))
    docs_text: list[str] = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text(separator="\n")
            cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
            if cleaned:
                docs_text.append(cleaned)
    return "\n\n".join(docs_text)


def iter_source_books(raw_dir: Path) -> Iterable[Path]:
    for file_path in raw_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield file_path


def map_to_txt_path(book_path: Path, raw_dir: Path, txt_dir: Path) -> Path:
    return txt_dir / book_path.relative_to(raw_dir).with_suffix(".txt")


def convert_book(book_path: Path) -> str:
    suffix = book_path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(book_path)
    if suffix == ".epub":
        return extract_epub_text(book_path)
    raise ValueError(f"Unsupported file format: {book_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Scan raw_book and convert .pdf/.epub files to .txt if output file does not exist."
        )
    )
    parser.add_argument("--raw-dir", type=Path, default=Path("raw_book"))
    parser.add_argument("--txt-dir", type=Path, default=Path("txt_book"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    args.raw_dir.mkdir(parents=True, exist_ok=True)
    args.txt_dir.mkdir(parents=True, exist_ok=True)

    source_books = sorted(iter_source_books(args.raw_dir))
    if not source_books:
        logging.info("No .pdf or .epub files found in %s", args.raw_dir)
        return

    converted = 0
    skipped = 0
    failed = 0

    for book_path in source_books:
        out_path = map_to_txt_path(book_path, args.raw_dir, args.txt_dir)
        if out_path.exists():
            logging.info("Skip (already exists): %s", out_path)
            skipped += 1
            continue

        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            text = convert_book(book_path)
            out_path.write_text(text, encoding="utf-8")
            logging.info("Converted: %s -> %s", book_path, out_path)
            converted += 1
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed: %s (%s)", book_path, exc)
            failed += 1

    logging.info("Done. converted=%d skipped=%d failed=%d", converted, skipped, failed)


if __name__ == "__main__":
    main()
