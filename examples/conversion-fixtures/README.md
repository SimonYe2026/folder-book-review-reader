# 转换器测试夹具

测试可选转换器时，可以把复杂的公开源文档放在这里。

建议结构：

```text
examples/conversion-fixtures/
  source/
    sample.docx
  converted/
    sample.docx.md
```

不要提交私人或敏感文档。

核心阅读器不会直接读取这个目录。转换器测试可以使用这里的文件来检查文本提取、段落修复、表格处理和可选脱敏行为。

## 当前夹具

```text
source/
  complex_layout_review_reader_test.docx
converted/
  complex_layout_review_reader_test.docx.md
```

这个夹具用于测试当前推荐的 DOCX 转换路径。它适合检查：

- 段落提取；
- 表格保留；
- 标题识别；
- 可审阅块边界；
- 可选脱敏行为。

重新生成转换结果：

```powershell
python tools/convert_docs.py examples/conversion-fixtures/source -o examples/conversion-fixtures/converted
```

为转换结果构建阅读器：

```powershell
python build_reader.py config/workspace.converted.config.md
```

生成文件为：

```text
output/reader.converted.html
```

## English

## Conversion Fixtures

Put complex source documents here when testing optional converters.

Suggested layout:

```text
examples/conversion-fixtures/
  source/
    sample.docx
  converted/
    sample.docx.md
```

Do not commit private or sensitive documents.

The core reader does not read this directory directly. Converter tests can use it to verify extraction, paragraph repair, table handling, and desensitization behavior.

## Current Fixtures

```text
source/
  complex_layout_review_reader_test.docx
converted/
  complex_layout_review_reader_test.docx.md
```

This fixture is intended to test the current recommended DOCX conversion path. It should be used to test:

- paragraph extraction;
- table preservation;
- heading detection;
- reviewable block boundaries;
- optional desensitization behavior.

Regenerate converted outputs with:

```powershell
python tools/convert_docs.py examples/conversion-fixtures/source -o examples/conversion-fixtures/converted
```

Build a reader for the converted outputs with:

```powershell
python build_reader.py config/workspace.converted.config.md
```

The generated file is:

```text
output/reader.converted.html
```
