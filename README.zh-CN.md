# 本地 Markdown/TXT 审阅阅读器

一个本地优先的小工具，用来把一个文件夹里的 Markdown/TXT 文件打包成可阅读、可筛选、可批复的单文件 HTML。

它会生成一个自包含的 `reader.html`，可直接在浏览器中打开。阅读器支持搜索、筛选后翻页、布局调整、深色模式，以及可导出 `review.md` 的本地审阅板。

默认界面为中文：`locale: zh-CN`。英文作为国际化配置保留在 `workspace.en.config.md`。

## 快速开始

```powershell
python build_reader.py workspace.config.md
```

英文界面示例：

```powershell
python build_reader.py workspace.en.config.md
```

打开：

```text
output/reader.html
```

可选本地预览：

```powershell
python serve_reader.py
```

运行 smoke test：

```powershell
python tests/smoke_test.py
```

生成说明文档阅读器：

```powershell
python build_reader.py workspace.docs.config.md
```

打开：

```text
output/project-docs.html
```

如果想先直接查看效果，可以打开 `examples/generated/` 中选择性提交的静态示例：

- `examples/generated/basic-reader.demo.html`
- `examples/generated/project-docs.demo.html`

## 功能

- 读取配置目录下的 `.md` 和 `.txt` 文件。
- 生成单文件 `reader.html`。
- 不修改源文件。
- 支持标题、路径、文件名、正文搜索。
- 上一篇/下一篇基于当前筛选结果跳转。
- 支持字体大小、阅读宽度、主题、左右栏拖拽宽度。
- 支持目录栏和审阅板折叠。
- 支持 TXT 段落模式配置。
- 支持 UI 文案 labels 配置。
- 支持选中文本或段落加入批复。
- 批复保存到 `localStorage`。
- 支持按文件分组导出 `review.md`。
- Markdown 链接默认禁用，避免启用不可信链接。

## 预期工作流

```text
从任意工作流生成或收集文件
  -> 用本脚本打包 reader.html
  -> 本地阅读、筛选、审阅
  -> 复制或下载 review.md
  -> 把 review.md 交给 AI，或作为人工修改清单
  -> 由 AI 或用户在阅读器外修改源文件
  -> 再次打包 reader.html，检查修改后的整体结果
```

阅读器本身不调用 AI，也不修改源文件。它只生成一份旁路批复文件，方便 AI 或人工继续处理。

## 嵌入到其他项目

这个仓库可以作为完整 demo 使用，但核心工具刻意保持很小，适合被复制到别人的项目里。

最小集成只需要复制：

- `build_reader.py`
- 按目标项目修改后的 `workspace.config.md`

可选复制：

- `serve_reader.py`：用于本地预览。
- `tools/convert_docs.py`：用于 DOCX 转换路径。
- `tests/smoke_test.py`：用于回归检查。

宿主项目可以保留自己的文档、AI 输出、草稿或批复文件。阅读器只需要一个配置好的源目录和输出路径。

推荐嵌入流程：

```text
你的项目文件
  -> build_reader.py
  -> 本地 reader.html
  -> 人工审阅
  -> review.md
  -> AI 在阅读器外辅助修改
  -> 重新打包 reader.html
```

## 不做什么

- 不调用 AI API。
- 不从浏览器写回源文件。
- 不自动合并 AI 返回结果。
- 不依赖 React、Vue、npm 或前端构建链。
- 不在浏览器中直接解析 Office/PDF。
- 不承诺复杂 DOCX 版式完全还原。

## 可选转换器

核心阅读器只接受 Markdown/TXT。

如果要处理非 Markdown/TXT 的来源，建议先通过可选转换器转成 Markdown/TXT：

```text
原始文档 -> 转换器 -> md/txt -> build_reader.py -> reader.html
```

当前质量分级：

- `.docx`：当前推荐的可选转换路径。
- `.doc` / `.rtf` / `.pdf` / `.epub`：后续扩展方向，不是当前承诺。

当前转换器命令：

```powershell
python tools/convert_docs.py examples/conversion-fixtures/source -o examples/conversion-fixtures/converted
```

## 安全提示

生成的 HTML 会包含源文件正文。如果源文件有敏感内容，不要公开分享生成的 `reader.html`。

浏览器阅读器不会写回源文件。

项目已经做了链接禁用、TXT 转义渲染、嵌入 JSON 安全转义、图片 data URL 限制等防护。即便如此，也不建议打包来路不明的 Markdown/TXT 文件，也不建议对来路不明的 Office 文档运行可选转换器。陌生文本文件请先用普通文本编辑器检查。

## 许可证

MIT License。详见 `LICENSE`。

## 更多文档

- `docs/01-project-status.zh-CN.md` / `docs/01-project-status.en.md`：项目状态、边界和非目标。
- `docs/02-release-checklist.zh-CN.md` / `docs/02-release-checklist.en.md`：发布检查和测试覆盖。
- `docs/03-customization-guide.zh-CN.md` / `docs/03-customization-guide.en.md`：面向后来者的自定义指南。
- `docs/04-user-manual.zh-CN.md` / `docs/04-user-manual.en.md`：用户手册、快捷键、审阅板和导出流程。
- `docs/05-security-notes.zh-CN.md` / `docs/05-security-notes.en.md`：安全模型、已有防护和不可信输入说明。
- `docs/06-developer-guide.zh-CN.md` / `docs/06-developer-guide.en.md`：代码架构、扩展顺序、框架判断和回归要求。
