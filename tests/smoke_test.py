#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import shutil
import tempfile
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build_reader
from tools import convert_docs


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True)


def assert_contains(path: Path, needles: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise AssertionError(f"{path} missing expected text: {missing}")


def assert_not_contains(path: Path, needles: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    present = [needle for needle in needles if needle in text]
    if present:
        raise AssertionError(f"{path} contains private or local-only text: {present}")


def main() -> int:
    parsed = build_reader.parse_simple_yaml(
        """
title: 测试配置 # 行尾注释
workspace_root: .
include: ["*.md", "*.txt"]
exclude: []
display:
  default_font_size: 18
  theme: "light # not comment"
review:
  actions: [修改, 总结, 提取]
"""
    )
    if parsed["exclude"] != [] or parsed["include"] != ["*.md", "*.txt"]:
        raise AssertionError("config parser should support inline lists and empty lists")
    if parsed["display"]["theme"] != "light # not comment":
        raise AssertionError("config parser should preserve # inside quoted strings")
    default_config_path = ROOT / "output" / "default-include.config.md"
    default_config_path.parent.mkdir(exist_ok=True)
    default_config_path.write_text(
        "---\n"
        "source_dir: ./examples/basic/drafts\n"
        "---\n",
        encoding="utf-8",
    )
    default_config = build_reader.load_config(default_config_path)
    if default_config["include"] != ["*.md", "*.txt", "*.csv"]:
        raise AssertionError("default include should cover Markdown, TXT, and CSV")

    line_html = build_reader.render_text_basic("one\ntwo\n", paragraph_mode="line")
    if line_html.count('data-block-type="paragraph"') != 2:
        raise AssertionError("line paragraph mode should create one paragraph per non-empty line")
    unsafe_txt = build_reader.render_text_basic(
        '<script>alert(1)</script>\n[bad](javascript:alert(1))\n![x](data:image/svg+xml;base64,PHNjcmlwdD4=)\n',
        paragraph_mode="line",
    )
    if "<script>" in unsafe_txt or "href=" in unsafe_txt or "src=" in unsafe_txt:
        raise AssertionError("TXT rendering should escape HTML and never activate markdown links or images")

    csv_html = build_reader.render_csv_basic(
        'name,note,risk\n'
        'alpha,"quoted, comma",low\n'
        'beta,"line one\nline two",medium\n'
        'formula,"=SUM(1,2) and @name",medium\n'
        'danger,"<script>alert(1)</script><img src=x onerror=alert(1)>",high\n',
        labels=build_reader.DEFAULT_LABELS_EN,
    )
    if '<table class="csv-table">' not in csv_html or 'data-block-type="csv-row"' not in csv_html:
        raise AssertionError("CSV rendering should create a real table with row review anchors")
    if "csv-row-action" in csv_html or "csv-row-tools" in csv_html or 'class="btn csv-current-row-review"' not in csv_html:
        raise AssertionError("CSV review control should render as a single table-level button outside the table")
    if "quoted, comma" not in csv_html or "line one" not in csv_html or "line two" not in csv_html:
        raise AssertionError("CSV rendering should preserve quoted commas and quoted newlines")
    if "<script>" in csv_html or "onerror=" in csv_html or "<img" in csv_html:
        raise AssertionError("CSV rendering should escape HTML and never activate cell content")
    if "&#61;SUM(1,2)" not in csv_html or "@name" not in csv_html:
        raise AssertionError("CSV formula-like cells should remain visible as plain text")

    blank_line_html = build_reader.render_text_basic("one\ntwo\n\nthree\n", paragraph_mode="blank_line")
    if blank_line_html.count('data-block-type="paragraph"') != 2:
        raise AssertionError("blank_line paragraph mode should group lines until blank lines")

    clean_doc = convert_docs.clean_converted_text(
        "status: ACTIVE\n"
        "module: governance\n"
        "中控板与认知资产治理总览\n"
        "0. 一句话定义\n"
        "中控板是人机协作中的状态交汇点。\n"
        "1. 为什么需要中控板\n"
    )
    if not clean_doc.startswith("status: ACTIVE"):
        raise AssertionError("converter should preserve clean front matter before numbered sections")

    md_html = build_reader.render_markdown_basic("```text\nhello\n```", labels={"copy_code": "复制代码"})
    if "复制代码" not in md_html or "Copy code" in md_html:
        raise AssertionError("markdown code copy button should use configured labels")
    protected_image = build_reader.inline_markdown("![x](data:image/png;base64,AA++BB==)")
    if 'src="data:image/png;base64,AA++BB=="' not in protected_image or "<u>" in protected_image:
        raise AssertionError("inline formatting must not corrupt image data URLs")
    for image_url in [
        "data:image/jpeg;base64,AA++BB==",
        "data:image/jpg;base64,AA++BB==",
        "data:image/gif;base64,AA++BB==",
        "data:image/webp;base64,AA++BB==",
        "images/local-demo.png",
    ]:
        image_html = build_reader.inline_markdown(f"![x]({image_url})")
        if f'src="{image_url}"' not in image_html:
            raise AssertionError(f"safe image URL should still render: {image_url}")
    svg_image = build_reader.inline_markdown("![x](data:image/svg+xml;base64,PHNjcmlwdD4=)")
    if "src=" in svg_image or "svg+xml" in svg_image:
        raise AssertionError("svg data images should be disabled")
    disabled_link = build_reader.inline_markdown("[bad](javascript:alert(1)) and [web](https://example.com)")
    if "href=" in disabled_link or "javascript:" in disabled_link:
        raise AssertionError("markdown links should be disabled by default")
    if disabled_link.count(build_reader.DISABLED_LINK_TEXT_ZH) != 2:
        raise AssertionError("disabled markdown links should show the source-file placeholder")
    english_disabled_link = build_reader.inline_markdown(
        "[web](https://example.com)",
        labels=build_reader.DEFAULT_LABELS_EN,
    )
    if build_reader.DISABLED_LINK_TEXT_EN not in english_disabled_link or build_reader.DISABLED_LINK_TEXT_ZH in english_disabled_link:
        raise AssertionError("disabled markdown links should use the active locale labels")
    english_link_blocks = build_reader.render_markdown_basic(
        "\n".join(
            [
                "# [Heading](https://example.com)",
                "Paragraph [link](https://example.com).",
                "- List [link](https://example.com)",
                "> Quote [link](https://example.com)",
                "| Column |",
                "| --- |",
                "| Table [link](https://example.com) |",
                "```docx-table",
                '{"rows":[[{"text":["Docx table [link](https://example.com)"],"tables":[]}]]}',
                "```",
            ]
        ),
        labels=build_reader.DEFAULT_LABELS_EN,
    )
    if english_link_blocks.count(build_reader.DISABLED_LINK_TEXT_EN) != 6:
        raise AssertionError("all markdown block renderers should use the active disabled-link label")
    if build_reader.DISABLED_LINK_TEXT_ZH in english_link_blocks or "href=" in english_link_blocks:
        raise AssertionError("localized disabled links should not fall back to Chinese or render hrefs")
    unsafe_image = build_reader.inline_markdown("![bad](javascript:alert(1))")
    if "src=" in unsafe_image or "javascript:" in unsafe_image:
        raise AssertionError("unsafe markdown image URLs should not be rendered as images")
    malformed_table = build_reader.render_markdown_basic("```docx-table\n{\"rows\":[[\"bad cell\"]]}\n```")
    if "bad cell" not in malformed_table or "docx-structured-table" in malformed_table:
        raise AssertionError("malformed docx-table blocks should fall back to code display")
    serialized = build_reader.safe_json_dumps({"text": "</script><script>alert(1)</script>"})
    if "</script>" in serialized.lower() or "<script" in serialized.lower():
        raise AssertionError("embedded JSON must not contain raw script tags")
    if json.loads(serialized)["text"] != "</script><script>alert(1)</script>":
        raise AssertionError("safe JSON serialization should preserve original data after parsing")
    html_doc = build_reader.html_document(
        {
            "title": "Script Safety",
            "generated_at": "2026-07-02T00:00:00",
            "source_dir": "./x",
            "chapters": [
                {
                    "id": "chapter-001",
                    "title": "</script><script>alert(1)</script>",
                    "file_name": "x.md",
                    "relative_path": "x.md",
                    "path": "x.md",
                    "folder": "",
                    "path_segments": [],
                    "prefix": "x",
                    "ext": ".md",
                    "word_count": 1,
                    "modified_time": "2026-07-02T00:00:00",
                    "content_html": "<p>safe</p>",
                    "content_text": "</script><script>alert(1)</script>",
                }
            ],
        },
        {"title": "Script Safety", "locale": "en", "labels": {}},
    )
    if html_doc.lower().count("</script>") != 1 or "<script>alert" in html_doc.lower():
        raise AssertionError("reader data should not be able to break out of the script tag")

    run([sys.executable, "-m", "py_compile", "build_reader.py", "serve_reader.py", "tools/convert_docs.py"])
    run([sys.executable, "-m", "py_compile", "tools/build_demos.py"])
    run([sys.executable, "-m", "py_compile", "tests/html_quality_check.py", "tests/browser_smoke_test.py"])

    license_file = ROOT / "LICENSE"
    if not license_file.exists():
        raise AssertionError("LICENSE file is required before release")
    assert_contains(license_file, ["MIT License", "folder-book-reader contributors"])
    assert_contains(ROOT / "README.md", ["Python 3.10 or newer", "Python standard library", "[中文说明](README.zh-CN.md)"])
    assert_contains(ROOT / "README.zh-CN.md", ["Python 3.10 或更高版本", "Python 标准库", "[English README](README.md)"])

    (ROOT / "output").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "output") as temp_root:
        temp_path = Path(temp_root)
        source_dir = temp_path / "source"
        source_dir.mkdir()
        (source_dir / "001.md").write_text("# Temp\n\nbody\n", encoding="utf-8")

        dry_config = temp_path / "dry-run.config.md"
        dry_output = temp_path / "dry-reader.html"
        dry_config.write_text(
            "---\n"
            "title: Dry Run Test\n"
            "source_dir: ./source\n"
            "include: [\"*.md\"]\n"
            f"output: ./{dry_output.name}\n"
            "overwrite: true\n"
            "---\n",
            encoding="utf-8",
        )
        dry_result = run([sys.executable, "build_reader.py", str(dry_config), "--dry-run"])
        if dry_output.exists() or "Dry run: no files were written." not in dry_result.stdout:
            raise AssertionError("dry-run should report scope without writing output")

        overwrite_config = temp_path / "overwrite-false.config.md"
        overwrite_output = temp_path / "reader.html"
        overwrite_output.write_text("keep me", encoding="utf-8")
        overwrite_config.write_text(
            "---\n"
            "title: Overwrite Test\n"
            "source_dir: ./source\n"
            "include: [\"*.md\"]\n"
            "output: ./reader.html\n"
            "overwrite: false\n"
            "---\n",
            encoding="utf-8",
        )
        run([sys.executable, "build_reader.py", str(overwrite_config)])
        if overwrite_output.read_text(encoding="utf-8") != "keep me":
            raise AssertionError("overwrite: false should not replace an existing output file")
        if not list(temp_path.glob("reader_*.html")):
            raise AssertionError("overwrite: false should create a timestamped output file when target exists")

        missing_source_config = temp_path / "missing-source.config.md"
        missing_source_config.write_text("---\ntitle: Missing Source\n---\n", encoding="utf-8")
        missing_source = subprocess.run(
            [sys.executable, "build_reader.py", str(missing_source_config)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if missing_source.returncode != 2 or "Missing required field: source_dir" not in missing_source.stderr:
            raise AssertionError("missing source_dir should fail with a clear config error")

        empty_dir = temp_path / "empty"
        empty_dir.mkdir()
        empty_config = temp_path / "empty.config.md"
        empty_config.write_text(
            "---\n"
            "title: Empty Source\n"
            "source_dir: ./empty\n"
            "include: [\"*.md\", \"*.txt\", \"*.csv\"]\n"
            "---\n",
            encoding="utf-8",
        )
        empty_result = subprocess.run(
            [sys.executable, "build_reader.py", str(empty_config)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if empty_result.returncode != 2 or "No .md, .txt, or .csv files matched" not in empty_result.stderr:
            raise AssertionError("empty source directories should fail with a clear config error")

        no_match_dir = temp_path / "no-match"
        no_match_dir.mkdir()
        (no_match_dir / "data.json").write_text("{}", encoding="utf-8")
        no_match_config = temp_path / "no-match.config.md"
        no_match_config.write_text(
            "---\n"
            "title: No Match\n"
            "source_dir: ./no-match\n"
            "include: [\"*.md\", \"*.txt\", \"*.csv\"]\n"
            "---\n",
            encoding="utf-8",
        )
        no_match_result = subprocess.run(
            [sys.executable, "build_reader.py", str(no_match_config)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if no_match_result.returncode != 2 or "No .md, .txt, or .csv files matched" not in no_match_result.stderr:
            raise AssertionError("non-matching source directories should fail with a clear config error")

        nested_workspace = temp_path / "nested-workspace"
        nested_workspace.mkdir()
        nested_source = nested_workspace / "docs"
        nested_source.mkdir()
        (nested_source / "001.md").write_text("# Nested\n\nbody\n", encoding="utf-8")
        config_dir = nested_workspace / "config"
        config_dir.mkdir()
        workspace_root_config = config_dir / "reader.config.md"
        workspace_root_config.write_text(
            "---\n"
            "title: Workspace Root Test\n"
            "workspace_root: ..\n"
            "source_dir: ./docs\n"
            "include: [\"*.md\"]\n"
            "output: ./published/reader.html\n"
            "overwrite: true\n"
            "---\n",
            encoding="utf-8",
        )
        workspace_root_result = run([sys.executable, "build_reader.py", str(workspace_root_config)])
        workspace_root_output = nested_workspace / "published" / "reader.html"
        if not workspace_root_output.exists():
            raise AssertionError("workspace_root should let configs live below the project root")
        if "Workspace root:" not in workspace_root_result.stdout or "Config dir:" not in workspace_root_result.stdout:
            raise AssertionError("build scope should show both config dir and workspace root")

        escaped_config = config_dir / "escaped.config.md"
        escaped_config.write_text(
            "---\n"
            "title: Escaped Source\n"
            "workspace_root: ..\n"
            "source_dir: ../outside\n"
            "include: [\"*.md\"]\n"
            "---\n",
            encoding="utf-8",
        )
        escaped_result = subprocess.run(
            [sys.executable, "build_reader.py", str(escaped_config)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if escaped_result.returncode != 2 or "source_dir must stay inside workspace_root" not in escaped_result.stderr:
            raise AssertionError("source_dir must not escape workspace_root")

    run([sys.executable, "build_reader.py", "--dry-run"])
    run([sys.executable, "build_reader.py"])
    run([sys.executable, "build_reader.py", "workspace.config.md", "--dry-run"])
    run([sys.executable, "build_reader.py", "workspace.template.config.md", "--dry-run"])
    run([sys.executable, "build_reader.py", "config/workspace.template.config.md", "--dry-run"])
    run([sys.executable, "build_reader.py", "config/workspace.en.config.md"])
    run([sys.executable, "build_reader.py", "config/workspace.docs.config.md"])
    run([sys.executable, "build_reader.py", "config/workspace.docs.en.config.md"])
    run([sys.executable, "build_reader.py", "config/workspace.converted.config.md", "--dry-run"])
    run([sys.executable, "build_reader.py", "config/workspace.converted.config.md"])

    reader = ROOT / "output" / "reader.html"
    if not reader.exists():
        raise AssertionError("output/reader.html was not generated")
    assert_contains(
        reader,
        [
            "本地 Markdown/TXT/CSV 审阅阅读器 Demo",
            "floatingReviewButton",
            "leftPanelResizer",
            "rightPanelResizer",
            "toggleTocButton",
            "toggleReviewPanelButton",
            "toolbar-row",
            "syncToolbarHeight",
            "grid-column: 3; border-left: 0; border-top",
            "toolbar-filters",
            "left-collapsed",
            "right-collapsed",
            "审阅板",
            "复制 review.md",
            "zh-001-introduction.md",
            "zh-002-review-workflow.md",
            "zh-003-plain-text.txt",
            "004-review-table.csv",
            "csv-table",
            '<option value=".csv">.csv</option>',
            "csv-current-row-review",
            "data-block-type=\\\"csv-row\\\"",
            "function blockQuoteText(block)",
            "block.cells || []",
            "function csvSelectionMeta(selection)",
            "range.intersectsNode(cell)",
            "position_text",
            "const activeCsvRow = els.content.querySelector(\".csv-chapter .csv-row-active\")",
            "CSV · 5 行 · 5 列",
            "（未知链接，请回源文件查看）",
            "function move(delta)",
            "const chapters = visibleChapters();",
            "function scrollReaderToTop()",
            "overflow-anchor: none",
            "font-size: calc(var(--reader-font-size) * 1.65)",
            "resetLayoutButton",
            "Object.assign(state, layoutDefaults)",
            "updateReview(event.target.dataset.editComment, { comment: event.target.value }, false)",
            "state.leftCollapsed",
            "reviewBesideReader",
        ],
    )
    english_reader = ROOT / "output" / "reader.en.html"
    if not english_reader.exists():
        raise AssertionError("output/reader.en.html was not generated")
    assert_contains(
        english_reader,
        [
            "(Unknown link, check the source file)",
            "Local Markdown/TXT/CSV Review Reader Demo",
            'return Object.prototype.hasOwnProperty.call(labels, key) ? labels[key] : key;',
        ],
    )
    assert_not_contains(english_reader, ["paragraph 1 paragraph_suffix"])
    docs_reader = ROOT / "output" / "project-docs.html"
    if not docs_reader.exists():
        raise AssertionError("output/project-docs.html was not generated")
    assert_contains(
        docs_reader,
        [
            "README.zh-CN.md",
            "docs/01-project-status.zh-CN.md",
            "docs/01-project-status.en.md",
            "docs/04-user-manual.zh-CN.md",
            "docs/04-user-manual.en.md",
            "docs/05-security-notes.zh-CN.md",
            "docs/05-security-notes.en.md",
            "docs/06-developer-guide.zh-CN.md",
            "docs/06-developer-guide.en.md",
            "快捷键",
            "Keyboard Shortcuts",
            "预期工作流",
            "Expected Workflow",
            "嵌入到其他项目",
            "Embed in Another Project",
            "任意来源文件",
            "files from any source",
            "复制或下载 review.md",
            "Copy or download review.md",
            "来路不明",
            "unknown sources",
            "MIT License",
            "确认 MIT",
        ],
    )
    docs_reader_en = ROOT / "output" / "project-docs.en.html"
    if not docs_reader_en.exists():
        raise AssertionError("output/project-docs.en.html was not generated")
    assert_contains(
        docs_reader_en,
        [
            "Local Markdown/TXT Review Reader Docs",
            "README.zh-CN.md",
            "docs/05-security-notes.en.md",
            "docs/06-developer-guide.en.md",
            "Review Board",
            "Copy review.md",
        ],
    )

    fixture_source = ROOT / "examples" / "conversion-fixtures" / "source"
    converted = ROOT / "examples" / "conversion-fixtures" / "converted"
    run([sys.executable, "tools/convert_docs.py", str(fixture_source), "-o", str(converted)])

    source_docx = next(fixture_source.glob("*.docx"))
    with tempfile.TemporaryDirectory(dir=ROOT / "output") as temp_root:
        temp_path = Path(temp_root)
        nested_input = temp_path / "input"
        nested_output = temp_path / "converted"
        (nested_input / "a").mkdir(parents=True)
        (nested_input / "b").mkdir(parents=True)
        shutil.copyfile(source_docx, nested_input / "a" / "same.docx")
        shutil.copyfile(source_docx, nested_input / "b" / "same.docx")
        run([sys.executable, "tools/convert_docs.py", str(nested_input), "-o", str(nested_output), "--strict"])
        if not (nested_output / "a" / "same.docx.md").exists() or not (nested_output / "b" / "same.docx.md").exists():
            raise AssertionError("recursive converter should preserve relative folders for duplicate file names")

    converted_files = sorted(converted.glob("*.docx.md"))
    if len(converted_files) != 1:
        raise AssertionError(f"expected 1 converted docx file, found {len(converted_files)}")
    for item in converted_files:
        if item.stat().st_size == 0:
            raise AssertionError(f"converted file is empty: {item}")
    converted_text = converted_files[0].read_text(encoding="utf-8", errors="replace")
    if build_reader.extract_title(converted_files[0], converted_text) != "复杂排版转换器测试文档":
        raise AssertionError("converted DOCX title should not expose inline formatting markers")
    for needle in [
        "复杂排版转换器测试文档",
        "测试目的",
        "表格压力测试",
        "审阅路由样例",
        "文件：正文/round-02.md",
        "**复杂排版转换器测试文档**",
        "```text",
        "++下划线++",
        "==高亮文字==",
        "{{small}}",
        "data:image/png;base64,",
        '```docx-table',
        '"key_1"',
        "文件：正文/round-02.md<br>位置：第 6 段",
    ]:
        if needle not in converted_text:
            raise AssertionError(f"converted DOCX text missing expected content: {needle}")

    converted_reader = ROOT / "output" / "reader.converted.html"
    if not converted_reader.exists():
        raise AssertionError("output/reader.converted.html was not generated")
    assert_contains(
        converted_reader,
        [
            "转换器测试文档审阅 Demo",
            "complex_layout_review_reader_test.docx.md",
            "\\u003cstrong\\u003e复杂排版转换器测试文档\\u003c/strong\\u003e",
            "\\u003cu\\u003e下划线\\u003c/u\\u003e",
            "\\u003cmark\\u003e高亮文字\\u003c/mark\\u003e",
            "data:image/png;base64,",
            "docx-nested-table",
            "style=\\\"color:#C00000\\\"",
            "class=\\\"docx-small\\\"",
            "\\u003cbr\\u003e位置：第 6 段",
            "floatingReviewButton",
            "审阅板",
        ],
    )

    generated_demo_dir = ROOT / "examples" / "generated"
    generated_basic = generated_demo_dir / "basic-reader.demo.html"
    generated_english = generated_demo_dir / "basic-reader.en.demo.html"
    generated_docs = generated_demo_dir / "project-docs.demo.html"
    generated_docs_english = generated_demo_dir / "project-docs.en.demo.html"
    for demo_file in [generated_basic, generated_english, generated_docs, generated_docs_english]:
        if not demo_file.exists():
            raise AssertionError(f"selected generated demo is missing: {demo_file}")
        assert_not_contains(
            demo_file,
            [
                "C:\\Users",
                "AppData",
                "Desktop\\html-md",
                "review_2026",
                "112333",
                "12312312",
            ],
        )
    assert_contains(generated_basic, ["本地 Markdown/TXT/CSV 审阅阅读器 Demo", "zh-001-introduction.md", "004-review-table.csv"])
    assert_contains(
        generated_english,
        ["Local Markdown/TXT/CSV Review Reader Demo", "(Unknown link, check the source file)", "004-review-table.csv"],
    )
    assert_contains(
        generated_docs,
        ["README.zh-CN.md", "docs/05-security-notes.en.md", "docs/06-developer-guide.en.md"],
    )
    assert_contains(
        generated_docs_english,
        ["Local Markdown/TXT Review Reader Docs", "Review Board", "docs/06-developer-guide.en.md"],
    )

    for readme_path in [ROOT / "README.md", ROOT / "README.zh-CN.md", ROOT / "examples" / "generated" / "README.md"]:
        readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
        demo_paths = set(re.findall(r"examples/generated/[A-Za-z0-9._-]+\.html", readme_text))
        if not demo_paths:
            raise AssertionError(f"{readme_path} should list generated demo HTML files")
        missing_demo_paths = [path for path in sorted(demo_paths) if not (ROOT / path).exists()]
        if missing_demo_paths:
            raise AssertionError(f"{readme_path} lists missing generated demos: {missing_demo_paths}")
    assert_contains(
        ROOT / "index.html",
        [
            "./examples/generated/basic-reader.demo.html",
            "./examples/generated/basic-reader.en.demo.html",
            "./examples/generated/project-docs.demo.html",
            "./examples/generated/project-docs.en.demo.html",
        ],
    )
    run([sys.executable, "tests/html_quality_check.py"])

    print("smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
