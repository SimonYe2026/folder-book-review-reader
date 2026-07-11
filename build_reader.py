from __future__ import annotations

import argparse
import csv
import fnmatch
import html
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SUPPORTED_EXTENSIONS = {".md", ".txt", ".csv"}
VALID_ORDERS = {"natural", "natural_desc", "modified_desc"}
DISABLED_LINK_TEXT_ZH = "（未知链接，请回源文件查看）"
DISABLED_LINK_TEXT_EN = "(Unknown link, check the source file)"
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    "output",
    ".cache",
}

DEFAULT_LABELS_ZH = {
    "search_placeholder": "搜索标题、路径或正文",
    "file_type": "文件类型",
    "all": "全部",
    "clear": "清空",
    "sort_asc": "正序",
    "sort_desc": "倒序",
    "theme_dark": "深色",
    "theme_light": "浅色",
    "width_title": "阅读宽度",
    "width_narrow": "窄",
    "width_standard": "标准",
    "width_wide": "大屏",
    "width_full": "铺满",
    "reset_layout": "恢复默认",
    "toc": "目录",
    "bookmarks": "书签",
    "add_bookmark": "添加书签",
    "remove_bookmark": "移除书签",
    "delete_bookmark": "删除书签",
    "clear_bookmarks": "清空书签",
    "confirm_clear_bookmarks": "确认清空当前全部书签？",
    "bookmark_shortcut_title": "添加或移除当前位置书签（快捷键 B）",
    "empty_bookmarks": "还没有书签。阅读时可添加当前位置。",
    "review_panel": "审阅板",
    "previous": "上一篇",
    "next": "下一篇",
    "copy_review": "复制 review.md",
    "download": "下载",
    "delete": "删除",
    "copy_code": "复制代码",
    "copied": "已复制",
    "empty_reviews": "还没有批复。选中文本或点击段落旁的批复按钮。",
    "review": "批复",
    "review_current_row": "批复当前行",
    "add_review": "加入批复",
    "quote_original": "引用原文",
    "action": "动作",
    "target": "目标",
    "review_instruction": "用户批复",
    "review_placeholder": "写下要交给 AI 或后续流程的处理说明。",
    "cancel": "取消",
    "no_files": "没有文件",
    "items": "条",
    "paragraph": "第 ? 段",
    "paragraph_prefix": "第",
    "paragraph_suffix": "段",
    "context_blocks": "附近内容块",
    "context_heading": "附近上下文",
    "review_scope": "审阅范围",
    "review_scope_selection": "选中文本（精确）",
    "review_scope_block": "内容块（精确）",
    "review_scope_viewport": "阅读视口（核心引用仅用于定位）",
    "heading_prefix": "标题",
    "heading_suffix": "",
    "code_block_prefix": "代码块",
    "code_block_suffix": "",
    "table_prefix": "表格",
    "table_suffix": "",
    "row_prefix": "第",
    "row_suffix": "行",
    "column_prefix": "第",
    "column_suffix": "列",
    "csv_rows": "行",
    "csv_columns": "列",
    "position_prefix": "当前筛选结果第",
    "current_prefix": "当前",
    "filtered_prefix": "筛选",
    "reading_minutes": "分钟",
    "words": "字",
    "confirm_clear_reviews": "确认清空当前全部批复？",
    "left_resizer_title": "拖拽调整目录宽度",
    "right_resizer_title": "拖拽调整审阅板宽度",
    "floating_review_title": "加入批复（可拖拽，快捷键 R）",
    "hide_toc": "收起目录",
    "show_toc": "展开目录",
    "hide_review_panel": "收起审阅板",
    "show_review_panel": "展开审阅板",
    "generated_at": "生成时间",
    "review_count": "批复数量",
    "grouping": "分组方式",
    "group_by_file": "按文件",
    "file_label": "文件",
    "path_label": "路径",
    "reviews_label": "批复数",
    "review_label": "批复",
    "position_label": "位置",
    "time_label": "时间",
    "quote_heading": "引用原文",
    "instruction_heading": "用户批复",
    "empty_value": "空",
}

DEFAULT_LABELS_EN = {
    "search_placeholder": "Search title, path, or content",
    "file_type": "File type",
    "all": "All",
    "clear": "Clear",
    "sort_asc": "Ascending",
    "sort_desc": "Descending",
    "theme_dark": "Dark",
    "theme_light": "Light",
    "width_title": "Reading width",
    "width_narrow": "Narrow",
    "width_standard": "Standard",
    "width_wide": "Wide",
    "width_full": "Full",
    "reset_layout": "Reset layout",
    "toc": "Contents",
    "bookmarks": "Bookmarks",
    "add_bookmark": "Add Bookmark",
    "remove_bookmark": "Remove Bookmark",
    "delete_bookmark": "Delete bookmark",
    "clear_bookmarks": "Clear bookmarks",
    "confirm_clear_bookmarks": "Clear all current bookmarks?",
    "bookmark_shortcut_title": "Add or remove the current-position bookmark (shortcut B)",
    "empty_bookmarks": "No bookmarks yet. Add one from the current reading position.",
    "review_panel": "Review Board",
    "previous": "Previous",
    "next": "Next",
    "copy_review": "Copy review.md",
    "download": "Download",
    "delete": "Delete",
    "copy_code": "Copy code",
    "copied": "Copied",
    "empty_reviews": "No review notes yet. Select text or use a paragraph review button.",
    "review": "Review",
    "review_current_row": "Review Current Row",
    "add_review": "Add Review",
    "quote_original": "Quote",
    "action": "Action",
    "target": "Target",
    "review_instruction": "Instruction",
    "review_placeholder": "Write the instruction you want to send to AI or use later.",
    "cancel": "Cancel",
    "no_files": "No files",
    "items": "items",
    "paragraph": "paragraph",
    "paragraph_prefix": "paragraph",
    "paragraph_suffix": "",
    "context_blocks": "Nearby blocks",
    "context_heading": "Nearby context",
    "review_scope": "Review scope",
    "review_scope_selection": "Selected text (precise)",
    "review_scope_block": "Content block (precise)",
    "review_scope_viewport": "Reading viewport (the quote is an anchor only)",
    "heading_prefix": "heading",
    "heading_suffix": "",
    "code_block_prefix": "code block",
    "code_block_suffix": "",
    "table_prefix": "table",
    "table_suffix": "",
    "row_prefix": "row",
    "row_suffix": "",
    "column_prefix": "column",
    "column_suffix": "",
    "csv_rows": "rows",
    "csv_columns": "columns",
    "position_prefix": "Filtered result",
    "current_prefix": "Current",
    "filtered_prefix": "Filtered",
    "reading_minutes": "min",
    "words": "words",
    "confirm_clear_reviews": "Clear all review notes?",
    "left_resizer_title": "Drag to resize contents panel",
    "right_resizer_title": "Drag to resize review panel",
    "floating_review_title": "Add review (drag to move, shortcut R)",
    "hide_toc": "Hide contents",
    "show_toc": "Show contents",
    "hide_review_panel": "Hide review board",
    "show_review_panel": "Show review board",
    "generated_at": "Generated at",
    "review_count": "Review count",
    "grouping": "Grouping",
    "group_by_file": "by file",
    "file_label": "File",
    "path_label": "Path",
    "reviews_label": "Reviews",
    "review_label": "Review",
    "position_label": "Position",
    "time_label": "Time",
    "quote_heading": "Quote",
    "instruction_heading": "Instruction",
    "empty_value": "empty",
}

DEFAULT_LABELS_ZH["disabled_link"] = DISABLED_LINK_TEXT_ZH
DEFAULT_LABELS_EN["disabled_link"] = DISABLED_LINK_TEXT_EN

LABEL_SETS = {
    "zh": DEFAULT_LABELS_ZH,
    "zh-cn": DEFAULT_LABELS_ZH,
    "en": DEFAULT_LABELS_EN,
}


class ConfigError(Exception):
    pass


def strip_inline_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            continue
        if char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value


def split_inline_items(value: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    for char in value:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            current.append(char)
            escaped = True
            continue
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            current.append(char)
            quote = char
            continue
        if char == ",":
            items.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        items.append(tail)
    return items


def parse_scalar(value: str) -> Any:
    value = strip_inline_comment(value)
    value = value.strip()
    if value == "":
        return ""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none"}:
        return None
    if value in {"[]", "[ ]"}:
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item) for item in split_inline_items(inner)]
    if value in {"{}", "{ }"}:
        return {}
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def count_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def parse_block(lines: list[str], start: int, indent: int) -> tuple[Any, int]:
    items: list[Any] = []
    mapping: dict[str, Any] = {}
    mode: str | None = None
    index = start

    while index < len(lines):
        raw = lines[index]
        if not raw.strip() or raw.lstrip().startswith("#"):
            index += 1
            continue
        current_indent = count_indent(raw)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ConfigError(f"Unexpected indentation: {raw}")

        stripped = raw.strip()
        if stripped.startswith("- "):
            if mode == "map":
                raise ConfigError(f"Cannot mix list and mapping at line: {raw}")
            mode = "list"
            value = stripped[2:].strip()
            if value:
                items.append(parse_scalar(value))
                index += 1
            else:
                child, index = parse_block(lines, index + 1, indent + 2)
                items.append(child)
            continue

        if ":" not in stripped:
            raise ConfigError(f"Invalid config line: {raw}")
        if mode == "list":
            raise ConfigError(f"Cannot mix list and mapping at line: {raw}")
        mode = "map"
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            mapping[key] = parse_scalar(value)
            index += 1
        else:
            child, index = parse_block(lines, index + 1, indent + 2)
            mapping[key] = child

    if mode == "list":
        return items, index
    return mapping, index


def parse_simple_yaml(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    data, index = parse_block(lines, 0, 0)
    while index < len(lines):
        if lines[index].strip():
            raise ConfigError(f"Invalid trailing config line: {lines[index]}")
        index += 1
    if not isinstance(data, dict):
        raise ConfigError("Config frontmatter must be a mapping.")
    return data


def load_config(config_path: Path) -> dict[str, Any]:
    raw = config_path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ConfigError("Config file must start with YAML frontmatter.")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise ConfigError("Config file is missing a closing frontmatter marker.")

    config = parse_simple_yaml(parts[1])
    if not config.get("source_dir"):
        raise ConfigError("Missing required field: source_dir")

    config.setdefault("title", "Local Markdown/TXT/CSV Review Reader")
    config.setdefault("include", ["*.md", "*.txt", "*.csv"])
    config.setdefault("exclude", [])
    config.setdefault("order", "natural")
    config.setdefault("workspace_root", ".")
    config.setdefault("recursive", False)
    config.setdefault("flatten", True)
    config.setdefault("output", "./output/reader.html")
    config.setdefault("overwrite", True)
    config.setdefault("display", {})
    config.setdefault("features", {})
    config.setdefault("review", {})
    config.setdefault("tables", {})
    config.setdefault("stats", {})

    if not isinstance(config["include"], list):
        raise ConfigError("include must be a list.")
    if not isinstance(config["exclude"], list):
        raise ConfigError("exclude must be a list.")
    if config["order"] not in VALID_ORDERS:
        raise ConfigError(f"Unsupported order: {config['order']}")

    review = dict(config.get("review") or {})
    review.setdefault("enabled", True)
    review.setdefault("actions", ["修改", "总结", "提取", "登记"])
    review.setdefault("targets", ["原文段落", "审阅队列", "笔记", "待办清单"])
    review.setdefault("shortcut", "r")
    config["review"] = review

    config.setdefault("locale", "zh-CN")

    text = dict(config.get("text") or {})
    text.setdefault("paragraph_mode", "line")
    if text["paragraph_mode"] not in {"line", "blank_line"}:
        raise ConfigError("text.paragraph_mode must be 'line' or 'blank_line'")
    config["text"] = text

    locale_key = str(config.get("locale") or "zh-CN").lower()
    labels = dict(LABEL_SETS.get(locale_key, DEFAULT_LABELS_ZH))
    labels.update(dict(config.get("labels") or {}))
    config["labels"] = labels

    tables = dict(config.get("tables") or {})
    tables.setdefault("enabled", True)
    tables.setdefault("sticky_header", True)
    tables.setdefault("horizontal_scroll", True)
    tables.setdefault("copy_button", False)
    config["tables"] = tables

    stats = dict(config.get("stats") or {})
    stats.setdefault("enabled", False)
    config["stats"] = stats

    return config


def natural_key(value: str) -> list[Any]:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def normalize_patterns(values: list[Any]) -> list[str]:
    return [str(item).replace("\\", "/") for item in values]


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_workspace_root(config_path: Path, config: dict[str, Any]) -> Path:
    raw_root = str(config.get("workspace_root") or ".")
    root_path = Path(raw_root)
    if not root_path.is_absolute():
        root_path = config_path.parent / root_path
    workspace_root = root_path.resolve()
    if not workspace_root.exists():
        raise ConfigError(f"workspace_root does not exist: {workspace_root}")
    if not workspace_root.is_dir():
        raise ConfigError(f"workspace_root is not a directory: {workspace_root}")
    return workspace_root


def resolve_inside_workspace(workspace_root: Path, value: str, field_name: str) -> Path:
    raw_path = Path(value)
    if not raw_path.is_absolute():
        raw_path = workspace_root / raw_path
    resolved = raw_path.resolve()
    if not is_under(resolved, workspace_root):
        raise ConfigError(f"{field_name} must stay inside workspace_root: {resolved}")
    return resolved


def matches_any(path: Path, relative_path: str, patterns: list[str]) -> bool:
    return any(
        fnmatch.fnmatch(path.name, pattern)
        or fnmatch.fnmatch(relative_path, pattern)
        or fnmatch.fnmatch(relative_path, pattern.rstrip("/") + "/*")
        for pattern in patterns
    )


def is_included(path: Path, relative_path: str, include: list[str], exclude: list[str]) -> bool:
    included = matches_any(path, relative_path, include)
    excluded = matches_any(path, relative_path, exclude)
    return included and not excluded and path.suffix.lower() in SUPPORTED_EXTENSIONS


def discover_files(workspace_root: Path, config: dict[str, Any]) -> tuple[list[Path], Path]:
    source_dir = resolve_inside_workspace(workspace_root, str(config["source_dir"]), "source_dir")
    if not source_dir.exists():
        raise ConfigError(f"source_dir does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise ConfigError(f"source_dir is not a directory: {source_dir}")

    include = normalize_patterns(config.get("include", ["*.md", "*.txt"]))
    exclude = normalize_patterns(config.get("exclude", []))
    recursive = bool(config.get("recursive", False))
    files: list[Path] = []

    if recursive:
        for path in source_dir.rglob("*"):
            if any(part in DEFAULT_EXCLUDED_DIRS for part in path.relative_to(source_dir).parts[:-1]):
                continue
            if path.is_file():
                relative_path = path.relative_to(source_dir).as_posix()
                if is_included(path, relative_path, include, exclude):
                    files.append(path)
    else:
        for path in source_dir.iterdir():
            if path.is_file():
                relative_path = path.relative_to(source_dir).as_posix()
                if is_included(path, relative_path, include, exclude):
                    files.append(path)

    if config["order"] == "modified_desc":
        files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    else:
        files.sort(key=lambda item: natural_key(item.relative_to(source_dir).as_posix()))
        if config["order"] == "natural_desc":
            files.reverse()

    if not files:
        raise ConfigError("No .md, .txt, or .csv files matched the configured include/exclude rules.")
    return files, source_dir


def extract_title(path: Path, text: str) -> str:
    if path.suffix.lower() == ".csv":
        return path.stem

    def plain_title(value: str) -> str:
        value = re.sub(r"\{\{(?:color:[0-9A-Fa-f]{6}|small)\}\}|\{\{/(?:color|small)\}\}", "", value)
        value = re.sub(r"\*\*|\*|\+\+|==|`", "", value)
        return value.strip()

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if path.suffix.lower() == ".md":
            heading = re.match(r"^#{1,6}\s+(.+)$", stripped)
            if heading:
                return plain_title(heading.group(1))
        return plain_title(stripped)[:80]
    return path.stem


def split_markdown_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        return parse_simple_yaml(parts[1]), parts[2].lstrip()
    except ConfigError:
        return {}, text


def word_count(text: str) -> int:
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    latin_words = re.findall(r"[A-Za-z0-9_]+(?:['-][A-Za-z0-9_]+)?", text)
    return len(chinese_chars) + len(latin_words)


def text_from_csv_rows(rows: list[list[str]]) -> str:
    return "\n".join("\t".join(str(cell) for cell in row) for row in rows)


def strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def safe_json_dumps(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def inline_markdown(value: str, labels: dict[str, str] | None = None) -> str:
    labels = labels or DEFAULT_LABELS_ZH
    disabled_link_text = str(labels.get("disabled_link", DISABLED_LINK_TEXT_ZH))
    escaped = html.escape(value)
    protected: list[str] = []

    def protect(rendered: str) -> str:
        token = f"@@INLINEPROTECTED{len(protected)}@@"
        protected.append(rendered)
        return token

    def has_url_scheme(url: str) -> bool:
        return bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", html.unescape(url).strip()))

    def safe_image_url(url: str) -> str | None:
        raw_url = html.unescape(url).strip()
        lowered = raw_url.lower()
        if re.match(r"^data:image/(?:png|jpe?g|gif|webp);base64,[a-z0-9+/=\s]+$", lowered):
            return html.escape(raw_url, quote=True)
        if has_url_scheme(raw_url):
            return None
        return html.escape(raw_url, quote=True)

    def render_image(match: re.Match[str]) -> str:
        src = safe_image_url(match.group(2))
        alt = match.group(1)
        if not src:
            return protect(f'<span class="disabled-image">[{alt}]</span>')
        return protect(f'<img src="{src}" alt="{alt}">')

    def render_disabled_link(match: re.Match[str]) -> str:
        return protect(f'<span class="disabled-link">{html.escape(disabled_link_text)}</span>')

    escaped = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        render_image,
        escaped,
    )
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        render_disabled_link,
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", lambda match: protect(f"<code>{match.group(1)}</code>"), escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"\+\+(.+?)\+\+", r"<u>\1</u>", escaped)
    escaped = re.sub(r"==(.+?)==", r"<mark>\1</mark>", escaped)
    escaped = re.sub(r"\{\{small\}\}(.+?)\{\{/small\}\}", r'<span class="docx-small">\1</span>', escaped)
    escaped = re.sub(
        r"\{\{color:([0-9A-Fa-f]{6})\}\}(.+?)\{\{/color\}\}",
        r'<span style="color:#\1">\2</span>',
        escaped,
    )
    for index, rendered in enumerate(protected):
        escaped = escaped.replace(f"@@INLINEPROTECTED{index}@@", rendered)
    return escaped


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_table(
    lines: list[str],
    table_index: int,
    labels: dict[str, str] | None = None,
    block_index: int | None = None,
) -> str:
    header = split_table_row(lines[0])
    rows = [split_table_row(line) for line in lines[2:]]
    columns = len(header)
    def table_cell(value: str) -> str:
        return inline_markdown(value, labels).replace("&lt;br&gt;", "<br>")

    head_html = "".join(f"<th>{table_cell(cell)}</th>" for cell in header)
    body_html = []
    for row in rows:
        padded = row + [""] * max(0, columns - len(row))
        body_html.append("<tr>" + "".join(f"<td>{table_cell(cell)}</td>" for cell in padded[:columns]) + "</tr>")
    block_attributes = ""
    if block_index is not None:
        block_attributes = f' data-block-index="{block_index}" data-block-type="table"'
    return (
        f'<div class="table-wrap" data-table-index="{table_index}"{block_attributes}>'
        f'<table><thead><tr>{head_html}</tr></thead><tbody>{"".join(body_html)}</tbody></table>'
        "</div>"
    )


def render_docx_table(
    data: dict[str, Any],
    table_index: int,
    labels: dict[str, str] | None = None,
    nested: bool = False,
    block_index: int | None = None,
) -> str:
    if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
        raise ValueError("docx-table data must contain a rows list")
    rows_html: list[str] = []
    for row in data.get("rows", []):
        if not isinstance(row, list):
            raise ValueError("docx-table row must be a list")
        cells_html: list[str] = []
        for cell in row:
            if not isinstance(cell, dict):
                raise ValueError("docx-table cell must be a mapping")
            text_values = cell.get("text", [])
            nested_tables = cell.get("tables", [])
            if not isinstance(text_values, list) or not isinstance(nested_tables, list):
                raise ValueError("docx-table cell text and tables must be lists")
            parts = [inline_markdown(str(value), labels) for value in cell.get("text", [])]
            parts.extend(render_docx_table(table, table_index, labels, nested=True) for table in nested_tables)
            cells_html.append(f'<td>{"<br>".join(parts)}</td>')
        rows_html.append(f'<tr>{"".join(cells_html)}</tr>')
    table_class = ' class="docx-nested-table"' if nested else ' class="docx-structured-table"'
    table_html = f'<table{table_class}><tbody>{"".join(rows_html)}</tbody></table>'
    if nested:
        return table_html
    block_attributes = ""
    if block_index is not None:
        block_attributes = f' data-block-index="{block_index}" data-block-type="docx-table"'
    return f'<div class="table-wrap docx-table-wrap" data-table-index="{table_index}"{block_attributes}>{table_html}</div>'


def csv_cell(value: str) -> str:
    return html.escape(value).replace("=", "&#61;")


def render_markdown_basic(text: str, labels: dict[str, str] | None = None) -> str:
    labels = labels or DEFAULT_LABELS_ZH
    copy_code_label = html.escape(str(labels.get("copy_code", "Copy code")))
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    in_code = False
    code_lines: list[str] = []
    code_lang = ""
    block_index = 1
    table_index = 1
    lines = text.splitlines()
    index = 0

    def next_block_index() -> int:
        nonlocal block_index
        value = block_index
        block_index += 1
        return value

    def flush_paragraph() -> None:
        if paragraph:
            idx = next_block_index()
            body = inline_markdown(" ".join(paragraph), labels)
            blocks.append(f'<p data-block-index="{idx}" data-block-type="paragraph">{body}</p>')
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            items = []
            for item in list_items:
                idx = next_block_index()
                items.append(f'<li data-block-index="{idx}" data-block-type="list-item">{inline_markdown(item, labels)}</li>')
            blocks.append(f"<ul>{''.join(items)}</ul>")
            list_items.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                if code_lang == "docx-table":
                    idx = next_block_index()
                    try:
                        blocks.append(render_docx_table(json.loads("\n".join(code_lines)), table_index, labels, block_index=idx))
                        table_index += 1
                    except (json.JSONDecodeError, TypeError, ValueError):
                        code = html.escape("\n".join(code_lines))
                        blocks.append(
                            f'<div class="code-block" data-block-index="{idx}" data-block-type="code-block">'
                            f"<pre><code>{code}</code></pre></div>"
                        )
                else:
                    idx = next_block_index()
                    language = html.escape(code_lang)
                    code = html.escape("\n".join(code_lines))
                    blocks.append(
                        f'<div class="code-block" data-block-index="{idx}" data-block-type="code-block" data-language="{language}">'
                        f'<div class="code-tools"><span>{language or "text"}</span><button type="button" class="copy-code">{copy_code_label}</button></div>'
                        f"<pre><code>{code}</code></pre></div>"
                    )
                code_lines.clear()
                code_lang = ""
                in_code = False
            else:
                flush_paragraph()
                flush_list()
                in_code = True
                code_lang = stripped[3:].strip()
            index += 1
            continue

        if in_code:
            code_lines.append(line)
            index += 1
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            index += 1
            continue

        if "|" in stripped and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            flush_paragraph()
            flush_list()
            table_lines = [line, lines[index + 1]]
            index += 2
            while index < len(lines) and "|" in lines[index].strip() and lines[index].strip():
                table_lines.append(lines[index])
                index += 1
            blocks.append(render_table(table_lines, table_index, labels, block_index=next_block_index()))
            table_index += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            idx = next_block_index()
            blocks.append(
                f'<h{level} data-block-index="{idx}" data-block-type="heading">'
                f"{inline_markdown(heading.group(2), labels)}</h{level}>"
            )
            index += 1
            continue

        bullet = re.match(r"^[-*+]\s+(.+)$", stripped)
        if bullet:
            flush_paragraph()
            list_items.append(bullet.group(1))
            index += 1
            continue

        quote = re.match(r"^>\s?(.+)$", stripped)
        if quote:
            flush_paragraph()
            flush_list()
            idx = next_block_index()
            blocks.append(
                f'<blockquote data-block-index="{idx}" data-block-type="quote">{inline_markdown(quote.group(1), labels)}</blockquote>'
            )
            index += 1
            continue

        paragraph.append(stripped)
        index += 1

    if in_code:
        idx = next_block_index()
        language = html.escape(code_lang)
        code = html.escape("\n".join(code_lines))
        blocks.append(
            f'<div class="code-block" data-block-index="{idx}" data-block-type="code-block" data-language="{language}">'
            f'<div class="code-tools"><span>{language or "text"}</span><button type="button" class="copy-code">{copy_code_label}</button></div>'
            f"<pre><code>{code}</code></pre></div>"
        )
    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def render_text_basic(text: str, paragraph_mode: str = "line") -> str:
    blocks: list[str] = []
    block_index = 1

    def append_paragraph(value: str) -> None:
        nonlocal block_index
        stripped = value.strip()
        if not stripped:
            return
        body = html.escape(stripped)
        blocks.append(f'<p data-block-index="{block_index}" data-block-type="paragraph">{body}</p>')
        block_index += 1

    if paragraph_mode == "blank_line":
        paragraph: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                paragraph.append(stripped)
            elif paragraph:
                append_paragraph(" ".join(paragraph))
                paragraph.clear()
        if paragraph:
            append_paragraph(" ".join(paragraph))
    else:
        for line in text.splitlines():
            append_paragraph(line)

    return "\n".join(blocks)


def parse_csv_rows(text: str) -> list[list[str]]:
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample)
    except csv.Error:
        dialect = csv.excel
    return [[str(cell) for cell in row] for row in csv.reader(io.StringIO(text), dialect)]


def render_csv_basic(text: str, labels: dict[str, str] | None = None) -> str:
    labels = labels or DEFAULT_LABELS_ZH
    rows = parse_csv_rows(text)
    column_count = max((len(row) for row in rows), default=0)
    data_rows = rows[1:] if rows else []
    row_count = len(data_rows)
    review_label = html.escape(str(labels.get("review_current_row", "Review Current Row")))
    rows_label = html.escape(str(labels.get("csv_rows", "rows")))
    columns_label = html.escape(str(labels.get("csv_columns", "columns")))

    summary = (
        f'<div class="csv-summary"><span>CSV · {row_count} {rows_label} · '
        f'{column_count} {columns_label}</span>'
        f'<button type="button" class="btn csv-current-row-review">{review_label}</button></div>'
    )
    if not rows:
        return f'<section class="csv-chapter">{summary}</section>'

    header = rows[0] + [""] * max(0, column_count - len(rows[0]))
    head_cells = [f"<th>{csv_cell(cell)}</th>" for cell in header[:column_count]]

    body_rows: list[str] = []
    for index, row in enumerate(data_rows, start=1):
        padded = row + [""] * max(0, column_count - len(row))
        data_cells = "".join(f"<td>{csv_cell(cell)}</td>" for cell in padded[:column_count])
        body_rows.append(
            f'<tr data-block-index="{index}" data-block-type="csv-row">{data_cells}</tr>'
        )

    table = (
        '<div class="table-wrap csv-table-wrap">'
        '<table class="csv-table">'
        f'<thead><tr>{"".join(head_cells)}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        "</table>"
        "</div>"
    )
    return f'<section class="csv-chapter">{summary}{table}</section>'


def render_content(path: Path, text: str, config: dict[str, Any]) -> str:
    if path.suffix.lower() == ".md":
        return render_markdown_basic(text, labels=dict(config.get("labels") or {}))
    if path.suffix.lower() == ".csv":
        return render_csv_basic(text, labels=dict(config.get("labels") or {}))
    paragraph_mode = str((config.get("text") or {}).get("paragraph_mode") or "line")
    return render_text_basic(text, paragraph_mode=paragraph_mode)


def derive_prefix(stem: str) -> str:
    match = re.match(r"^(.+?)(?:[_\s-][^\d].*)?$", stem)
    return match.group(1) if match else stem


def build_chapters(workspace_root: Path, source_dir: Path, files: list[Path], config: dict[str, Any]) -> list[dict[str, Any]]:
    chapters = []
    for index, path in enumerate(files, start=1):
        raw_text = path.read_text(encoding="utf-8-sig")
        frontmatter: dict[str, Any] = {}
        text = raw_text
        if path.suffix.lower() == ".md":
            frontmatter, text = split_markdown_frontmatter(raw_text)
        stat = path.stat()
        relative_to_source = path.relative_to(source_dir)
        relative_path = relative_to_source.as_posix()
        path_segments = list(relative_to_source.parts[:-1])
        content_html = render_content(path, text, config)
        title = str(frontmatter.get("title") or extract_title(path, text))
        chapter: dict[str, Any] = {
            "id": f"chapter-{index:03d}",
            "title": title,
            "file_name": path.name,
            "relative_path": relative_path,
            "path": path.relative_to(workspace_root).as_posix(),
            "folder": "/".join(path_segments),
            "path_segments": path_segments,
            "prefix": derive_prefix(path.stem),
            "ext": path.suffix.lower(),
            "word_count": word_count(text),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "content_html": content_html,
            "content_text": strip_html(text),
        }
        if path.suffix.lower() == ".csv":
            csv_rows = parse_csv_rows(text)
            csv_text = text_from_csv_rows(csv_rows)
            chapter.update(
                {
                    "row_count": max(0, len(csv_rows) - 1),
                    "column_count": max((len(row) for row in csv_rows), default=0),
                    "word_count": word_count(csv_text),
                    "content_text": csv_text,
                }
            )
        chapters.append(chapter)
    return chapters


def output_path_for(workspace_root: Path, config: dict[str, Any], force_overwrite: bool = False) -> Path:
    output_path = resolve_inside_workspace(workspace_root, str(config.get("output", "./output/reader.html")), "output")
    overwrite = bool(config.get("overwrite", True)) or force_overwrite
    if output_path.exists() and not overwrite:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")
    return output_path


def summarize_build(
    config_path: Path,
    workspace_root: Path,
    source_dir: Path,
    files: list[Path],
    output_path: Path,
    config: dict[str, Any],
) -> str:
    relative_files = [path.relative_to(source_dir).as_posix() for path in files]
    lines = [
        "Build scope:",
        f"- Config: {config_path}",
        f"- Config dir: {config_path.parent}",
        f"- Workspace root: {workspace_root}",
        f"- Source dir: {source_dir}",
        f"- Recursive: {bool(config.get('recursive', False))}",
        f"- Matched files: {len(files)}",
        f"- Output: {output_path}",
        f"- Include: {', '.join(normalize_patterns(config.get('include', [])))}",
        f"- Exclude: {', '.join(normalize_patterns(config.get('exclude', [])) or ['(none)'])}",
        f"- Default excluded dirs: {', '.join(sorted(DEFAULT_EXCLUDED_DIRS))}",
        "- Files:",
    ]
    lines.extend(f"  - {item}" for item in relative_files)
    return "\n".join(lines)


def html_document(data: dict[str, Any], app_config: dict[str, Any]) -> str:
    payload = safe_json_dumps(data)
    config_payload = safe_json_dumps(app_config)
    title = html.escape(str(data["title"]))
    locale_raw = str(app_config.get("locale") or "zh-CN")
    locale = html.escape(locale_raw)
    labels = dict(LABEL_SETS.get(locale_raw.lower(), DEFAULT_LABELS_ZH))
    labels.update(dict(app_config.get("labels") or {}))

    def label(key: str) -> str:
        return html.escape(str(labels.get(key, DEFAULT_LABELS_ZH.get(key, key))))

    return f"""<!doctype html>
<html lang="{locale}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f2ec;
      --panel: #fffefa;
      --panel-2: #f0ede7;
      --text: #25211b;
      --muted: #70685d;
      --line: #ded6ca;
      --accent: #2f6f73;
      --accent-2: #775a2d;
      --accent-soft: #dfeeed;
      --danger: #a33a32;
      --shadow: 0 16px 36px rgba(48, 39, 28, 0.12);
      --reader-font-size: 18px;
      --reader-width: 100%;
      --left-panel-width: 300px;
      --right-panel-width: 360px;
      --toolbar-height: 104px;
    }}
    body.dark {{
      color-scheme: dark;
      --bg: #171b1c;
      --panel: #222829;
      --panel-2: #2b3233;
      --text: #eee9df;
      --muted: #b8afa2;
      --line: #3d4546;
      --accent: #8ac7be;
      --accent-2: #d4b06c;
      --accent-soft: #243c3d;
      --danger: #f08d86;
      --shadow: 0 16px 36px rgba(0, 0, 0, 0.28);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
      line-height: 1.7;
    }}
    button, input, select, textarea {{ font: inherit; color: inherit; }}
    button:disabled {{ opacity: .45; cursor: not-allowed; }}
    .app {{ min-height: 100vh; display: grid; grid-template-rows: auto 1fr auto; }}
    .toolbar {{
      position: sticky; top: 0; z-index: 5;
      display: grid; grid-template-columns: 1fr; gap: 8px;
      padding: 10px 14px;
      background: color-mix(in srgb, var(--panel) 94%, transparent);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(10px);
    }}
    .toolbar-row {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; min-width: 0; }}
    .book-title {{ min-width: 0; font-size: 18px; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .controls {{ display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; align-items: center; }}
    .toolbar-main {{ justify-content: flex-end; flex: 0 0 auto; }}
    .toolbar-filters {{ justify-content: flex-start; }}
    .search, .select, .field, textarea {{
      border: 1px solid var(--line); background: var(--panel); border-radius: 6px; padding: 8px 10px;
    }}
    .search {{ width: min(320px, 32vw); min-width: 160px; }}
    .btn {{
      min-height: 38px; border: 1px solid var(--line); background: var(--panel); border-radius: 6px;
      padding: 7px 10px; cursor: pointer;
    }}
    .btn,
    .toolbar,
    .side-head,
    .chapter-nav,
    .fixed-nav,
    .csv-summary,
    .code-tools,
    .review-item header,
    .review-grid,
    .dialog-actions,
    .floating-review {{ user-select: none; -webkit-user-select: none; }}
    .btn:hover, .chapter-item:hover {{ border-color: var(--accent); }}
    .btn.primary {{ background: var(--accent); border-color: var(--accent); color: white; }}
    .btn.danger {{ border-color: color-mix(in srgb, var(--danger) 45%, var(--line)); color: var(--danger); }}
    .layout {{ display: grid; grid-template-columns: var(--left-panel-width) 0 minmax(0, 1fr) 0 var(--right-panel-width); min-height: 0; }}
    .layout.left-collapsed {{ grid-template-columns: 0 0 minmax(0, 1fr) 0 var(--right-panel-width); }}
    .layout.right-collapsed {{ grid-template-columns: var(--left-panel-width) 0 minmax(0, 1fr) 0 0; }}
    .layout.left-collapsed.right-collapsed {{ grid-template-columns: 0 0 minmax(0, 1fr) 0 0; }}
    .layout.left-collapsed .sidebar,
    .layout.left-collapsed .panel-resizer.left,
    .layout.right-collapsed .review-panel,
    .layout.right-collapsed .panel-resizer.right {{ display: none; }}
    .sidebar {{ grid-column: 1; }}
    .panel-resizer.left {{ grid-column: 2; }}
    .reader-shell {{ grid-column: 3; }}
    .panel-resizer.right {{ grid-column: 4; }}
    .review-panel {{ grid-column: 5; }}
    .sidebar, .review-panel {{
      position: sticky; top: var(--toolbar-height); height: calc(100vh - var(--toolbar-height)); overflow: auto; background: var(--panel); padding: 12px;
    }}
    .sidebar {{ border-right: 1px solid var(--line); }}
    .review-panel {{ border-left: 1px solid var(--line); }}
    .panel-resizer {{
      position: sticky; top: var(--toolbar-height); height: calc(100vh - var(--toolbar-height)); width: 9px; z-index: 3;
      align-self: start; cursor: col-resize; background: transparent;
    }}
    .panel-resizer::before {{
      content: ""; display: block; width: 1px; height: 100%; margin: 0 auto; background: var(--line);
    }}
    .panel-resizer:hover::before,
    .panel-resizer.dragging::before {{ width: 3px; background: var(--accent); }}
    .panel-resizer.left {{ margin-left: -5px; margin-right: -4px; }}
    .panel-resizer.right {{ margin-left: -4px; margin-right: -5px; }}
    body.resizing-panels {{ cursor: col-resize; user-select: none; }}
    .side-head {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px; }}
    .panel-tabs {{ display: flex; align-items: center; gap: 4px; min-width: 0; }}
    .panel-tab {{ min-height: 30px; padding: 3px 8px; font-size: 12px; white-space: nowrap; }}
    .panel-tab.active {{ border-color: var(--accent); background: var(--accent-soft); color: var(--text); }}
    .small-text {{ color: var(--muted); font-size: 12px; }}
    .chapter-list {{ display: grid; gap: 8px; }}
    .chapter-item {{
      width: 100%; text-align: left; border: 1px solid var(--line); background: var(--panel);
      border-radius: 8px; padding: 10px; cursor: pointer;
    }}
    .chapter-item.active {{ border-color: var(--accent); background: var(--accent-soft); }}
    .chapter-name {{ display: block; font-weight: 800; line-height: 1.35; }}
    .chapter-meta {{ display: block; margin-top: 4px; color: var(--muted); font-size: 12px; line-height: 1.4; word-break: break-all; }}
    .bookmark-list {{ display: grid; gap: 8px; }}
    .sidebar .chapter-list[hidden],
    .sidebar .bookmark-list[hidden] {{ display: none !important; }}
    .side-actions {{ display: flex; align-items: center; gap: 6px; min-width: 0; }}
    .bookmark-item {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px; align-items: stretch; }}
    .bookmark-open {{ width: 100%; text-align: left; border: 1px solid var(--line); background: var(--panel); border-radius: 8px; padding: 10px; cursor: pointer; }}
    .bookmark-open:hover, .bookmark-open:focus {{ border-color: var(--accent); background: var(--accent-soft); outline: none; }}
    .bookmark-delete {{ align-self: stretch; color: var(--danger); border-color: color-mix(in srgb, var(--danger) 42%, var(--line)); }}
    .reader-shell {{ min-width: 0; padding: 18px 18px 96px; overflow-anchor: none; }}
    .reader {{
      width: min(var(--reader-width), 100%); margin: 0 auto; background: var(--panel);
      border: 1px solid var(--line); border-radius: 8px; box-shadow: var(--shadow);
      padding: clamp(22px, 4vw, 46px);
    }}
    .reader > h1 {{ margin: 0 0 6px; font-size: calc(var(--reader-font-size) * 1.65); line-height: 1.25; letter-spacing: 0; }}
    .source-line {{ margin-bottom: 18px; color: var(--muted); font-size: 14px; word-break: break-all; }}
    .chapter-nav {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 18px 0; }}
    .content {{ font-size: var(--reader-font-size); }}
    .content h1, .content h2, .content h3 {{ line-height: 1.35; margin-top: 1.25em; }}
    .content h1 {{ font-size: 2em; }}
    .content h2 {{ font-size: 1.5em; }}
    .content h3 {{ font-size: 1.25em; }}
    .content h1, .content h2, .content h3, .content h4, .content h5, .content h6 {{ position: relative; }}
    .content p, .content blockquote, .content li {{ position: relative; }}
    .content p {{ margin: 0 0 1em; }}
    .content blockquote {{
      margin: 1em 0; padding: .2em 1em; border-left: 4px solid var(--accent);
      color: var(--muted); background: var(--accent-soft);
    }}
    .content img {{ max-width: 100%; height: auto; border-radius: 6px; cursor: zoom-in; }}
    .content a {{ color: var(--accent); }}
    .content .disabled-link, .content .disabled-image {{
      display: inline-block;
      color: var(--muted);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0 .55em;
      background: var(--panel);
      font-size: .9em;
    }}
    .content mark {{ background: #ffe58a; color: #241f18; padding: 0 .08em; }}
    .content .docx-small {{ font-size: .78em; color: var(--muted); }}
    .code-block {{ position: relative; margin: 1em 0; border: 1px solid var(--line); border-radius: 6px; overflow: hidden; background: var(--panel-2); }}
    .code-tools {{ display: flex; justify-content: space-between; gap: 10px; padding: 7px 10px; border-bottom: 1px solid var(--line); color: var(--muted); font-size: 12px; }}
    .code-block pre {{ margin: 0; overflow: auto; padding: 14px; }}
    code, pre {{ font-family: Consolas, "Cascadia Mono", monospace; }}
    .table-wrap {{ position: relative; overflow: auto; margin: 1em 0; border: 1px solid var(--line); border-radius: 6px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 520px; background: var(--panel); }}
    .csv-summary {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; color: var(--muted); font-size: .9em; margin: .25em 0 .5em; }}
    .csv-current-row-review {{ min-height: 30px; padding: 3px 8px; font-size: 12px; white-space: nowrap; }}
    .csv-table {{ min-width: 640px; }}
    .csv-table tr[data-block-type="csv-row"] {{ cursor: pointer; }}
    .csv-table tr.csv-row-active td {{ background: color-mix(in srgb, var(--accent-soft) 78%, var(--panel)); box-shadow: inset 3px 0 0 var(--accent); }}
    .docx-structured-table {{ min-width: 520px; }}
    .docx-nested-table {{ min-width: 260px; margin: 6px 0; border: 1px solid var(--line); }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px 10px; vertical-align: top; }}
    th {{ position: sticky; top: 0; background: var(--panel-2); text-align: left; font-weight: 800; }}
    tr:hover td {{ background: var(--accent-soft); }}
    .block-review {{
      opacity: 0; position: absolute; right: 0; transform: translateX(100%); margin-right: -8px;
      border: 1px solid var(--line); background: var(--panel); border-radius: 999px; padding: 2px 7px; font-size: 12px; cursor: pointer;
    }}
    .block-review-contained {{ right: 8px; transform: none; margin-right: 0; z-index: 2; }}
    .code-block > .block-review-contained {{ top: 7px; right: 78px; }}
    .table-wrap > .block-review-contained {{ top: 7px; }}
    [data-block-index]:hover .block-review {{ opacity: 1; }}
    .fixed-nav {{
      position: fixed; left: var(--fixed-left-offset); right: var(--fixed-right-offset); bottom: 0; z-index: 4;
      display: flex; justify-content: center; align-items: center; gap: 12px;
      padding: 10px; background: color-mix(in srgb, var(--panel) 94%, transparent);
      border-top: 1px solid var(--line); backdrop-filter: blur(10px);
    }}
    .fixed-nav #positionText {{ min-width: 0; text-align: center; }}
    .bookmark-current[aria-pressed="true"] {{ border-color: var(--accent); background: var(--accent-soft); }}
    .floating-review {{
      position: fixed; right: calc(var(--fixed-right-offset) + 20px); bottom: 80px; z-index: 10;
      width: 44px; height: 44px; border-radius: 50%;
      background: var(--accent); color: white; border: none;
      box-shadow: 0 2px 12px rgba(0,0,0,.18);
      display: flex; align-items: center; justify-content: center; cursor: grab;
      opacity: .72; transition: opacity .18s, transform .18s, box-shadow .18s;
      user-select: none; -webkit-user-select: none;
    }}
    .floating-review:hover,
    .floating-review.has-selection {{
      opacity: 1; transform: scale(1.08); box-shadow: 0 4px 20px rgba(0,0,0,.25);
    }}
    .floating-review.dragging {{ cursor: grabbing; opacity: 1; transform: scale(1.12); }}
    @media (max-width: 1100px) {{
      .floating-review {{ right: 16px; bottom: 80px; }}
    }}
    .review-list {{ display: grid; gap: 10px; margin: 10px 0; }}
    .review-item {{ border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: var(--panel); overflow-wrap: anywhere; word-break: break-word; }}
    .review-item[data-review-id] {{ cursor: pointer; }}
    .review-item[data-review-id]:hover,
    .review-item[data-review-id]:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); outline: none; }}
    .review-item header {{ display: flex; justify-content: space-between; gap: 8px; align-items: start; margin-bottom: 8px; }}
    .review-item textarea {{ width: 100%; min-height: 72px; resize: vertical; margin-top: 8px; }}
    .review-context {{ margin-top: 8px; }}
    .review-context-heading {{ color: var(--muted); font-size: 12px; margin-bottom: 4px; }}
    .review-context .quote-box {{ max-height: 120px; }}
    .review-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }}
    .review-preview {{ width: 100%; min-height: 220px; margin-top: 10px; resize: vertical; font-family: Consolas, monospace; font-size: 12px; }}
    .review-target-highlight {{ animation: review-target-pulse 1.6s ease-out; }}
    .csv-table tr.review-target-highlight td {{ animation: review-target-cell-pulse 1.6s ease-out; }}
    @keyframes review-target-pulse {{
      0%, 70% {{ background: #fff3bf; box-shadow: 0 0 0 4px rgba(245, 158, 11, .32); }}
      100% {{ background: transparent; box-shadow: none; }}
    }}
    @keyframes review-target-cell-pulse {{
      0%, 70% {{ background: #fff3bf; }}
      100% {{ background: transparent; }}
    }}
    .empty {{ padding: 14px; color: var(--muted); text-align: center; border: 1px dashed var(--line); border-radius: 8px; }}
    dialog {{ width: min(680px, calc(100vw - 32px)); border: 1px solid var(--line); border-radius: 10px; background: var(--panel); color: var(--text); box-shadow: var(--shadow); resize: both; overflow: auto; min-width: 320px; min-height: 240px; max-width: 92vw; max-height: 92vh; }}
    dialog::backdrop {{ background: rgba(0, 0, 0, .35); }}
    .dialog-body {{ display: grid; gap: 10px; }}
    .quote-box {{ max-height: 180px; overflow: auto; padding: 10px; background: var(--panel-2); border: 1px solid var(--line); border-radius: 6px; white-space: pre-wrap; overflow-wrap: anywhere; word-break: break-word; }}
    .dialog-actions {{ display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }}
    @media (max-width: 1180px) {{
      .layout {{ grid-template-columns: var(--left-panel-width) 0 minmax(0, 1fr); }}
      .layout.left-collapsed,
      .layout.left-collapsed.right-collapsed {{ grid-template-columns: 0 0 minmax(0, 1fr); }}
      .layout.right-collapsed {{ grid-template-columns: var(--left-panel-width) 0 minmax(0, 1fr); }}
      .review-panel {{ position: static; height: auto; grid-column: 3; border-left: 0; border-top: 1px solid var(--line); }}
      .layout.left-collapsed:not(.right-collapsed) {{ grid-template-columns: 0 0 minmax(0, 1fr) 0 var(--right-panel-width); }}
      .layout.left-collapsed:not(.right-collapsed) .review-panel {{
        position: sticky; top: var(--toolbar-height); height: calc(100vh - var(--toolbar-height));
        grid-column: 5; border-left: 1px solid var(--line); border-top: 0;
      }}
      .layout.left-collapsed:not(.right-collapsed) .panel-resizer.right {{ display: block; grid-column: 4; }}
      .fixed-nav {{ left: var(--fixed-left-offset); right: 0; }}
      .panel-resizer.right {{ display: none; }}
    }}
    @media (max-width: 820px) {{
      .toolbar-row {{ align-items: stretch; flex-direction: column; }}
      .toolbar-main, .toolbar-filters {{ justify-content: flex-start; width: 100%; }}
      .search {{ width: 100%; }}
      .layout,
      .layout.left-collapsed,
      .layout.right-collapsed,
      .layout.left-collapsed.right-collapsed {{ grid-template-columns: minmax(0, 1fr); }}
      .sidebar {{ position: static; height: auto; max-height: 42vh; border-right: 0; border-bottom: 1px solid var(--line); grid-column: 1; }}
      .panel-resizer {{ display: none; }}
      .reader-shell {{ padding: 14px 10px 96px; grid-column: 1; }}
      .review-panel {{ grid-column: 1; }}
      .layout.left-collapsed:not(.right-collapsed) .review-panel {{ position: static; height: auto; grid-column: 1; border-left: 0; border-top: 1px solid var(--line); }}
      .layout.left-collapsed:not(.right-collapsed) .panel-resizer.right {{ display: none; }}
      .fixed-nav {{ left: 0; right: 0; gap: 8px; padding: 8px; }}
      .fixed-nav #positionText {{ display: none; }}
      .block-review {{ opacity: 1; position: static; transform: none; margin: 4px 0 0 0; }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <header class="toolbar">
      <div class="toolbar-row">
        <div class="book-title" id="bookTitle"></div>
        <div class="controls toolbar-main">
          <button class="btn" id="toggleTocButton" type="button">{label('hide_toc')}</button>
          <button class="btn" id="toggleReviewPanelButton" type="button">{label('hide_review_panel')}</button>
          <button class="btn" id="themeButton" type="button">{label('theme_dark')}</button>
        </div>
      </div>
      <div class="controls toolbar-filters">
        <input class="search" id="searchInput" type="search" placeholder="{label('search_placeholder')}">
        <select class="select" id="extFilter" title="{label('file_type')}">
          <option value="all">{label('all')}</option>
          <option value=".md">.md</option>
          <option value=".txt">.txt</option>
          <option value=".csv">.csv</option>
        </select>
        <button class="btn" id="clearFilterButton" type="button">{label('clear')}</button>
        <button class="btn" id="sortButton" type="button">{label('sort_asc')}</button>
        <button class="btn" id="smallerButton" type="button">A-</button>
        <button class="btn" id="largerButton" type="button">A+</button>
        <select class="select" id="widthSelect" title="{label('width_title')}">
          <option value="780">{label('width_narrow')}</option>
          <option value="1040">{label('width_standard')}</option>
          <option value="1360">{label('width_wide')}</option>
          <option value="full">{label('width_full')}</option>
        </select>
        <button class="btn" id="resetLayoutButton" type="button">{label('reset_layout')}</button>
      </div>
    </header>
    <main class="layout" id="layoutRoot">
      <aside class="sidebar">
        <div class="side-head">
          <div class="panel-tabs" role="tablist">
            <button class="btn panel-tab" id="tocTabButton" type="button" role="tab">{label('toc')}</button>
            <button class="btn panel-tab" id="bookmarkTabButton" type="button" role="tab">{label('bookmarks')}</button>
          </div>
          <div class="side-actions">
            <span class="small-text" id="chapterCount"></span>
            <button class="btn" id="clearBookmarksButton" type="button" hidden>{label('clear_bookmarks')}</button>
          </div>
        </div>
        <div class="chapter-list" id="chapterList"></div>
        <div class="bookmark-list" id="bookmarkList" hidden></div>
      </aside>
      <div class="panel-resizer left" id="leftPanelResizer" role="separator" aria-orientation="vertical" title="{label('left_resizer_title')}"></div>
      <section class="reader-shell">
        <article class="reader">
          <h1 id="chapterTitle"></h1>
          <div class="source-line" id="sourceLine"></div>
          <nav class="chapter-nav">
            <button class="btn" id="topPrevButton" type="button">{label('previous')}</button>
            <button class="btn" id="topNextButton" type="button">{label('next')}</button>
          </nav>
          <div class="content" id="content"></div>
          <nav class="chapter-nav">
            <button class="btn" id="bottomPrevButton" type="button">{label('previous')}</button>
            <button class="btn" id="bottomNextButton" type="button">{label('next')}</button>
          </nav>
        </article>
      </section>
      <div class="panel-resizer right" id="rightPanelResizer" role="separator" aria-orientation="vertical" title="{label('right_resizer_title')}"></div>
      <aside class="review-panel">
        <div class="side-head">
          <strong>{label('review_panel')}</strong>
          <span class="small-text" id="reviewCount"></span>
        </div>
        <div class="controls">
          <button class="btn" id="copyReviewButton" type="button">{label('copy_review')}</button>
          <button class="btn" id="downloadReviewButton" type="button">{label('download')}</button>
          <button class="btn danger" id="clearReviewsButton" type="button">{label('clear')}</button>
        </div>
        <div class="review-list" id="reviewList"></div>
        <textarea class="review-preview" id="reviewPreview" readonly></textarea>
      </aside>
      <button class="floating-review" id="floatingReviewButton" type="button" title="{label('floating_review_title')}">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12.5 4.5l3 3L7 16H4v-3l8.5-8.5z"/>
          <path d="M11 6l3 3"/>
        </svg>
      </button>
    </main>
    <nav class="fixed-nav">
      <button class="btn" id="fixedPrevButton" type="button">{label('previous')}</button>
      <span class="small-text" id="positionText"></span>
      <button class="btn bookmark-current" id="bookmarkCurrentButton" type="button" title="{label('bookmark_shortcut_title')}">{label('add_bookmark')}</button>
      <button class="btn" id="fixedNextButton" type="button">{label('next')}</button>
    </nav>
  </div>

  <dialog id="reviewDialog">
    <form method="dialog" id="reviewForm">
      <h2>{label('add_review')}</h2>
      <div class="dialog-body">
        <label>{label('quote_original')}</label>
        <div class="quote-box" id="dialogQuote"></div>
        <div class="review-grid">
          <label>{label('action')}
            <select class="select" id="dialogAction"></select>
          </label>
          <label>{label('target')}
            <select class="select" id="dialogTarget"></select>
          </label>
        </div>
        <label>{label('review_instruction')}</label>
        <textarea id="dialogComment" rows="5" placeholder="{label('review_placeholder')}"></textarea>
      </div>
      <div class="dialog-actions">
        <button class="btn" value="cancel" type="button" id="cancelReviewButton">{label('cancel')}</button>
        <button class="btn primary" value="default" type="submit">{label('add_review')}</button>
      </div>
    </form>
  </dialog>

  <script>
    const BOOK_DATA = {payload};
    const APP_CONFIG = {config_payload};
    const storageKey = "folder-review-reader:" + BOOK_DATA.title;
    const reviewStorageKey = storageKey + ":reviews";
    const bookmarkStorageKey = storageKey + ":bookmarks";
    const display = APP_CONFIG.display || {{}};
    const reviewConfig = APP_CONFIG.review || {{}};
    const labels = APP_CONFIG.labels || {{}};
    const layoutDefaults = {{
      fontSize: Number(display.default_font_size || 18),
      width: display.default_width || "full",
      theme: display.theme || "light",
      leftPanelWidth: 300,
      rightPanelWidth: 360,
      leftCollapsed: false,
      rightCollapsed: false
    }};
    const state = {{
      currentId: null,
      query: "",
      ext: "all",
      reversed: false,
      leftPanelView: "toc",
      ...layoutDefaults,
      reviews: [],
      bookmarks: [],
      pendingReview: null,
      lastSelection: null,
      activeBlock: null
    }};

    const els = {{
      toolbar: document.querySelector(".toolbar"),
      bookTitle: document.getElementById("bookTitle"),
      layoutRoot: document.getElementById("layoutRoot"),
      readerShell: document.querySelector(".reader-shell"),
      searchInput: document.getElementById("searchInput"),
      extFilter: document.getElementById("extFilter"),
      clearFilterButton: document.getElementById("clearFilterButton"),
      sortButton: document.getElementById("sortButton"),
      toggleTocButton: document.getElementById("toggleTocButton"),
      bookmarkCurrentButton: document.getElementById("bookmarkCurrentButton"),
      toggleReviewPanelButton: document.getElementById("toggleReviewPanelButton"),
      smallerButton: document.getElementById("smallerButton"),
      largerButton: document.getElementById("largerButton"),
      widthSelect: document.getElementById("widthSelect"),
      resetLayoutButton: document.getElementById("resetLayoutButton"),
      themeButton: document.getElementById("themeButton"),
      chapterCount: document.getElementById("chapterCount"),
      chapterList: document.getElementById("chapterList"),
      tocTabButton: document.getElementById("tocTabButton"),
      bookmarkTabButton: document.getElementById("bookmarkTabButton"),
      bookmarkList: document.getElementById("bookmarkList"),
      clearBookmarksButton: document.getElementById("clearBookmarksButton"),
      chapterTitle: document.getElementById("chapterTitle"),
      sourceLine: document.getElementById("sourceLine"),
      content: document.getElementById("content"),
      topPrevButton: document.getElementById("topPrevButton"),
      topNextButton: document.getElementById("topNextButton"),
      bottomPrevButton: document.getElementById("bottomPrevButton"),
      bottomNextButton: document.getElementById("bottomNextButton"),
      fixedPrevButton: document.getElementById("fixedPrevButton"),
      fixedNextButton: document.getElementById("fixedNextButton"),
      fixedNav: document.querySelector(".fixed-nav"),
      positionText: document.getElementById("positionText"),
      leftPanelResizer: document.getElementById("leftPanelResizer"),
      rightPanelResizer: document.getElementById("rightPanelResizer"),
      floatingReviewButton: document.getElementById("floatingReviewButton"),
      reviewCount: document.getElementById("reviewCount"),
      reviewList: document.getElementById("reviewList"),
      reviewPreview: document.getElementById("reviewPreview"),
      copyReviewButton: document.getElementById("copyReviewButton"),
      downloadReviewButton: document.getElementById("downloadReviewButton"),
      clearReviewsButton: document.getElementById("clearReviewsButton"),
      dialog: document.getElementById("reviewDialog"),
      reviewForm: document.getElementById("reviewForm"),
      dialogQuote: document.getElementById("dialogQuote"),
      dialogAction: document.getElementById("dialogAction"),
      dialogTarget: document.getElementById("dialogTarget"),
      dialogComment: document.getElementById("dialogComment"),
      cancelReviewButton: document.getElementById("cancelReviewButton")
    }};

    function escapeHtml(value) {{
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }}

    function label(key) {{
      return Object.prototype.hasOwnProperty.call(labels, key) ? labels[key] : key;
    }}

    function readingMinutes(wordCount) {{
      return Math.max(1, Math.ceil(Number(wordCount || 0) / 450));
    }}

    function readingTimeLabel(wordCount) {{
      return `${{readingMinutes(wordCount)}} ${{label("reading_minutes")}}`;
    }}

    function totalReadingTimeLabel(chapters) {{
      const totalWords = chapters.reduce((sum, chapter) => sum + Number(chapter.word_count || 0), 0);
      return readingTimeLabel(totalWords);
    }}

    function chapterCsvMeta(chapter) {{
      if (chapter.ext !== ".csv") return "";
      const rows = Number.isFinite(chapter.row_count) ? chapter.row_count : 0;
      const columns = Number.isFinite(chapter.column_count) ? chapter.column_count : 0;
      return `CSV · ${{rows}} ${{label("csv_rows")}} · ${{columns}} ${{label("csv_columns")}}`;
    }}

    function loadState() {{
      try {{
        Object.assign(state, JSON.parse(localStorage.getItem(storageKey) || "{{}}"));
      }} catch (error) {{}}
      try {{
        state.reviews = JSON.parse(localStorage.getItem(reviewStorageKey) || "[]");
      }} catch (error) {{
        state.reviews = [];
      }}
      try {{
        state.bookmarks = JSON.parse(localStorage.getItem(bookmarkStorageKey) || "[]");
      }} catch (error) {{
        state.bookmarks = [];
      }}
      if (!BOOK_DATA.chapters.some(chapter => chapter.id === state.currentId)) {{
        state.currentId = BOOK_DATA.chapters[0]?.id || null;
      }}
    }}

    function saveState() {{
      localStorage.setItem(storageKey, JSON.stringify({{
        currentId: state.currentId,
        reversed: state.reversed,
        fontSize: state.fontSize,
        width: state.width,
        theme: state.theme,
        leftPanelWidth: state.leftPanelWidth,
        rightPanelWidth: state.rightPanelWidth,
        leftCollapsed: state.leftCollapsed,
        rightCollapsed: state.rightCollapsed,
        leftPanelView: state.leftPanelView,
        query: state.query,
        ext: state.ext
      }}));
      localStorage.setItem(reviewStorageKey, JSON.stringify(state.reviews));
      localStorage.setItem(bookmarkStorageKey, JSON.stringify(state.bookmarks));
    }}

    function orderedChapters() {{
      const chapters = [...BOOK_DATA.chapters];
      return state.reversed ? chapters.reverse() : chapters;
    }}

    function visibleChapters() {{
      const query = state.query.trim().toLowerCase();
      return orderedChapters().filter(chapter => {{
        if (state.ext !== "all" && chapter.ext !== state.ext) return false;
        if (!query) return true;
        return [
          chapter.title,
          chapter.file_name,
          chapter.relative_path,
          chapter.folder,
          chapter.prefix,
          chapter.ext,
          chapter.content_text
        ].some(value => String(value || "").toLowerCase().includes(query));
      }});
    }}

    function currentChapter() {{
      return BOOK_DATA.chapters.find(chapter => chapter.id === state.currentId) || BOOK_DATA.chapters[0] || null;
    }}

    function currentVisibleIndex(chapters = visibleChapters()) {{
      return chapters.findIndex(chapter => chapter.id === state.currentId);
    }}

    function ensureCurrentVisible(chapters = visibleChapters()) {{
      if (!chapters.length) return;
      if (!chapters.some(chapter => chapter.id === state.currentId)) {{
        state.currentId = chapters[0].id;
      }}
    }}

    function scrollReaderToTop() {{
      requestAnimationFrame(() => requestAnimationFrame(() => {{
        const toolbarHeight = els.toolbar.getBoundingClientRect().height;
        const readerTop = els.readerShell.getBoundingClientRect().top + window.scrollY;
        window.scrollTo({{ top: Math.max(0, readerTop - toolbarHeight), left: 0, behavior: "auto" }});
      }}));
    }}

    function setCurrent(id, scrollTop = true) {{
      state.currentId = id;
      saveState();
      render();
      if (scrollTop) scrollReaderToTop();
    }}

    function move(delta) {{
      const chapters = visibleChapters();
      ensureCurrentVisible(chapters);
      const index = currentVisibleIndex(chapters);
      const next = chapters[index + delta];
      if (next) setCurrent(next.id);
    }}

    function clamp(value, min, max) {{
      return Math.min(max, Math.max(min, value));
    }}

    function syncToolbarHeight() {{
      const height = Math.ceil(els.toolbar.getBoundingClientRect().height);
      document.documentElement.style.setProperty("--toolbar-height", height + "px");
    }}

    function clampPanelWidths() {{
      const available = window.innerWidth || 1200;
      const minReader = available < 1180 ? 360 : 420;
      state.leftPanelWidth = clamp(Number(state.leftPanelWidth || 300), 220, Math.min(520, available - minReader));
      state.rightPanelWidth = clamp(Number(state.rightPanelWidth || 360), 280, Math.min(620, available - minReader));
      if (available >= 1180 && state.leftPanelWidth + state.rightPanelWidth > available - minReader) {{
        state.rightPanelWidth = Math.max(280, available - minReader - state.leftPanelWidth);
      }}
    }}

    function applyPreferences() {{
      clampPanelWidths();
      document.body.classList.toggle("dark", state.theme === "dark");
      document.documentElement.style.setProperty("--reader-font-size", state.fontSize + "px");
      const readerWidth = state.width === "full" ? "100%" : Number(state.width || 1360) + "px";
      document.documentElement.style.setProperty("--reader-width", readerWidth);
      document.documentElement.style.setProperty("--left-panel-width", state.leftPanelWidth + "px");
      document.documentElement.style.setProperty("--right-panel-width", state.rightPanelWidth + "px");
      const viewportWidth = window.innerWidth || 1200;
      const fixedLeftOffset = viewportWidth <= 820 || state.leftCollapsed ? 0 : state.leftPanelWidth;
      const reviewBesideReader = viewportWidth >= 1180 || (viewportWidth > 820 && state.leftCollapsed);
      const fixedRightOffset = !reviewBesideReader || state.rightCollapsed ? 0 : state.rightPanelWidth;
      document.documentElement.style.setProperty("--fixed-left-offset", fixedLeftOffset + "px");
      document.documentElement.style.setProperty("--fixed-right-offset", fixedRightOffset + "px");
      els.layoutRoot.classList.toggle("left-collapsed", !!state.leftCollapsed);
      els.layoutRoot.classList.toggle("right-collapsed", !!state.rightCollapsed);
      els.widthSelect.value = String(state.width);
      els.themeButton.textContent = state.theme === "dark" ? label("theme_light") : label("theme_dark");
      els.sortButton.textContent = state.reversed ? label("sort_desc") : label("sort_asc");
      els.toggleTocButton.textContent = state.leftCollapsed ? label("show_toc") : label("hide_toc");
      els.toggleReviewPanelButton.textContent = state.rightCollapsed ? label("show_review_panel") : label("hide_review_panel");
      els.toggleTocButton.setAttribute("aria-pressed", String(!state.leftCollapsed));
      els.toggleReviewPanelButton.setAttribute("aria-pressed", String(!state.rightCollapsed));
      els.searchInput.value = state.query || "";
      els.extFilter.value = state.ext || "all";
    }}

    function renderList() {{
      const chapters = visibleChapters();
      ensureCurrentVisible(chapters);
      const showBookmarks = state.leftPanelView === "bookmarks";
      els.chapterList.hidden = showBookmarks;
      els.bookmarkList.hidden = !showBookmarks;
      els.tocTabButton.classList.toggle("active", !showBookmarks);
      els.bookmarkTabButton.classList.toggle("active", showBookmarks);
      els.tocTabButton.setAttribute("aria-selected", String(!showBookmarks));
      els.bookmarkTabButton.setAttribute("aria-selected", String(showBookmarks));
      els.clearBookmarksButton.hidden = !showBookmarks || !state.bookmarks.length;
      els.chapterCount.textContent = showBookmarks
        ? `${{state.bookmarks.length}} ${{label("items")}}`
        : `${{chapters.length}} / ${{BOOK_DATA.chapters.length}}`;
      els.chapterList.innerHTML = "";
      if (!chapters.length) {{
        els.chapterList.innerHTML = `<div class="empty">${{escapeHtml(label("no_files"))}}</div>`;
        renderBookmarks();
        return;
      }}
      for (const [index, chapter] of chapters.entries()) {{
        const csvMeta = chapterCsvMeta(chapter);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chapter-item" + (chapter.id === state.currentId ? " active" : "");
        button.innerHTML = `
          <span class="chapter-name">${{index + 1}}. ${{escapeHtml(chapter.title)}}</span>
          <span class="chapter-meta">${{escapeHtml(chapter.relative_path)}} · ${{chapter.word_count}} ${{escapeHtml(label("words"))}} · ${{readingTimeLabel(chapter.word_count)}} · ${{chapter.ext}}${{csvMeta ? " · " + escapeHtml(csvMeta) : ""}}</span>
        `;
        button.addEventListener("click", () => setCurrent(chapter.id));
        els.chapterList.appendChild(button);
      }}
      renderBookmarks();
    }}

    function currentBookmarkTarget() {{
      const chapter = currentChapter();
      const block = state.activeBlock && els.content.contains(state.activeBlock)
        ? state.activeBlock
        : nearestReviewBlock();
      if (!chapter || !block) return null;
      return {{
        chapter_id: chapter.id,
        file_name: chapter.file_name,
        relative_path: chapter.relative_path,
        title: chapter.title,
        block_index: block.dataset.blockIndex || "",
        block_type: block.dataset.blockType || "selection",
        position_text: "",
        quote: blockQuoteText(block)
      }};
    }}

    function matchingBookmark(target) {{
      if (!target) return null;
      return state.bookmarks.find(bookmark => (
        bookmark.chapter_id === target.chapter_id
        && bookmark.block_index === target.block_index
        && bookmark.block_type === target.block_type
      )) || null;
    }}

    function toggleCurrentBookmark() {{
      const target = currentBookmarkTarget();
      if (!target) return;
      const existing = matchingBookmark(target);
      if (existing) {{
        state.bookmarks = state.bookmarks.filter(bookmark => bookmark.id !== existing.id);
      }} else {{
        state.bookmarks.push({{ id: "bookmark-" + Date.now(), ...target }});
      }}
      saveState();
      renderList();
    }}

    function renderBookmarks() {{
      renderBookmarkCurrentButton();
      els.bookmarkList.innerHTML = "";
      if (!state.bookmarks.length) {{
        els.bookmarkList.innerHTML = `<div class="empty">${{escapeHtml(label("empty_bookmarks"))}}</div>`;
        return;
      }}
      state.bookmarks.forEach((bookmark, index) => {{
        const item = document.createElement("div");
        item.className = "bookmark-item";
        const openButton = document.createElement("button");
        openButton.type = "button";
        openButton.className = "bookmark-open";
        openButton.dataset.bookmarkId = bookmark.id;
        openButton.innerHTML = `
          <span class="chapter-name">${{index + 1}}. ${{escapeHtml(bookmark.title)}}</span>
          <span class="chapter-meta">${{escapeHtml(bookmark.relative_path)}} · ${{escapeHtml(reviewPositionText(bookmark))}}</span>
        `;
        openButton.addEventListener("click", () => navigateToReview(bookmark));
        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "btn bookmark-delete";
        deleteButton.dataset.bookmarkId = bookmark.id;
        deleteButton.textContent = label("delete");
        deleteButton.title = label("delete_bookmark");
        deleteButton.addEventListener("click", () => {{
          state.bookmarks = state.bookmarks.filter(item => item.id !== bookmark.id);
          saveState();
          renderList();
        }});
        item.append(openButton, deleteButton);
        els.bookmarkList.appendChild(item);
      }});
    }}

    function renderBookmarkCurrentButton() {{
      const current = currentBookmarkTarget();
      const activeBookmark = matchingBookmark(current);
      els.bookmarkCurrentButton.textContent = activeBookmark ? label("remove_bookmark") : label("add_bookmark");
      els.bookmarkCurrentButton.setAttribute("aria-pressed", String(!!activeBookmark));
    }}

    function addBlockReviewButtons() {{
      els.content.querySelectorAll("[data-block-index]").forEach(block => {{
        if (block.dataset.blockType === "csv-row") return;
        if (block.querySelector(":scope > .block-review")) return;
        const button = document.createElement("button");
        button.type = "button";
        button.className = ["code-block", "table", "docx-table"].includes(block.dataset.blockType)
          ? "block-review block-review-contained"
          : "block-review";
        button.textContent = label("review");
        button.addEventListener("click", event => {{
          event.stopPropagation();
          state.activeBlock = block;
          renderBookmarks();
          openReviewDialog(block);
        }});
        block.addEventListener("click", event => {{
          if (event.target.closest(".block-review")) return;
          state.activeBlock = block;
          renderBookmarks();
        }});
        block.appendChild(button);
      }});
    }}

    function attachCsvTables() {{
      els.content.querySelectorAll(".csv-chapter").forEach(chapter => {{
        const rows = Array.from(chapter.querySelectorAll('[data-block-type="csv-row"]'));
        const reviewButton = chapter.querySelector(".csv-current-row-review");
        const setActive = row => {{
          rows.forEach(item => item.classList.toggle("csv-row-active", item === row));
        }};
        if (rows.length && !rows.some(row => row.classList.contains("csv-row-active"))) {{
          setActive(rows[0]);
        }}
        rows.forEach(row => {{
          row.addEventListener("click", () => {{
            setActive(row);
            state.activeBlock = row;
            renderBookmarks();
          }});
        }});
        reviewButton?.addEventListener("click", event => {{
          event.stopPropagation();
          if (selectionInsideContent()) {{
            openReviewDialog();
            return;
          }}
          openReviewDialog(chapter.querySelector(".csv-row-active") || rows[0] || null);
        }});
      }});
    }}

    function reviewPositionText(review) {{
      if (review.position_text) return review.position_text;
      if (review.block_type === "csv-row") {{
        return `${{label("row_prefix")}} ${{review.block_index || "?"}} ${{label("row_suffix")}}`.trim();
      }}
      if (review.block_type === "heading") {{
        return `${{label("heading_prefix")}} ${{review.block_index || "?"}} ${{label("heading_suffix")}}`.trim();
      }}
      if (review.block_type === "code-block") {{
        return `${{label("code_block_prefix")}} ${{review.block_index || "?"}} ${{label("code_block_suffix")}}`.trim();
      }}
      if (review.block_type === "table" || review.block_type === "docx-table") {{
        return `${{label("table_prefix")}} ${{review.block_index || "?"}} ${{label("table_suffix")}}`.trim();
      }}
      return `${{label("paragraph_prefix")}} ${{review.block_index || "?"}} ${{label("paragraph_suffix")}}`.trim();
    }}

    function reviewContextForBlock(block, scope) {{
      const blocks = Array.from(els.content.querySelectorAll("[data-block-index]"));
      const currentIndex = blocks.indexOf(block);
      if (currentIndex < 0) return {{ start: "", end: "", excerpt: "" }};
      const toolbarBottom = Math.max(0, els.toolbar.getBoundingClientRect().bottom);
      const fixedNavTop = els.fixedNav?.getBoundingClientRect().top ?? window.innerHeight;
      const visibleTop = Math.min(toolbarBottom, window.innerHeight);
      const visibleBottom = Math.max(visibleTop + 1, Math.min(window.innerHeight, fixedNavTop));
      const visibleBlocks = blocks.filter(item => {{
        const rect = item.getBoundingClientRect();
        return rect.bottom > visibleTop && rect.top < visibleBottom;
      }});
      const candidateBlocks = scope === "viewport" && visibleBlocks.length
        ? visibleBlocks
        : blocks.slice(Math.max(0, currentIndex - 1), Math.min(blocks.length, currentIndex + 2));
      const anchorIndex = candidateBlocks.indexOf(block);
      const orderedIndexes = [];
      for (let offset = 0; orderedIndexes.length < candidateBlocks.length; offset += 1) {{
        const before = anchorIndex - offset;
        const after = anchorIndex + offset;
        if (before >= 0) orderedIndexes.push(before);
        if (offset && after < candidateBlocks.length) orderedIndexes.push(after);
      }}
      let excerptLength = 0;
      const entries = [];
      orderedIndexes.forEach(index => {{
        if (excerptLength >= 2400) return;
        const item = candidateBlocks[index];
        const text = blockQuoteText(item);
        if (!text) return;
        const remaining = Math.max(0, 2400 - excerptLength);
        const limit = Math.min(700, remaining);
        const shortened = text.length > limit
          ? `${{text.slice(0, limit)}}...`
          : text;
        excerptLength += shortened.length;
        entries.push({{ item, text: `[${{item.dataset.blockIndex}}] ${{shortened}}` }});
      }});
      entries.sort((left, right) => candidateBlocks.indexOf(left.item) - candidateBlocks.indexOf(right.item));
      const excerpt = entries.map(entry => entry.text).join("\\n\\n");
      return {{
        start: entries[0]?.item.dataset.blockIndex || "",
        end: entries[entries.length - 1]?.item.dataset.blockIndex || "",
        excerpt
      }};
    }}

    function reviewContextText(review) {{
      const start = review.context_start_index;
      const end = review.context_end_index;
      if (!start || !end) return "";
      return start === end
        ? `${{label("context_blocks")}} ${{start}}`
        : `${{label("context_blocks")}} ${{start}}-${{end}}`;
    }}

    function reviewScopeText(review) {{
      if (review.review_scope === "selection") return label("review_scope_selection");
      if (review.review_scope === "viewport") return label("review_scope_viewport");
      return label("review_scope_block");
    }}

    function attachCodeCopy() {{
      els.content.querySelectorAll(".copy-code").forEach(button => {{
        button.addEventListener("click", async () => {{
          const code = button.closest(".code-block")?.querySelector("code")?.textContent || "";
          await copyText(code);
          button.textContent = label("copied");
          setTimeout(() => button.textContent = label("copy_code"), 1200);
        }});
      }});
    }}

    function renderReader() {{
      const chapters = visibleChapters();
      ensureCurrentVisible(chapters);
      const chapter = currentChapter();
      if (!chapter) {{
        els.chapterTitle.textContent = label("no_files");
        els.sourceLine.textContent = "";
        els.content.innerHTML = "";
        return;
      }}
      els.chapterTitle.textContent = chapter.title;
      const visibleIndex = currentVisibleIndex(chapters);
      if (els.content.dataset.chapterId !== chapter.id) {{
        state.lastSelection = null;
        state.activeBlock = null;
        els.content.dataset.chapterId = chapter.id;
      }}
      els.sourceLine.textContent = [
        chapter.relative_path,
        `${{chapter.word_count}} ${{label("words")}}`,
        readingTimeLabel(chapter.word_count),
        chapter.ext,
        chapterCsvMeta(chapter),
        `${{label("position_prefix")}} ${{visibleIndex + 1}} / ${{chapters.length}}`,
        chapter.modified_time
      ].filter(Boolean).join(" · ");
      els.content.innerHTML = chapter.content_html;
      addBlockReviewButtons();
      attachCsvTables();
      attachCodeCopy();
      renderBookmarks();
      const prevDisabled = visibleIndex <= 0;
      const nextDisabled = visibleIndex === -1 || visibleIndex >= chapters.length - 1;
      [els.topPrevButton, els.bottomPrevButton, els.fixedPrevButton].forEach(button => button.disabled = prevDisabled);
      [els.topNextButton, els.bottomNextButton, els.fixedNextButton].forEach(button => button.disabled = nextDisabled);
      els.positionText.textContent = chapters.length
        ? `${{label("position_prefix")}} ${{visibleIndex + 1}} / ${{chapters.length}} · ${{label("current_prefix")}} ${{readingTimeLabel(chapter.word_count)}} · ${{label("filtered_prefix")}} ${{totalReadingTimeLabel(chapters)}}`
        : `${{label("position_prefix")}} 0 / 0`;
    }}

    function selectionInsideContent() {{
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) return "";
      const range = selection.getRangeAt(0);
      if (!els.content.contains(range.commonAncestorContainer)) return "";
      return selection.toString().trim();
    }}

    function closestElement(node, selector) {{
      while (node && node !== els.content) {{
        if (node.nodeType === 1 && node.matches?.(selector)) return node;
        node = node.parentNode;
      }}
      return null;
    }}

    function rangeLabel(start, end, prefix, suffix) {{
      if (!start && !end) return "";
      if (start === end || !end) return `${{prefix}} ${{start || "?"}} ${{suffix}}`.trim();
      return `${{prefix}} ${{start}}-${{end}} ${{suffix}}`.trim();
    }}

    function csvSelectionMeta(selection) {{
      if (!selection || selection.isCollapsed) return null;
      const range = selection.getRangeAt(0);
      let cells = Array.from(els.content.querySelectorAll(".csv-table tbody td"))
        .filter(cell => {{
          try {{
            return range.intersectsNode(cell);
          }} catch (error) {{
            return false;
          }}
        }});
      if (!cells.length) {{
        cells = [closestElement(range.startContainer, "td, th"), closestElement(range.endContainer, "td, th")].filter(Boolean);
      }}
      const rows = cells.map(cell => cell.closest('[data-block-type="csv-row"]')).filter(Boolean);
      if (!rows.length) return null;
      const rowNumbers = rows
        .map(row => Number(row.dataset.blockIndex))
        .filter(Number.isFinite)
        .sort((a, b) => a - b);
      const columnNumbers = cells
        .map(cell => cell.cellIndex + 1)
        .filter(Number.isFinite)
        .sort((a, b) => a - b);
      const firstRow = rows.reduce((best, row) => {{
        if (!best) return row;
        return Number(row.dataset.blockIndex) < Number(best.dataset.blockIndex) ? row : best;
      }}, null);
      const rowLabel = rangeLabel(rowNumbers[0], rowNumbers[rowNumbers.length - 1], label("row_prefix"), label("row_suffix"));
      const columnLabel = rangeLabel(columnNumbers[0], columnNumbers[columnNumbers.length - 1], label("column_prefix"), label("column_suffix"));
      return {{
        block: firstRow,
        block_index: rowNumbers[0] === rowNumbers[rowNumbers.length - 1]
          ? String(rowNumbers[0])
          : `${{rowNumbers[0]}}-${{rowNumbers[rowNumbers.length - 1]}}`,
        block_type: "csv-cell-selection",
        position_text: [rowLabel, columnLabel].filter(Boolean).join("，")
      }};
    }}

    function captureSelection() {{
      const selected = selectionInsideContent();
      if (!selected) {{
        state.lastSelection = null;
        return;
      }}
      const selection = window.getSelection();
      let block = null;
      if (selection && !selection.isCollapsed) {{
        let node = selection.anchorNode;
        while (node && node !== els.content) {{
          if (node.nodeType === 1 && node.matches?.("[data-block-index]")) {{
            block = node;
            break;
          }}
          node = node.parentNode;
        }}
      }}
      const csvMeta = csvSelectionMeta(selection);
      state.activeBlock = csvMeta?.block || block || state.activeBlock;
      state.lastSelection = {{
        quote: selected,
        block: csvMeta?.block || block,
        block_index: csvMeta?.block_index || block?.dataset?.blockIndex || "",
        block_type: csvMeta?.block_type || block?.dataset?.blockType || "selection",
        position_text: csvMeta?.position_text || ""
      }};
    }}

    function initFloatingDrag(button) {{
      let dragging = false;
      let moved = false;
      let startX, startY, origLeft, origTop;
      button.addEventListener("mousedown", event => {{
        if (event.button !== 0) return;
        dragging = true;
        moved = false;
        button.classList.add("dragging");
        const rect = button.getBoundingClientRect();
        startX = event.clientX;
        startY = event.clientY;
        origLeft = rect.left;
        origTop = rect.top;
        button.style.right = "auto";
        button.style.bottom = "auto";
        button.style.left = origLeft + "px";
        button.style.top = origTop + "px";
        event.preventDefault();
      }});
      document.addEventListener("mousemove", event => {{
        if (!dragging) return;
        const dx = event.clientX - startX;
        const dy = event.clientY - startY;
        if (Math.abs(dx) > 3 || Math.abs(dy) > 3) moved = true;
        button.style.left = (origLeft + dx) + "px";
        button.style.top = (origTop + dy) + "px";
      }});
      document.addEventListener("mouseup", () => {{
        if (!dragging) return;
        dragging = false;
        button.classList.remove("dragging");
      }});
      button.addEventListener("click", event => {{
        if (moved) {{
          moved = false;
          event.stopImmediatePropagation();
          event.preventDefault();
        }}
      }});
    }}

    function initPanelResize(handle, side) {{
      if (!handle) return;
      let startX = 0;
      let startWidth = 0;
      handle.addEventListener("mousedown", event => {{
        if (event.button !== 0) return;
        startX = event.clientX;
        startWidth = side === "left" ? state.leftPanelWidth : state.rightPanelWidth;
        handle.classList.add("dragging");
        document.body.classList.add("resizing-panels");
        event.preventDefault();
      }});
      document.addEventListener("mousemove", event => {{
        if (!handle.classList.contains("dragging")) return;
        const delta = event.clientX - startX;
        if (side === "left") {{
          state.leftPanelWidth = startWidth + delta;
        }} else {{
          state.rightPanelWidth = startWidth - delta;
        }}
        applyPreferences();
      }});
      document.addEventListener("mouseup", () => {{
        if (!handle.classList.contains("dragging")) return;
        handle.classList.remove("dragging");
        document.body.classList.remove("resizing-panels");
        saveState();
      }});
    }}

    function nearestReviewBlock(block = null) {{
      if (block) return block;
      const selection = window.getSelection();
      if (selection && !selection.isCollapsed) {{
        let node = selection.anchorNode;
        while (node && node !== els.content) {{
          if (node.nodeType === 1 && node.matches?.("[data-block-index]")) return node;
          node = node.parentNode;
        }}
      }}
      const activeCsvRow = els.content.querySelector(".csv-chapter .csv-row-active");
      if (activeCsvRow) return activeCsvRow;
      const centeredBlock = nearestVisualCenterBlock();
      if (centeredBlock) return centeredBlock;
      if (state.lastSelection?.block) return state.lastSelection.block;
      if (state.activeBlock && els.content.contains(state.activeBlock)) return state.activeBlock;
      return els.content.querySelector("[data-block-index]");
    }}

    function nearestVisualCenterBlock() {{
      const blocks = Array.from(els.content.querySelectorAll("[data-block-index]"));
      if (!blocks.length) return null;
      const toolbarBottom = Math.max(0, els.toolbar.getBoundingClientRect().bottom);
      const fixedNavTop = els.fixedNav?.getBoundingClientRect().top ?? window.innerHeight;
      const visibleTop = Math.min(toolbarBottom, window.innerHeight);
      const visibleBottom = Math.max(visibleTop + 1, Math.min(window.innerHeight, fixedNavTop));
      const center = (visibleTop + visibleBottom) / 2;
      let nearest = null;
      let nearestDistance = Infinity;
      blocks.forEach(candidate => {{
        const rect = candidate.getBoundingClientRect();
        if (rect.bottom <= visibleTop || rect.top >= visibleBottom) return;
        const distance = rect.top <= center && rect.bottom >= center
          ? 0
          : Math.min(Math.abs(rect.top - center), Math.abs(rect.bottom - center));
        if (distance < nearestDistance) {{
          nearest = candidate;
          nearestDistance = distance;
        }}
      }});
      return nearest;
    }}

    function blockQuoteText(block) {{
      if (!block) return "";
      if (block.dataset?.blockType === "csv-row") {{
        return Array.from(block.cells || [])
          .map(cell => cell.textContent.trim())
          .join("\\t")
          .trim();
      }}
      if (block.dataset?.blockType === "code-block") {{
        return block.querySelector("pre > code")?.textContent.trim() || "";
      }}
      const clone = block.cloneNode(true);
      clone.querySelectorAll(".block-review").forEach(button => button.remove());
      return clone.textContent.trim();
    }}

    function populateDialogOptions() {{
      const actions = Array.isArray(reviewConfig.actions) && reviewConfig.actions.length ? reviewConfig.actions : [label("review")];
      const targets = Array.isArray(reviewConfig.targets) && reviewConfig.targets.length ? reviewConfig.targets : [label("target")];
      els.dialogAction.innerHTML = actions.map(item => `<option value="${{escapeHtml(item)}}">${{escapeHtml(item)}}</option>`).join("");
      els.dialogTarget.innerHTML = targets.map(item => `<option value="${{escapeHtml(item)}}">${{escapeHtml(item)}}</option>`).join("");
    }}

    function openReviewDialog(block = null) {{
      if (reviewConfig.enabled === false) return;
      const chapter = currentChapter();
      if (!chapter) return;
      // A direct block button must not inherit an earlier text selection.
      const selected = block ? "" : selectionInsideContent();
      if (selected) {{
        captureSelection();
      }}
      const cached = selected ? state.lastSelection : null;
      const targetBlock = block || nearestReviewBlock(block);
      const quote = selected
        || (cached?.quote)
        || blockQuoteText(targetBlock);
      if (!quote) return;
      const reviewScope = selected ? "selection" : (block ? "block" : "viewport");
      const context = reviewContextForBlock(targetBlock, reviewScope);
      state.pendingReview = {{
        chapter_id: chapter.id,
        file_name: chapter.file_name,
        relative_path: chapter.relative_path,
        title: chapter.title,
        block_index: cached?.block_index || targetBlock?.dataset?.blockIndex || "",
        block_type: cached?.block_type || targetBlock?.dataset?.blockType || "selection",
        position_text: cached?.position_text || "",
        review_scope: reviewScope,
        context_start_index: context.start,
        context_end_index: context.end,
        context_excerpt: context.excerpt,
        quote
      }};
      state.lastSelection = null;
      populateDialogOptions();
      els.dialogQuote.textContent = quote;
      els.dialogComment.value = "";
      els.dialog.showModal();
      setTimeout(() => els.dialogComment.focus(), 0);
    }}

    function addReviewFromDialog() {{
      if (!state.pendingReview) return;
      const review = {{
        id: "review-" + Date.now(),
        ...state.pendingReview,
        action: els.dialogAction.value,
        target: els.dialogTarget.value,
        comment: els.dialogComment.value.trim(),
        created_at: new Date().toISOString()
      }};
      state.reviews.push(review);
      state.pendingReview = null;
      saveState();
      renderReviews();
    }}

    function markdownQuote(value) {{
      return String(value || "").split("\\n").map(line => "> " + line).join("\\n");
    }}

    function reviewMarkdown() {{
      const lines = [
        `# ${{BOOK_DATA.title}} - review.md`,
        "",
        `- ${{label("generated_at")}}: ${{new Date().toLocaleString()}}`,
        `- ${{label("review_count")}}: ${{state.reviews.length}}`,
        `- ${{label("grouping")}}: ${{label("group_by_file")}}`,
        ""
      ];
      const groups = [];
      const groupIndex = new Map();
      state.reviews.forEach(review => {{
        const key = review.relative_path || review.file_name || "unknown";
        if (!groupIndex.has(key)) {{
          const group = {{
            relative_path: review.relative_path,
            title: review.title,
            items: []
          }};
          groupIndex.set(key, group);
          groups.push(group);
        }}
        groupIndex.get(key).items.push(review);
      }});
      groups.forEach((group, groupOffset) => {{
        lines.push(`## ${{label("file_label")}} ${{groupOffset + 1}}: ${{group.title}}`);
        lines.push("");
        lines.push(`- ${{label("path_label")}}: ${{group.relative_path}}`);
        lines.push(`- ${{label("reviews_label")}}: ${{group.items.length}}`);
        lines.push("");
        group.items.forEach((review, index) => {{
          lines.push(`### ${{label("review_label")}} ${{index + 1}}: ${{review.action}} -> ${{review.target}}`);
          lines.push("");
          lines.push(`- ${{label("position_label")}}: ${{reviewPositionText(review)}}`);
          lines.push(`- ${{label("review_scope")}}: ${{reviewScopeText(review)}}`);
          lines.push(`- ${{label("time_label")}}: ${{review.created_at}}`);
          lines.push("");
          lines.push(`#### ${{label("quote_heading")}}`);
          lines.push("");
          lines.push(markdownQuote(review.quote));
          lines.push("");
          if (review.context_excerpt) {{
            lines.push(`#### ${{label("context_heading")}} (${{reviewContextText(review)}})`);
            lines.push("");
            lines.push(markdownQuote(review.context_excerpt));
            lines.push("");
          }}
          lines.push(`#### ${{label("instruction_heading")}}`);
          lines.push("");
          lines.push(review.comment || `(${{label("empty_value")}})`);
          lines.push("");
        }});
      }});
      return lines.join("\\n");
    }}

    function timestampForFileName(date = new Date()) {{
      const pad = value => String(value).padStart(2, "0");
      return [
        date.getFullYear(),
        pad(date.getMonth() + 1),
        pad(date.getDate())
      ].join("-") + "_" + pad(date.getHours()) + pad(date.getMinutes());
    }}

    function reviewFileName() {{
      return `review_${{timestampForFileName()}}.md`;
    }}

    function firstBlockIndex(value) {{
      const match = String(value || "").match(/\\d+/);
      return match ? match[0] : "";
    }}

    function currentFiltersHideChapter(chapterId) {{
      return !visibleChapters().some(chapter => chapter.id === chapterId);
    }}

    function findReviewTargetBlock(review) {{
      const blockIndex = firstBlockIndex(review.block_index);
      const blockType = String(review.block_type || "");
      let indexedBlock = null;
      if (review.block_type === "csv-row" || review.block_type === "csv-cell-selection") {{
        indexedBlock = els.content.querySelector(`[data-block-type="csv-row"][data-block-index="${{blockIndex}}"]`);
      }}
      if (!indexedBlock && blockIndex && blockType && blockType !== "selection") {{
        indexedBlock = els.content.querySelector(`[data-block-type="${{blockType}}"]` + `[data-block-index="${{blockIndex}}"]`);
      }}

      // Block indexes are fast but can shift after source edits. Confirm them against
      // the saved quote before accepting an older local review's target.
      const quote = String(review.quote || "").replace(/\\s+/g, " ").trim();
      if (quote) {{
        const quoteMatches = block => {{
          const text = blockQuoteText(block).replace(/\\s+/g, " ").trim();
          return text === quote || text.includes(quote);
        }};
        if (indexedBlock && quoteMatches(indexedBlock)) return indexedBlock;
        const quoteMatch = Array.from(els.content.querySelectorAll("[data-block-index]")).find(block => {{
          return quoteMatches(block);
        }});
        if (quoteMatch) return quoteMatch;
      }}
      if (indexedBlock) return indexedBlock;
      if (blockIndex && (!blockType || blockType === "selection")) {{
        return els.content.querySelector(`[data-block-index="${{blockIndex}}"]`);
      }}
      return null;
    }}

    function highlightReviewTarget(block) {{
      if (!block) return;
      block.classList.remove("review-target-highlight");
      void block.offsetWidth;
      block.classList.add("review-target-highlight");
      state.activeBlock = block;
      if (block.dataset.blockType === "csv-row") {{
        els.content.querySelectorAll(".csv-row-active").forEach(row => row.classList.remove("csv-row-active"));
        block.classList.add("csv-row-active");
      }}
      renderBookmarks();
      block.scrollIntoView({{ block: "center", inline: "nearest", behavior: "auto" }});
      setTimeout(() => block.classList.remove("review-target-highlight"), 1700);
    }}

    function navigateToReview(review) {{
      const chapter = BOOK_DATA.chapters.find(item => item.id === review.chapter_id);
      if (!chapter) return;
      if (currentFiltersHideChapter(chapter.id)) {{
        state.query = "";
        state.ext = "all";
      }}
      state.currentId = chapter.id;
      saveState();
      render();
      requestAnimationFrame(() => requestAnimationFrame(() => {{
        const target = findReviewTargetBlock(review);
        if (target) {{
          highlightReviewTarget(target);
        }} else {{
          scrollReaderToTop();
        }}
      }}));
    }}

    function renderReviews() {{
      els.reviewCount.textContent = `${{state.reviews.length}} ${{label("items")}}`;
      els.reviewList.innerHTML = "";
      if (!state.reviews.length) {{
        els.reviewList.innerHTML = `<div class="empty">${{escapeHtml(label("empty_reviews"))}}</div>`;
      }} else {{
        state.reviews.forEach((review, index) => {{
          const item = document.createElement("section");
          item.className = "review-item";
          item.tabIndex = 0;
          item.dataset.reviewId = review.id;
          item.innerHTML = `
            <header>
              <div>
                <strong>#${{index + 1}} ${{escapeHtml(review.action)}} -> ${{escapeHtml(review.target)}}</strong>
                <div class="small-text">${{escapeHtml(review.relative_path)}} · ${{escapeHtml(reviewPositionText(review))}}</div>
                <div class="small-text">${{escapeHtml(label("review_scope"))}}: ${{escapeHtml(reviewScopeText(review))}}</div>
                ${{reviewContextText(review) ? `<div class="small-text">${{escapeHtml(reviewContextText(review))}}</div>` : ""}}
              </div>
              <button class="btn danger" type="button" data-delete-review="${{review.id}}">${{escapeHtml(label("delete"))}}</button>
            </header>
            <div class="quote-box">${{escapeHtml(review.quote)}}</div>
            ${{review.context_excerpt ? `<div class="review-context"><div class="review-context-heading">${{escapeHtml(label("context_heading"))}}</div><div class="quote-box">${{escapeHtml(review.context_excerpt)}}</div></div>` : ""}}
            <div class="review-grid">
              <select class="select" data-edit-action="${{review.id}}"></select>
              <select class="select" data-edit-target="${{review.id}}"></select>
            </div>
            <textarea data-edit-comment="${{review.id}}">${{escapeHtml(review.comment || "")}}</textarea>
          `;
          els.reviewList.appendChild(item);
          fillSelect(item.querySelector(`[data-edit-action="${{review.id}}"]`), reviewConfig.actions || [label("review")], review.action);
          fillSelect(item.querySelector(`[data-edit-target="${{review.id}}"]`), reviewConfig.targets || [label("target")], review.target);
        }});
      }}
      els.reviewPreview.value = reviewMarkdown();
      saveState();
    }}

    function fillSelect(select, values, current) {{
      select.innerHTML = values.map(value => `<option value="${{escapeHtml(value)}}">${{escapeHtml(value)}}</option>`).join("");
      select.value = current;
    }}

    function updateReview(id, patch, rerender = true) {{
      const review = state.reviews.find(item => item.id === id);
      if (!review) return;
      Object.assign(review, patch);
      if (rerender) {{
        renderReviews();
      }} else {{
        els.reviewPreview.value = reviewMarkdown();
        saveState();
      }}
    }}

    async function copyText(text) {{
      if (navigator.clipboard?.writeText) {{
        try {{
          await navigator.clipboard.writeText(text);
          return;
        }} catch (error) {{}}
      }}
      els.reviewPreview.value = text;
      els.reviewPreview.select();
      document.execCommand("copy");
    }}

    function downloadReview() {{
      const blob = new Blob([reviewMarkdown()], {{ type: "text/markdown;charset=utf-8" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = reviewFileName();
      link.click();
      URL.revokeObjectURL(url);
    }}

    function render() {{
      applyPreferences();
      renderList();
      renderReader();
      renderReviews();
      saveState();
    }}

    els.bookTitle.textContent = BOOK_DATA.title;
    els.searchInput.addEventListener("input", event => {{
      state.query = event.target.value;
      render();
    }});
    els.extFilter.addEventListener("change", event => {{
      state.ext = event.target.value;
      render();
    }});
    els.clearFilterButton.addEventListener("click", () => {{
      state.query = "";
      state.ext = "all";
      render();
    }});
    els.sortButton.addEventListener("click", () => {{
      state.reversed = !state.reversed;
      render();
    }});
    els.toggleTocButton.addEventListener("click", () => {{
      state.leftCollapsed = !state.leftCollapsed;
      render();
    }});
    els.bookmarkCurrentButton.addEventListener("click", toggleCurrentBookmark);
    els.clearBookmarksButton.addEventListener("click", () => {{
      if (state.bookmarks.length && confirm(label("confirm_clear_bookmarks"))) {{
        state.bookmarks = [];
        saveState();
        renderList();
      }}
    }});
    els.tocTabButton.addEventListener("click", () => {{
      state.leftPanelView = "toc";
      render();
    }});
    els.bookmarkTabButton.addEventListener("click", () => {{
      state.leftPanelView = "bookmarks";
      render();
    }});
    els.toggleReviewPanelButton.addEventListener("click", () => {{
      state.rightCollapsed = !state.rightCollapsed;
      render();
    }});
    els.smallerButton.addEventListener("click", () => {{
      state.fontSize = Math.max(14, state.fontSize - 1);
      render();
    }});
    els.largerButton.addEventListener("click", () => {{
      state.fontSize = Math.min(30, state.fontSize + 1);
      render();
    }});
    els.widthSelect.addEventListener("change", event => {{
      state.width = event.target.value === "full" ? "full" : Number(event.target.value);
      render();
    }});
    els.themeButton.addEventListener("click", () => {{
      state.theme = state.theme === "dark" ? "light" : "dark";
      render();
    }});
    els.resetLayoutButton.addEventListener("click", () => {{
      Object.assign(state, layoutDefaults);
      render();
    }});
    [els.topPrevButton, els.bottomPrevButton, els.fixedPrevButton].forEach(button => button.addEventListener("click", () => move(-1)));
    [els.topNextButton, els.bottomNextButton, els.fixedNextButton].forEach(button => button.addEventListener("click", () => move(1)));
    initPanelResize(els.leftPanelResizer, "left");
    initPanelResize(els.rightPanelResizer, "right");
    els.content.addEventListener("mouseup", captureSelection);
    document.addEventListener("selectionchange", captureSelection);
    initFloatingDrag(els.floatingReviewButton);
    els.floatingReviewButton.addEventListener("click", () => openReviewDialog());
    document.addEventListener("selectionchange", () => {{
      const has = !!selectionInsideContent();
      els.floatingReviewButton.classList.toggle("has-selection", has);
    }});
    els.cancelReviewButton.addEventListener("click", () => els.dialog.close());
    els.dialog.addEventListener("click", event => {{
      if (event.target === els.dialog) els.dialog.close();
    }});
    els.reviewForm.addEventListener("submit", event => {{
      event.preventDefault();
      addReviewFromDialog();
      els.dialog.close();
    }});
    els.reviewList.addEventListener("click", event => {{
      const deleteId = event.target?.dataset?.deleteReview;
      if (deleteId) {{
        state.reviews = state.reviews.filter(review => review.id !== deleteId);
        renderReviews();
        return;
      }}
      if (event.target?.closest?.("button, select, textarea, input, a")) return;
      const reviewItem = event.target?.closest?.("[data-review-id]");
      const review = state.reviews.find(item => item.id === reviewItem?.dataset?.reviewId);
      if (review) navigateToReview(review);
    }});
    els.reviewList.addEventListener("keydown", event => {{
      if (event.key !== "Enter" && event.key !== " ") return;
      if (event.target?.closest?.("button, select, textarea, input, a")) return;
      const review = state.reviews.find(item => item.id === event.target?.dataset?.reviewId);
      if (!review) return;
      event.preventDefault();
      navigateToReview(review);
    }});
    els.reviewList.addEventListener("change", event => {{
      if (event.target?.dataset?.editAction) updateReview(event.target.dataset.editAction, {{ action: event.target.value }});
      if (event.target?.dataset?.editTarget) updateReview(event.target.dataset.editTarget, {{ target: event.target.value }});
    }});
    els.reviewList.addEventListener("input", event => {{
      if (event.target?.dataset?.editComment) updateReview(event.target.dataset.editComment, {{ comment: event.target.value }}, false);
    }});
    els.copyReviewButton.addEventListener("click", async () => {{
      await copyText(reviewMarkdown());
      els.copyReviewButton.textContent = label("copied");
      setTimeout(() => els.copyReviewButton.textContent = label("copy_review"), 1200);
    }});
    els.downloadReviewButton.addEventListener("click", downloadReview);
    els.clearReviewsButton.addEventListener("click", () => {{
      if (state.reviews.length && confirm(label("confirm_clear_reviews"))) {{
        state.reviews = [];
        renderReviews();
      }}
    }});
    document.addEventListener("keydown", event => {{
      if (event.target && ["INPUT", "SELECT", "TEXTAREA"].includes(event.target.tagName)) return;
      if (event.key === "ArrowLeft" || event.key.toLowerCase() === "a") move(-1);
      if (event.key === "ArrowRight" || event.key.toLowerCase() === "d") move(1);
      if (event.key.toLowerCase() === "b" && !event.ctrlKey && !event.metaKey) {{
        event.preventDefault();
        toggleCurrentBookmark();
        return;
      }}
      const shortcut = (reviewConfig.shortcut || "r").toLowerCase();
      if (event.key.toLowerCase() === shortcut && !event.ctrlKey && !event.metaKey) {{
        event.preventDefault();
        openReviewDialog();
      }}
    }});
    window.addEventListener("resize", () => {{
      syncToolbarHeight();
      applyPreferences();
      saveState();
    }});
    let bookmarkButtonFrame = 0;
    window.addEventListener("scroll", () => {{
      state.activeBlock = null;
      if (bookmarkButtonFrame) return;
      bookmarkButtonFrame = requestAnimationFrame(() => {{
        bookmarkButtonFrame = 0;
        renderBookmarkCurrentButton();
      }});
    }}, {{ passive: true }});

    loadState();
    syncToolbarHeight();
    if (window.ResizeObserver) {{
      new ResizeObserver(syncToolbarHeight).observe(els.toolbar);
    }}
    render();
  </script>
</body>
</html>
"""


def build_reader(config_path: Path, dry_run: bool = False, force_overwrite: bool = False) -> Path | None:
    config = load_config(config_path)
    workspace_root = resolve_workspace_root(config_path, config)
    files, source_dir = discover_files(workspace_root, config)
    output_path = output_path_for(workspace_root, config, force_overwrite)
    print(summarize_build(config_path, workspace_root, source_dir, files, output_path, config))
    if dry_run:
        print("Dry run: no files were written.")
        return None

    data = {
        "title": config["title"],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_dir": str(config["source_dir"]),
        "chapters": build_chapters(workspace_root, source_dir, files, config),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_document(data, config), encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a single-file local Markdown/TXT review reader.")
    parser.add_argument("config", nargs="?", default="config/workspace.config.md", help="Path to a config markdown file")
    parser.add_argument("--dry-run", action="store_true", help="Show matched files without writing reader.html")
    parser.add_argument("--overwrite", action="store_true", help="Force overwrite even when config overwrite is false")
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    try:
        output_path = build_reader(config_path, dry_run=args.dry_run, force_overwrite=args.overwrite)
    except ConfigError as error:
        print(f"Config error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"File error: {error}", file=sys.stderr)
        return 3
    if output_path:
        print(f"Generated {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
