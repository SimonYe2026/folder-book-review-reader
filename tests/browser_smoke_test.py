#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import socket
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEMO = ROOT / "examples" / "generated" / "basic-reader.demo.html"
ENGLISH_DEMO = ROOT / "examples" / "generated" / "basic-reader.en.demo.html"
DOCS_DEMO = ROOT / "examples" / "generated" / "project-docs.demo.html"
CONVERTED_READER = ROOT / "output" / "reader.converted.html"


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
    expect(page.locator("#chapterList")).to_be_visible()
    expect(page.locator("#bookmarkList")).to_be_hidden()
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
    page.keyboard.press("b")
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(1)
    expect(page.locator("#bookmarkCurrentButton")).to_have_attribute("aria-pressed", "true")

    page.locator("#bookmarkTabButton").click()
    expect(page.locator("#bookmarkList")).to_be_visible()
    expect(page.locator("#extFilter")).to_have_value(".csv")
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(1)
    page.locator("#tocTabButton").click()
    expect(page.locator("#chapterList")).to_be_visible()
    expect(page.locator("#bookmarkList")).to_be_hidden()
    expect(page.locator("#extFilter")).to_have_value(".csv")
    expect(page.locator("#chapterList .chapter-item")).to_have_count(1)

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

    filtered_target = page.evaluate(
        """() => {
          const block = nearestVisualCenterBlock();
          return { type: block?.dataset.blockType || "", index: block?.dataset.blockIndex || "" };
        }"""
    )
    if not filtered_target["type"] or not filtered_target["index"]:
        fail("floating review needs a visual-center target")
    filtered_target_selector = (
        f'[data-block-type="{filtered_target["type"]}"]'
        f'[data-block-index="{filtered_target["index"]}"]'
    )
    page.locator("#floatingReviewButton").click()
    expect(page.locator("#reviewDialog")).to_be_visible()
    page.locator("#dialogComment").fill("browser smoke filtered review")
    page.locator("#reviewForm button[type='submit']").click()
    wait_for_preview(page, "browser smoke filtered review")
    expect(page.locator("#reviewCount")).to_contain_text("2")

    click_review_item(page, "browser smoke csv row review")
    expect(page.locator("#searchInput")).to_have_value("")
    expect(page.locator("#extFilter")).to_have_value("all")
    expect(page.locator("#chapterTitle")).to_contain_text("004-review-table")
    wait_for_class(page, '[data-block-type="csv-row"][data-block-index="2"]', "csv-row-active")
    wait_for_class(page, '[data-block-type="csv-row"][data-block-index="2"]', "review-target-highlight")

    page.locator("#searchInput").fill("zh-")
    page.locator("#bookmarkTabButton").click()
    expect(page.locator("#bookmarkList")).to_be_visible()
    page.locator("#bookmarkList .bookmark-open").click()
    expect(page.locator("#searchInput")).to_have_value("")
    expect(page.locator("#chapterTitle")).to_contain_text("004-review-table")
    wait_for_class(page, '[data-block-type="csv-row"][data-block-index="2"]', "review-target-highlight")

    click_review_item(page, "browser smoke filtered review")
    expect(page.locator("#chapterTitle")).to_contain_text(second_title)
    expect(page.locator(filtered_target_selector + ".review-target-highlight")).to_be_visible()
    page.locator("#bookmarkCurrentButton").click()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(2)
    page.locator("#bookmarkList .bookmark-open").last.click()
    expect(page.locator("#chapterTitle")).to_contain_text(second_title)
    expect(page.locator('[data-block-index].review-target-highlight')).to_be_visible()

    page.reload(wait_until="domcontentloaded")
    expect(page.locator("#bookmarkList")).to_be_visible()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(2)
    expect(page.locator("#reviewCount")).to_contain_text("2")

    page.locator("#bookmarkList .bookmark-open").last.click()
    expect(page.locator('[data-block-index].review-target-highlight')).to_be_visible()
    expect(page.locator("#bookmarkCurrentButton")).to_have_attribute("aria-pressed", "true")
    page.locator("#bookmarkCurrentButton").click()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(1)
    expect(page.locator("#bookmarkCurrentButton")).to_have_attribute("aria-pressed", "false")
    page.locator("#bookmarkCurrentButton").click()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(2)

    page.locator("#tocTabButton").click()
    expect(page.locator("#chapterList")).to_be_visible()
    page.locator("#searchInput").fill("not-a-real-file")
    expect(page.locator("#chapterList .chapter-item")).to_have_count(0)
    page.locator("#clearFilterButton").click()
    expect(page.locator("#searchInput")).to_have_value("")
    expect(page.locator("#chapterList .chapter-item")).to_have_count(7)
    first_chapter_before_sort = page.locator("#chapterList .chapter-item").first.inner_text()
    page.locator("#sortButton").click()
    first_chapter_after_sort = page.locator("#chapterList .chapter-item").first.inner_text()
    if first_chapter_before_sort == first_chapter_after_sort:
        fail("sort button should reverse the visible chapter order")
    page.locator("#sortButton").click()

    initial_font_size = page.evaluate(
        "getComputedStyle(document.documentElement).getPropertyValue('--reader-font-size')"
    )
    page.locator("#largerButton").click()
    if page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--reader-font-size')") == initial_font_size:
        fail("larger font button should update the reader font size")
    page.locator("#widthSelect").select_option("780")
    if page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--reader-width')") != "780px":
        fail("reading width control should update the reader width")
    page.locator("#themeButton").click()
    if not page.evaluate("document.body.classList.contains('dark')"):
        fail("theme button should enable dark mode")
    page.locator("#toggleTocButton").click()
    wait_for_class(page, "#layoutRoot", "left-collapsed")
    page.locator("#toggleTocButton").click()
    page.locator("#toggleReviewPanelButton").click()
    wait_for_class(page, "#layoutRoot", "right-collapsed")
    page.locator("#toggleReviewPanelButton").click()
    page.locator("#resetLayoutButton").click()
    if page.evaluate("document.body.classList.contains('dark')"):
        fail("reset layout should restore the configured light theme")
    left_width = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--left-panel-width')")
    drag_panel(page, "#leftPanelResizer", 40)
    if page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--left-panel-width')") == left_width:
        fail("left panel resize handle should update the panel width")
    right_width = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--right-panel-width')")
    drag_panel(page, "#rightPanelResizer", -40)
    if page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--right-panel-width')") == right_width:
        fail("right panel resize handle should update the panel width")

    selected_text = page.locator("#content [data-block-index]").first.evaluate(
        "element => element.firstChild?.textContent.trim() || ''"
    )
    if not selected_text:
        fail("selection review test needs a text node in the current block")
    page.evaluate(
        """() => {
          const block = document.querySelector('#content [data-block-index]');
          const range = document.createRange();
          range.selectNodeContents(block.firstChild);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
        }"""
    )
    page.locator("#floatingReviewButton").click()
    expect(page.locator("#reviewDialog")).to_be_visible()
    expect(page.locator("#dialogQuote")).to_contain_text(selected_text)
    page.locator("#dialogComment").fill("browser smoke selected text review")
    page.locator("#reviewForm button[type='submit']").click()
    expect(page.locator("#reviewCount")).to_contain_text("3")

    page.locator("#content .block-review").first.click()
    expect(page.locator("#reviewDialog")).to_be_visible()
    page.locator("#dialogComment").fill("browser smoke block button review")
    page.locator("#reviewForm button[type='submit']").click()
    expect(page.locator("#reviewCount")).to_contain_text("4")
    page.locator("[data-edit-comment]").last.fill("browser smoke edited review")
    wait_for_preview(page, "browser smoke edited review")
    page.locator("[data-edit-action]").last.select_option(index=1)
    expect(page.locator("#reviewList .review-item")).to_have_count(4)

    page.locator("#copyReviewButton").click()
    expect(page.locator("#copyReviewButton")).to_contain_text("已复制")
    with page.expect_download() as download_info:
        page.locator("#downloadReviewButton").click()
    download = download_info.value
    if not download.suggested_filename.startswith("review_") or not download.suggested_filename.endswith(".md"):
        fail("review download should use the expected Markdown filename")

    page.locator("#reviewList [data-delete-review]").last.click()
    expect(page.locator("#reviewCount")).to_contain_text("3")
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#clearReviewsButton").click()
    expect(page.locator("#reviewCount")).to_contain_text("0")
    expect(page.locator("#reviewList .review-item")).to_have_count(0)


def wait_for_preview(page, text: str) -> None:
    page.wait_for_function(
        "(needle) => document.querySelector('#reviewPreview')?.value.includes(needle)",
        arg=text,
    )


def wait_for_class(page, selector: str, class_name: str) -> None:
    page.wait_for_function(
        "([selector, className]) => document.querySelector(selector)?.classList.contains(className)",
        arg=[selector, class_name],
    )


def drag_panel(page, selector: str, offset: int) -> None:
    box = page.locator(selector).bounding_box()
    if not box:
        fail(f"resize handle is not visible: {selector}")
    x = box["x"] + box["width"] / 2
    y = box["y"] + min(100, box["height"] / 2)
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + offset, y, steps=4)
    page.mouse.up()


def click_review_item(page, text: str) -> None:
    item = page.locator("#reviewList .review-item").filter(has_text=text)
    item.click(position={"x": 12, "y": 12})


def run_english_reader_flow(page, expect) -> None:
    expect(page.locator("#bookTitle")).to_contain_text("Local Markdown/TXT/CSV")
    expect(page.locator("#tocTabButton")).to_contain_text("Contents")
    expect(page.locator("#bookmarkTabButton")).to_contain_text("Bookmarks")
    visual_target = page.evaluate(
        """() => {
          const block = nearestVisualCenterBlock();
          return { type: block?.dataset.blockType || "", index: block?.dataset.blockIndex || "" };
        }"""
    )
    if not visual_target["type"] or not visual_target["index"]:
        fail("English bookmark flow needs a visual-center target")
    page.locator("#bookmarkCurrentButton").click()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(1)
    page.locator("#bookmarkTabButton").click()
    expect(page.locator("#bookmarkList")).to_be_visible()
    page.locator("#bookmarkList .bookmark-open").click()
    expect(
        page.locator(
            f'[data-block-type="{visual_target["type"]}"]'
            f'[data-block-index="{visual_target["index"]}"].review-target-highlight'
        )
    ).to_be_visible()


def run_bookmark_block_type_flow(page, expect) -> None:
    paragraphs = page.locator('[data-block-type="paragraph"]')
    bookmark_current_block(page, expect, paragraphs.nth(0), 1)
    page.locator("#tocTabButton").click()
    bookmark_current_block(page, expect, paragraphs.nth(1), 2)
    page.locator("#tocTabButton").click()
    bookmark_current_block(page, expect, page.locator('[data-block-type="list-item"]').first, 3)
    page.locator("#tocTabButton").click()
    bookmark_current_block(page, expect, page.locator('[data-block-type="quote"]').first, 4)

    page.locator("#tocTabButton").click()
    page.locator("#chapterList .chapter-item").filter(has_text="This is a plain TXT sample").click()
    bookmark_current_block(page, expect, page.locator('[data-block-type="paragraph"]').nth(1), 5)
    page.locator("#bookmarkList .bookmark-delete").first.click()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(4)
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#clearBookmarksButton").click()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(0)
    expect(page.locator("#clearBookmarksButton")).to_be_hidden()


def run_bookmark_scroll_reset_flow(page, expect) -> None:
    target = page.locator('[data-block-type="paragraph"]').first
    target.evaluate("element => element.click()")
    page.locator("#bookmarkCurrentButton").click()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(1)
    expect(page.locator("#bookmarkCurrentButton")).to_have_attribute("aria-pressed", "true")

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    expect(page.locator("#bookmarkCurrentButton")).to_have_attribute("aria-pressed", "false")
    page.keyboard.press("b")
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(2)


def run_visual_center_target_flow(page, expect) -> None:
    bookmark_target = visual_center_target(page)
    page.keyboard.press("b")
    page.locator("#bookmarkTabButton").click()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(1)
    page.locator("#bookmarkList .bookmark-open").click()
    wait_for_class(
        page,
        bookmark_target,
        "review-target-highlight",
    )

    review_target = visual_center_target(page)
    review_target_text = page.locator(review_target).evaluate(
        """element => {
          const clone = element.cloneNode(true);
          clone.querySelectorAll('.block-review').forEach(button => button.remove());
          return clone.textContent.trim();
        }"""
    )
    page.keyboard.press("r")
    expect(page.locator("#reviewDialog")).to_be_visible()
    expect(page.locator("#dialogQuote")).to_contain_text(review_target_text)
    page.locator("#dialogComment").fill("browser smoke visual center review")
    page.locator("#reviewForm button[type='submit']").click()
    expect(page.locator("#reviewList .review-item")).to_contain_text("阅读视口")
    expect(page.locator("#reviewList .review-context")).to_contain_text(review_target_text)
    wait_for_preview(page, "- 审阅范围: 阅读视口（核心引用仅用于定位）")
    wait_for_preview(page, "#### 附近上下文")
    click_review_item(page, "browser smoke visual center review")
    wait_for_class(
        page,
        review_target,
        "review-target-highlight",
    )


def run_heading_review_flow(page, expect) -> None:
    heading = page.locator('#content h1[data-block-type="heading"]').first
    next_heading = page.locator('#content h2[data-block-type="heading"]').first
    expect(heading).to_be_visible()
    heading.click()
    heading.locator(".block-review").click()
    expect(page.locator("#reviewDialog")).to_be_visible()
    expect(page.locator("#dialogQuote")).to_contain_text("Introduction")
    page.locator("#dialogComment").fill("browser smoke heading review")
    page.locator("#reviewForm button[type='submit']").click()
    expect(page.locator("#reviewDialog")).not_to_be_visible()

    # Keep a previous selection active, then explicitly review another heading.
    # The button target must win over that earlier selection.
    page.evaluate(
        """() => {
          const heading = document.querySelector('#content h1[data-block-type="heading"]');
          const range = document.createRange();
          range.selectNodeContents(heading);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
        }"""
    )
    next_heading.click()
    next_heading.locator(".block-review").click()
    expect(page.locator("#dialogQuote")).to_contain_text("What to Try")
    page.locator("#dialogComment").fill("browser smoke second heading review")
    page.locator("#reviewForm button[type='submit']").click()
    expect(page.locator("#reviewList .review-item")).to_have_count(2)

    click_review_item(page, "browser smoke second heading review")
    wait_for_class(page, '#content h2[data-block-type="heading"]', "review-target-highlight")
    click_review_item(page, "browser smoke heading review")
    wait_for_class(page, '#content h1[data-block-type="heading"]', "review-target-highlight")
    expect(page.locator("#reviewList")).to_contain_text("标题")


def run_legacy_docs_review_recovery_flow(page, expect) -> None:
    page.locator("#chapterList .chapter-item").filter(has_text="03-customization-guide.en.md").click()
    target_heading = page.locator('#content h2[data-block-type="heading"]', has_text="Embed in an Existing Project")
    target_paragraph = page.locator('#content [data-block-type="paragraph"]', has_text="Chinese counterpart:")
    expect(target_heading).to_be_visible()
    expect(target_paragraph).to_be_visible()
    chapter_id = page.locator("#content").get_attribute("data-chapter-id")
    target_index = target_heading.get_attribute("data-block-index")
    paragraph_index = target_paragraph.get_attribute("data-block-index")
    if not chapter_id or not target_index or not paragraph_index:
        fail("docs review recovery test needs the selected heading coordinates")
    page.evaluate(
        """([chapterId]) => {
          const key = "folder-review-reader:Local Markdown/TXT Review Reader Docs:reviews";
          localStorage.setItem(key, JSON.stringify([{
            id: "legacy-heading-recovery",
            chapter_id: chapterId,
            file_name: "03-customization-guide.en.md",
            relative_path: "docs/03-customization-guide.en.md",
            title: "Customization Guide",
            block_index: "1",
            block_type: "paragraph",
            position_text: "",
            quote: "Embed in an Existing Project",
            action: "修改",
            target: "原文段落",
            comment: "browser smoke legacy heading recovery",
            created_at: "2026-07-11T00:00:00"
          }, {
            id: "legacy-paragraph-recovery",
            chapter_id: chapterId,
            file_name: "03-customization-guide.en.md",
            relative_path: "docs/03-customization-guide.en.md",
            title: "Customization Guide",
            block_index: "2",
            block_type: "paragraph",
            position_text: "",
            quote: "Chinese counterpart: 03-customization-guide.zh-CN.md",
            action: "修改",
            target: "原文段落",
            comment: "browser smoke shifted paragraph recovery",
            created_at: "2026-07-11T00:00:00"
          }]));
        }""",
        [chapter_id],
    )
    page.reload(wait_until="domcontentloaded")
    click_review_item(page, "browser smoke legacy heading recovery")
    wait_for_class(
        page,
        f'#content h2[data-block-type="heading"][data-block-index="{target_index}"]',
        "review-target-highlight",
    )
    expect(page.locator('#content h2[data-block-type="heading"]', has_text="Embed in an Existing Project")).to_be_visible()
    click_review_item(page, "browser smoke shifted paragraph recovery")
    wait_for_class(
        page,
        f'#content [data-block-type="paragraph"][data-block-index="{paragraph_index}"]',
        "review-target-highlight",
    )

    code_block = page.locator('#content [data-block-type="code-block"]').filter(has_text="workspace_root: .").first
    code = code_block.locator("code")
    code_index = code_block.get_attribute("data-block-index")
    if not code_index:
        fail("code selection review test needs code-block coordinates")
    page.evaluate(
        """() => {
          const code = Array.from(document.querySelectorAll('#content [data-block-type="code-block"] code'))
            .find(item => item.textContent.includes("workspace_root: ."));
          const range = document.createRange();
          range.selectNodeContents(code);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
        }"""
    )
    page.keyboard.press("r")
    expect(page.locator("#reviewDialog")).to_be_visible()
    expect(page.locator("#dialogQuote")).to_contain_text("workspace_root: .")
    page.locator("#dialogComment").fill("browser smoke code block review")
    page.locator("#reviewForm button[type='submit']").click()
    click_review_item(page, "browser smoke code block review")
    wait_for_class(
        page,
        f'#content [data-block-type="code-block"][data-block-index="{code_index}"]',
        "review-target-highlight",
    )
    code_block.hover()
    direct_code_review = code_block.locator(".block-review-contained")
    expect(direct_code_review).to_have_css("opacity", "1")
    direct_code_review.click()
    expect(page.locator("#reviewDialog")).to_be_visible()
    expect(page.locator("#dialogQuote")).to_contain_text("workspace_root: .")
    expect(page.locator("#dialogQuote")).not_to_contain_text("复制代码")
    page.locator("#dialogComment").fill("browser smoke direct code block review")
    page.locator("#reviewForm button[type='submit']").click()

    page.locator("#chapterList .chapter-item").filter(has_text="04-user-manual.en.md").click()
    markdown_table = page.locator('#content [data-block-type="table"]').first
    table_index = markdown_table.get_attribute("data-block-index")
    if not table_index:
        fail("Markdown table review test needs table coordinates")
    page.evaluate(
        """() => {
          const cell = document.querySelector('#content [data-block-type="table"] td');
          const range = document.createRange();
          range.selectNodeContents(cell);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
        }"""
    )
    page.keyboard.press("r")
    expect(page.locator("#reviewDialog")).to_be_visible()
    page.locator("#dialogComment").fill("browser smoke markdown table review")
    page.locator("#reviewForm button[type='submit']").click()
    click_review_item(page, "browser smoke markdown table review")
    wait_for_class(
        page,
        f'#content [data-block-type="table"][data-block-index="{table_index}"]',
        "review-target-highlight",
    )
    markdown_table.hover()
    direct_table_review = markdown_table.locator(".block-review-contained")
    expect(direct_table_review).to_have_css("opacity", "1")
    direct_table_review.click()
    expect(page.locator("#reviewDialog")).to_be_visible()
    page.locator("#dialogComment").fill("browser smoke direct markdown table review")
    page.locator("#reviewForm button[type='submit']").click()


def run_docx_table_review_flow(page, expect) -> None:
    docx_table = page.locator('#content [data-block-type="docx-table"]').first
    table_index = docx_table.get_attribute("data-block-index")
    if not table_index:
        fail("DOCX table review test needs table coordinates")
    page.evaluate(
        """() => {
          const cell = document.querySelector('#content [data-block-type="docx-table"] td');
          const range = document.createRange();
          range.selectNodeContents(cell);
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
        }"""
    )
    page.keyboard.press("r")
    expect(page.locator("#reviewDialog")).to_be_visible()
    page.locator("#dialogComment").fill("browser smoke docx table review")
    page.locator("#reviewForm button[type='submit']").click()
    click_review_item(page, "browser smoke docx table review")
    wait_for_class(
        page,
        f'#content [data-block-type="docx-table"][data-block-index="{table_index}"]',
        "review-target-highlight",
    )


def run_mobile_layout_flow(page, expect) -> None:
    expect(page.locator("#searchInput")).to_be_visible()
    expect(page.locator("#floatingReviewButton")).to_be_visible()
    expect(page.locator("#fixedNextButton")).to_be_visible()
    if page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1"):
        fail("mobile reader should not create page-level horizontal overflow")
    page.locator("#bookmarkCurrentButton").click()
    page.locator("#bookmarkTabButton").click()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(1)


def bookmark_current_block(page, expect, block, expected_count: int) -> None:
    block_type = block.get_attribute("data-block-type")
    block_index = block.get_attribute("data-block-index")
    if not block_type or not block_index:
        fail("bookmark target must have a block type and index")
    block.evaluate("element => element.click()")
    page.locator("#bookmarkCurrentButton").click()
    page.locator("#bookmarkTabButton").click()
    expect(page.locator("#chapterList")).to_be_hidden()
    expect(page.locator("#bookmarkList")).to_be_visible()
    expect(page.locator("#bookmarkList .bookmark-item")).to_have_count(expected_count)
    page.locator("#bookmarkList .bookmark-open").last.click()
    wait_for_class(
        page,
        f'[data-block-type="{block_type}"][data-block-index="{block_index}"]',
        "review-target-highlight",
    )


def visual_center_target(page) -> str:
    target = page.evaluate(
        """() => {
          window.getSelection().removeAllRanges();
          const block = nearestVisualCenterBlock();
          return { type: block?.dataset.blockType || "", index: block?.dataset.blockIndex || "" };
        }"""
    )
    if not target["type"] or not target["index"]:
        fail("visual-center flow needs a content-block target")
    return f'[data-block-type="{target["type"]}"][data-block-index="{target["index"]}"]'


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
    subprocess.run(
        [sys.executable, "build_reader.py", "config/workspace.converted.config.md"],
        cwd=ROOT,
        check=True,
    )

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
            english_page = context.new_page()
            english_url = f"{base_url}/{relative_url_for(ENGLISH_DEMO)}"
            english_page.goto(english_url, wait_until="domcontentloaded")
            english_page.evaluate("localStorage.clear()")
            english_page.reload(wait_until="domcontentloaded")
            run_english_reader_flow(english_page, expect)
            coverage_page = context.new_page()
            coverage_page.goto(target_url, wait_until="domcontentloaded")
            coverage_page.evaluate("localStorage.clear()")
            coverage_page.reload(wait_until="domcontentloaded")
            run_bookmark_block_type_flow(coverage_page, expect)
            bookmark_scroll_page = context.new_page()
            bookmark_scroll_page.goto(target_url, wait_until="domcontentloaded")
            bookmark_scroll_page.evaluate("localStorage.clear()")
            bookmark_scroll_page.reload(wait_until="domcontentloaded")
            run_bookmark_scroll_reset_flow(bookmark_scroll_page, expect)
            center_page = context.new_page()
            center_page.goto(target_url, wait_until="domcontentloaded")
            center_page.evaluate("localStorage.clear()")
            center_page.reload(wait_until="domcontentloaded")
            run_visual_center_target_flow(center_page, expect)
            heading_page = context.new_page()
            heading_page.goto(target_url, wait_until="domcontentloaded")
            heading_page.evaluate("localStorage.clear()")
            heading_page.reload(wait_until="domcontentloaded")
            run_heading_review_flow(heading_page, expect)
            docs_page = context.new_page()
            docs_url = f"{base_url}/{relative_url_for(DOCS_DEMO)}"
            docs_page.goto(docs_url, wait_until="domcontentloaded")
            docs_page.evaluate("localStorage.clear()")
            docs_page.reload(wait_until="domcontentloaded")
            run_legacy_docs_review_recovery_flow(docs_page, expect)
            converted_page = context.new_page()
            converted_url = f"{base_url}/{relative_url_for(CONVERTED_READER)}"
            converted_page.goto(converted_url, wait_until="domcontentloaded")
            converted_page.evaluate("localStorage.clear()")
            converted_page.reload(wait_until="domcontentloaded")
            run_docx_table_review_flow(converted_page, expect)
            mobile_page = context.new_page()
            mobile_page.set_viewport_size({"width": 390, "height": 844})
            mobile_page.goto(target_url, wait_until="domcontentloaded")
            mobile_page.evaluate("localStorage.clear()")
            mobile_page.reload(wait_until="domcontentloaded")
            run_mobile_layout_flow(mobile_page, expect)
            context.close()
            browser.close()

    print(f"browser smoke test passed: {html_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
