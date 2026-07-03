# 可选工具

这个目录用于存放可选的前置处理工具。

核心阅读器不依赖任何转换器。它可以直接读取 Markdown 和 TXT 文件。

可能的后续工具：

- `convert_docs.py`：当前推荐的 `.docx` 到 Markdown 转换路径。
- 打包前脱敏。
- 转换文档的段落归一化。

这些工具应和阅读器核心保持分离，让主项目仍然容易运行。

## 转换夹具

```powershell
python tools/convert_docs.py examples/conversion-fixtures/source -o examples/conversion-fixtures/converted
```

质量说明：

- `.docx` 是当前推荐路径。
- 转换器会尽量保留标题、列表、段落断点、表格、代码块、字符画、常见行内格式，以及 DOCX 结构能暴露出来的嵌入图片。
- 嵌入图片会写成 data URL，让生成后的阅读器仍然保持自包含。
- 它不复刻 Word 分页、浮动对象位置或所有 Word 样式。
- `.doc`、`.rtf`、PDF 和 EPUB 不属于当前 OSS 转换器范围。

## English

## Optional Tools

This directory is reserved for optional preprocessors.

The core reader does not require any converter. It reads Markdown and TXT files directly.

Potential future tools:

- `convert_docs.py`: recommended `.docx` to Markdown conversion.
- Desensitization before packaging.
- Paragraph normalization for converted documents.

Keep these tools separate from the reader core so the main project remains easy to run.

## Convert Fixtures

```powershell
python tools/convert_docs.py examples/conversion-fixtures/source -o examples/conversion-fixtures/converted
```

Quality note:

- `.docx` is the current recommended path.
- The converter preserves headings, lists, paragraph breaks, tables, code blocks, character art, common inline formatting, and embedded images where the DOCX structure exposes them.
- Embedded images are written as data URLs so the generated reader can remain self-contained.
- It does not reproduce Word pagination, floating-object placement, or every Word style.
- `.doc`, `.rtf`, PDF, and EPUB are not part of the current OSS converter.
