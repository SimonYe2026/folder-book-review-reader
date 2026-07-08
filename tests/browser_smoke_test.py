#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import socket
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEMO = ROOT / "examples" / "generated" / "basic-reader.demo.html"


def fail(message: str) -> None:
    raise AssertionError(message)


def require_playwright():
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is required for browser smoke tests.\n"
            "Install the development dependency first:\n\n"
            "  python -m pip install -r requirements-dev.txt\n"
            "  python -m playwright install chromium\n"
        ) from exc
    return expect, sync_playwright


def free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


@contextlib.contextmanager
def serve_root(root: Path):
    port = free_port()

    class Handler(QuietHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def relative_url_for(path: Path) -> str:
    try:
        relative = path.resolve().relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"HTML path must stay inside the project root: {path}") from exc
    return "/".join(relative.parts)


def run_reader_flow(page, expect) -> None:
    expect(page.locator("#bookTitle")).to_contain_text("Markdown/TXT/CSV")
    expect(page.locator("#chapterList .chapter-item")).to_have_count(7)
    expect(page.locator("#positionText")).to_contain_text("1 / 7")

    page.locator("#extFilter").select_option(".csv")
    expect(page.locator("#chapterList .chapter-item")).to_have_count(1)
    expect(page.locator("#chapterTitle")).to_contain_text("004-review-table")
    expect(page.locator(".csv-table")).to_be_visible()

    csv_row = page.locator('[data-block-type="csv-row"][data-block-index="2"]')
    csv_row.click()
    if not csv_row.evaluate("element => element.classList.contains('csv-row-active')"):
        fail("clicking a CSV row should mark it as the active review row")
    page.keyboard.press("r")
    expect(page.locator("#reviewDialog")).to_be_visible()
    expect(page.locator("#dialogQuote")).to_contain_text("按行批复")
    expect(page.locator("#dialogQuote")).to_contain_text("AI 助手")
    page.locator("#dialogComment").fill("browser smoke csv row review")
    page.locator("#reviewForm button[type='submit']").click()
    expect(page.locator("#reviewDialog")).not_to_be_visible()
    wait_for_preview(page, "第 2 行")
    wait_for_preview(page, "browser smoke csv row review")

    page.locator("#extFilter").select_option("all")
    page.locator("#searchInput").fill("zh-")
    expect(page.locator("#chapterList .chapter-item")).to_have_count(3)
    expect(page.locator("#positionText")).to_contain_text("1 / 3")
    first_title = page.locator("#chapterTitle").inner_text()
    page.locator("#topNextButton").click()
    expect(page.locator("#positionText")).to_contain_text("2 / 3")
    second_title = page.locator("#chapterTitle").inner_text()
    if first_title == second_title:
        fail("next navigation did not move inside filtered results")

    page.locator("#floatingReviewButton").click()
    expect(page.locator("#reviewDialog")).to_be_visible()
    page.locator("#dialogComment").fill("browser smoke filtered review")
    page.locator("#reviewForm button[type='submit']").click()
    wait_for_preview(page, "browser smoke filtered review")
    expect(page.locator("#reviewCount")).to_contain_text("2")


def wait_for_preview(page, text: str) -> None:
    page.wait_for_function(
        "(needle) => document.querySelector('#reviewPreview')?.value.includes(needle)",
        arg=text,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a real browser click-flow smoke test for generated reader HTML.")
    parser.add_argument(
        "--html",
        default=str(DEFAULT_DEMO),
        help="Generated reader HTML to test. Defaults to examples/generated/basic-reader.demo.html.",
    )
    parser.add_argument("--headed", action="store_true", help="Show the browser window while testing.")
    parser.add_argument("--slow-mo", type=int, default=0, help="Slow browser actions by N milliseconds.")
    args = parser.parse_args(argv)

    html_path = Path(args.html).resolve()
    if not html_path.exists():
        raise SystemExit(f"HTML file does not exist: {html_path}")

    expect, sync_playwright = require_playwright()
    with serve_root(ROOT) as base_url:
        target_url = f"{base_url}/{relative_url_for(html_path)}"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not args.headed, slow_mo=args.slow_mo)
            context = browser.new_context(viewport={"width": 1440, "height": 960})
            page = context.new_page()
            page.goto(target_url, wait_until="domcontentloaded")
            page.evaluate("localStorage.clear()")
            page.reload(wait_until="domcontentloaded")
            run_reader_flow(page, expect)
            context.close()
            browser.close()

    print(f"browser smoke test passed: {html_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
