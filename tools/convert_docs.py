#!/usr/bin/env python3
"""
Optional DOCX-to-Markdown converter for the local review reader.

Converts .docx files into Markdown files that can be packaged by build_reader.py.
The converter never modifies source documents.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


SUPPORTED_EXTS = {".docx"}
NOISE_TOKENS = (
    "Root Entry",
    "Normal.dotm",
    "LibreOffice",
    "AppVersion",
    "Default Paragraph Font",
)


class ConversionError(Exception):
    pass


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    cleaned: list[str] = []
    blank = False
    for line in lines:
        if not line:
            if not blank and cleaned:
                cleaned.append("")
            blank = True
            continue
        cleaned.append(line)
        blank = False
    return "\n".join(cleaned).strip() + "\n"


def looks_like_content(line: str) -> bool:
    if len(line) < 4:
        return False
    if any(token in line for token in NOISE_TOKENS):
        return False
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", line))
    latin_count = len(re.findall(r"[A-Za-z]", line))
    if cjk_count >= 4:
        return True
    if latin_count >= 12 and " " in line:
        return True
    return False


def strip_leading_noise(text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return text
    first_content = next((line for line in lines if line.strip()), "")
    if first_content.startswith(("status:", "---", "#")) or looks_like_content(first_content):
        return text
    for index, line in enumerate(lines):
        if looks_like_content(line):
            return "\n".join(lines[index:])
    return text


def clean_converted_text(text: str) -> str:
    text = normalize_text(text)
    text = strip_leading_noise(text)
    lines = [
        line
        for line in text.splitlines()
        if not any(token in line for token in NOISE_TOKENS)
    ]
    return normalize_text("\n".join(lines))


def normalize_markdown(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()]
    cleaned: list[str] = []
    blank_count = 0
    for line in lines:
        if line:
            cleaned.append(line)
            blank_count = 0
        elif cleaned and blank_count < 1:
            cleaned.append("")
            blank_count += 1
    return "\n".join(cleaned).strip() + "\n"


def extract_docx(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            document_xml = archive.read("word/document.xml")
            try:
                rels_xml = archive.read("word/_rels/document.xml.rels")
            except KeyError:
                rels_xml = b""
            related_images: dict[str, tuple[str, bytes]] = {}
            if rels_xml:
                rels_root = ET.fromstring(rels_xml)
                for relation in rels_root:
                    if not relation.attrib.get("Type", "").endswith("/image"):
                        continue
                    rel_id = relation.attrib.get("Id", "")
                    target = relation.attrib.get("Target", "")
                    archive_path = posixpath.normpath(posixpath.join("word", target))
                    try:
                        data = archive.read(archive_path)
                    except KeyError:
                        continue
                    mime = mimetypes.guess_type(archive_path)[0] or "application/octet-stream"
                    related_images[rel_id] = (mime, data)
    except KeyError as exc:
        raise ConversionError(f"{path.name}: missing word/document.xml") from exc
    except zipfile.BadZipFile as exc:
        raise ConversionError(f"{path.name}: invalid docx file") from exc

    root = ET.fromstring(document_xml)
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    blocks: list[str] = []

    def text_from_node(node: ET.Element) -> str:
        parts: list[str] = []
        for item in node.iter():
            tag = item.tag.rsplit("}", 1)[-1]
            if tag == "t":
                parts.append(item.text or "")
            elif tag == "tab":
                parts.append("\t")
            elif tag in {"br", "cr"}:
                parts.append("\n")
        return "".join(parts)

    def paragraph_style(node: ET.Element) -> str:
        style = node.find("./w:pPr/w:pStyle", ns)
        if style is None:
            return ""
        return style.attrib.get(f"{{{ns['w']}}}val", "")

    def image_placeholder(node: ET.Element) -> str:
        drawing = node.find(".//w:drawing", ns)
        if drawing is None:
            return ""
        props = drawing.find(".//wp:docPr", ns)
        alt = ""
        if props is not None:
            alt = props.attrib.get("descr") or props.attrib.get("title") or props.attrib.get("name") or ""
        alt = (alt or "Word 文档内嵌图片").replace("]", "")
        blip = drawing.find(".//a:blip", ns)
        rel_id = blip.attrib.get(f"{{{ns['r']}}}embed", "") if blip is not None else ""
        image = related_images.get(rel_id)
        if image:
            mime, data = image
            encoded = base64.b64encode(data).decode("ascii")
            return f"![{alt}](data:{mime};base64,{encoded})"
        return f"> [图片：{alt}]"

    def property_enabled(properties: ET.Element | None, name: str) -> bool:
        if properties is None:
            return False
        item = properties.find(f"w:{name}", ns)
        if item is None:
            return False
        value = item.attrib.get(f"{{{ns['w']}}}val", "true").lower()
        return value not in {"0", "false", "none", "off"}

    def run_markdown(run: ET.Element) -> str:
        value = text_from_node(run)
        if not value:
            return ""
        properties = run.find("./w:rPr", ns)
        if properties is None:
            return value
        if property_enabled(properties, "b"):
            value = f"**{value}**"
        if property_enabled(properties, "i"):
            value = f"*{value}*"
        if property_enabled(properties, "u"):
            value = f"++{value}++"
        highlight = properties.find("./w:highlight", ns)
        if highlight is not None and highlight.attrib.get(f"{{{ns['w']}}}val", "none") != "none":
            value = f"=={value}=="
        color = properties.find("./w:color", ns)
        color_value = color.attrib.get(f"{{{ns['w']}}}val", "") if color is not None else ""
        if re.fullmatch(r"[0-9A-Fa-f]{6}", color_value) and color_value.lower() not in {"000000", "ffffff"}:
            value = f"{{{{color:{color_value}}}}}{value}{{{{/color}}}}"
        size = properties.find("./w:sz", ns)
        size_value = size.attrib.get(f"{{{ns['w']}}}val", "") if size is not None else ""
        if size_value.isdigit() and int(size_value) < 20:
            value = f"{{{{small}}}}{value}{{{{/small}}}}"
        return value

    def inline_from_paragraph(node: ET.Element) -> str:
        runs = node.findall(".//w:r", ns)
        return "".join(run_markdown(run) for run in runs)

    def paragraph_markdown(node: ET.Element) -> str:
        text = text_from_node(node).strip("\n")
        if not text.strip():
            return image_placeholder(node)
        style = paragraph_style(node)
        heading = re.fullmatch(r"Heading([1-6])", style, flags=re.IGNORECASE)
        if heading:
            return f"{'#' * int(heading.group(1))} {inline_from_paragraph(node).strip()}"
        if style.lower().startswith("code"):
            return f"```text\n{text}\n```"
        if style.lower().startswith("listnumber"):
            indent = "  " if style[-1:].isdigit() and style[-1] != "1" else ""
            return f"{indent}1. {inline_from_paragraph(node).strip()}"
        if style.lower().startswith("listbullet"):
            indent = "  " if style[-1:].isdigit() and style[-1] != "1" else ""
            return f"{indent}- {inline_from_paragraph(node).strip()}"
        return inline_from_paragraph(node).strip()

    def table_markdown(node: ET.Element) -> str:
        nested_tables = node.findall(".//w:tbl", ns)
        if nested_tables:
            def table_structure(table: ET.Element) -> dict[str, object]:
                structured_rows: list[list[dict[str, object]]] = []
                for row in table.findall("./w:tr", ns):
                    structured_cells: list[dict[str, object]] = []
                    for cell in row.findall("./w:tc", ns):
                        texts = [inline_from_paragraph(paragraph).strip() for paragraph in cell.findall("./w:p", ns)]
                        structured_cells.append({
                            "text": [value for value in texts if value],
                            "tables": [table_structure(child) for child in cell.findall("./w:tbl", ns)],
                        })
                    structured_rows.append(structured_cells)
                return {"rows": structured_rows}

            payload = json.dumps(table_structure(node), ensure_ascii=False, separators=(",", ":"))
            return f"```docx-table\n{payload}\n```"

        rows: list[list[str]] = []
        for row in node.findall("./w:tr", ns):
            cells: list[str] = []
            for cell in row.findall("./w:tc", ns):
                paragraphs = [inline_from_paragraph(paragraph).strip() for paragraph in cell.findall("./w:p", ns)]
                paragraphs = [paragraph for paragraph in paragraphs if paragraph]
                value = "<br>".join(paragraphs).replace("|", "\\|").replace("\n", "<br>")
                cells.append(value)
            if any(cells):
                rows.append(cells)
        if not rows:
            return ""
        width = max(len(row) for row in rows)
        padded = [row + [""] * (width - len(row)) for row in rows]
        rendered = ["| " + " | ".join(row) + " |" for row in padded]
        rendered.insert(1, "| " + " | ".join(["---"] * width) + " |")
        return "\n".join(rendered)

    body = root.find("w:body", ns)
    if body is None:
        return ""

    for child in body:
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            block = paragraph_markdown(child)
            if block:
                if not blocks and not block.startswith(("#", ">", "```", "1. ", "- ")):
                    block = f"# {block}"
                blocks.append(block)
        elif tag == "tbl":
            block = table_markdown(child)
            if block:
                blocks.append(block)

    return normalize_markdown("\n\n".join(blocks))


def convert_file(path: Path, output_dir: Path, base_dir: Path | None = None) -> Path:
    if path.suffix.lower() != ".docx":
        raise ConversionError(f"Unsupported extension: {path.suffix}. Current OSS converter supports .docx only.")

    if base_dir:
        relative = path.relative_to(base_dir)
        output_path = output_dir / relative.parent / f"{path.name}.md"
    else:
        output_path = output_dir / f"{path.name}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(extract_docx(path), encoding="utf-8")
    return output_path


def iter_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path] if input_path.suffix.lower() in SUPPORTED_EXTS and not input_path.name.startswith("~$") else []
    files = [
        path
        for path in input_path.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTS and not path.name.startswith("~$")
    ]
    return sorted(files, key=lambda item: item.as_posix().lower())


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert .docx files to Markdown for the review reader.")
    parser.add_argument("input", help="Source .docx file or folder")
    parser.add_argument("-o", "--output-dir", default="examples/conversion-fixtures/converted", help="Output folder")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any file fails")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    files = iter_inputs(input_path)
    if not files:
        print(f"No .docx files found in {input_path}")
        return 1

    failures = 0
    base_dir = input_path if input_path.is_dir() else None
    for file_path in files:
        try:
            output_path = convert_file(file_path, output_dir, base_dir)
            print(f"OK  {file_path.name} -> {output_path}")
        except ConversionError as exc:
            failures += 1
            print(f"ERR {exc}", file=sys.stderr)

    if failures and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
