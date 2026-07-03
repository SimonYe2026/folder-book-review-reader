#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_HTML_PATHS = [
    ROOT / "examples" / "generated" / "basic-reader.demo.html",
    ROOT / "examples" / "generated" / "basic-reader.en.demo.html",
    ROOT / "examples" / "generated" / "project-docs.demo.html",
    ROOT / "examples" / "generated" / "project-docs.en.demo.html",
]

OPTIONAL_OUTPUT_PATHS = [
    ROOT / "output" / "reader.html",
    ROOT / "output" / "reader.en.html",
    ROOT / "output" / "project-docs.html",
    ROOT / "output" / "project-docs.en.html",
    ROOT / "output" / "reader.converted.html",
]

PRIVATE_SNIPPETS = [
    "C:\\Users",
    "AppData",
    "Desktop\\html-md",
    "CodexSandboxOffline",
    "review_2026",
    "112333",
    "12312312",
]

REQUIRED_ELEMENT_IDS = [
    "bookTitle",
    "toggleTocButton",
    "toggleReviewPanelButton",
    "searchInput",
    "extFilter",
    "clearFilterButton",
    "sortButton",
    "smallerButton",
    "largerButton",
    "widthSelect",
    "resetLayoutButton",
    "layoutRoot",
    "chapterList",
    "leftPanelResizer",
    "chapterTitle",
    "sourceLine",
    "topPrevButton",
    "topNextButton",
    "content",
    "bottomPrevButton",
    "bottomNextButton",
    "rightPanelResizer",
    "reviewCount",
    "copyReviewButton",
    "downloadReviewButton",
    "clearReviewsButton",
    "reviewList",
    "reviewPreview",
    "floatingReviewButton",
    "fixedPrevButton",
    "fixedNextButton",
    "positionText",
    "reviewDialog",
    "dialogQuote",
    "dialogAction",
    "dialogTarget",
    "dialogComment",
]

REQUIRED_SNIPPETS = [
    "<!doctype html>",
    'class="toolbar"',
    'class="layout"',
    'class="review-panel"',
    'class="fixed-nav"',
    'class="floating-review"',
    'role="separator"',
    "const BOOK_DATA =",
    "const APP_CONFIG =",
    "localStorage",
    "function visibleChapters()",
    "function ensureCurrentVisible(",
    "function move(delta)",
    "function scrollReaderToTop()",
    "function reviewMarkdown()",
    "function updateReview(",
    "reviewStorageKey",
    "localStorage.setItem(reviewStorageKey",
    "addEventListener(\"keydown\"",
    "data-edit-comment",
    "data-delete-review",
    "reviewBesideReader",
]


def fail(path: Path, message: str) -> None:
    raise AssertionError(f"{path}: {message}")


def extract_const(text: str, name: str, path: Path) -> Any:
    marker = f"const {name} = "
    start = text.find(marker)
    if start == -1:
        fail(path, f"missing {marker.strip()}")
    start += len(marker)
    try:
        value, _ = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError as exc:
        fail(path, f"cannot parse {name}: {exc}")
    return value


def require_all(text: str, needles: list[str], path: Path) -> None:
    missing = [needle for needle in needles if needle not in text]
    if missing:
        fail(path, f"missing required page structure: {missing}")


def check_no_private_or_active_danger(text: str, path: Path) -> None:
    present = [needle for needle in PRIVATE_SNIPPETS if needle in text]
    if present:
        fail(path, f"contains local/private snippets: {present}")

    lowered = text.lower()
    dangerous = [
        "href=\"javascript:",
        "href='javascript:",
        "src=\"data:image/svg+xml",
        "src='data:image/svg+xml",
        "<iframe",
        "<object",
        "<embed",
    ]
    found = [needle for needle in dangerous if needle in lowered]
    if found:
        fail(path, f"contains active unsafe HTML patterns: {found}")


def check_data_shape(book_data: dict[str, Any], app_config: dict[str, Any], path: Path) -> None:
    if not isinstance(book_data.get("title"), str) or not book_data["title"].strip():
        fail(path, "BOOK_DATA.title must be a non-empty string")
    if not isinstance(book_data.get("generated_at"), str) or "T" not in book_data["generated_at"]:
        fail(path, "BOOK_DATA.generated_at should be an ISO-like timestamp")

    chapters = book_data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        fail(path, "BOOK_DATA.chapters must be a non-empty list")

    ids: set[str] = set()
    relative_paths: set[str] = set()
    reviewable_count = 0
    total_words = 0

    for index, chapter in enumerate(chapters, start=1):
        if not isinstance(chapter, dict):
            fail(path, f"chapter {index} is not an object")
        for key in [
            "id",
            "title",
            "file_name",
            "relative_path",
            "ext",
            "word_count",
            "modified_time",
            "content_html",
            "content_text",
        ]:
            if key not in chapter:
                fail(path, f"chapter {index} missing {key}")

        chapter_id = chapter["id"]
        relative_path = chapter["relative_path"]
        if chapter_id in ids:
            fail(path, f"duplicate chapter id: {chapter_id}")
        if relative_path in relative_paths:
            fail(path, f"duplicate chapter relative_path: {relative_path}")
        ids.add(chapter_id)
        relative_paths.add(relative_path)

        if Path(str(relative_path)).is_absolute() or ".." in Path(str(relative_path)).parts:
            fail(path, f"chapter path should stay relative and local: {relative_path}")
        if chapter["ext"] not in [".md", ".txt"]:
            fail(path, f"unexpected chapter extension: {chapter['ext']}")
        if not isinstance(chapter["word_count"], int) or chapter["word_count"] < 0:
            fail(path, f"invalid word_count for {relative_path}")

        content_html = str(chapter["content_html"])
        lowered_html = content_html.lower()
        if re.search(r"<script(?:\s|>|/)", lowered_html):
            fail(path, f"chapter content contains an active script tag: {relative_path}")
        if re.search(r"\s(?:href|src)\s*=\s*['\"]javascript:", lowered_html):
            fail(path, f"chapter content contains an active javascript URL: {relative_path}")
        if re.search(r"\son[a-z]+\s*=", lowered_html):
            fail(path, f"chapter content contains inline event handler: {relative_path}")
        if "data-block-index=" in content_html:
            reviewable_count += 1
        total_words += chapter["word_count"]

    if reviewable_count == 0:
        fail(path, "no chapter contains data-block-index review anchors")
    if total_words <= 0:
        fail(path, "total word_count should be positive")

    review = app_config.get("review") or {}
    if review.get("enabled") is False:
        fail(path, "public demo should keep review enabled")
    for key in ["actions", "targets"]:
        if not isinstance(review.get(key), list) or not review[key]:
            fail(path, f"review.{key} should be a non-empty list")

    labels = app_config.get("labels") or {}
    locale = str(app_config.get("locale") or "").lower()
    if locale.startswith("en"):
        if labels.get("review_panel") != "Review Board":
            fail(path, "English reader should use English review panel label")
    else:
        if labels.get("review_panel") != "审阅板":
            fail(path, "Chinese reader should use Chinese review panel label")


def check_reader_html(path: Path) -> None:
    if not path.exists():
        fail(path, "HTML file does not exist")
    text = path.read_text(encoding="utf-8", errors="replace")
    require_all(text, REQUIRED_SNIPPETS, path)
    check_no_private_or_active_danger(text, path)

    found_ids = set(re.findall(r'\bid="([^"]+)"', text))
    missing_ids = [element_id for element_id in REQUIRED_ELEMENT_IDS if element_id not in found_ids]
    if missing_ids:
        fail(path, f"missing required element ids: {missing_ids}")

    book_data = extract_const(text, "BOOK_DATA", path)
    app_config = extract_const(text, "APP_CONFIG", path)
    if not isinstance(book_data, dict) or not isinstance(app_config, dict):
        fail(path, "BOOK_DATA and APP_CONFIG should both be JSON objects")
    check_data_shape(book_data, app_config, path)


def default_paths() -> list[Path]:
    paths = list(DEFAULT_HTML_PATHS)
    paths.extend(path for path in OPTIONAL_OUTPUT_PATHS if path.exists())
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check generated reader HTML quality.")
    parser.add_argument("html", nargs="*", help="HTML files to check. Defaults to public generated demos and existing output files.")
    args = parser.parse_args(argv)

    paths = [Path(item).resolve() for item in args.html] if args.html else default_paths()
    if not paths:
        raise AssertionError("no HTML files to check")

    for path in paths:
        check_reader_html(path)
        try:
            display_path = path.relative_to(ROOT)
        except ValueError:
            display_path = path
        print(f"checked {display_path}")

    print(f"html quality check passed ({len(paths)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
