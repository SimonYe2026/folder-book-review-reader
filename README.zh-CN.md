# 本地 Markdown/TXT 审阅阅读器

[English README](README.md)

一个本地优先的小工具，用来阅读和审阅一个文件夹里的 Markdown/TXT 文件。

它会把文件夹打包成一个自包含的 `reader.html`。你可以在浏览器里像读一本书一样连续阅读多个文件，按关键词形成临时书单，标记段落，并导出按文件分组的 `review.md`，交给 AI 或作为人工修改清单继续处理。

默认界面是中文：`locale: zh-CN`。英文界面保留在 `config/workspace.en.config.md`。

## 适合什么场景

当你手里有很多本地 Markdown/TXT 文件，例如草稿、AI 输出、笔记、转换后的文档、项目说明文件，并且想要：

- 连续阅读，而不修改源文件；
- 搜索并只在当前筛选结果里翻篇；
- 阅读时收集批复；
- 把 `review.md` 交给 AI，或自己按清单修改；
- 修改源文件后重新打包检查整体结果；

这个工具就适合使用。

阅读器本身不调用 AI、不修改源文件、不合并 AI 返回结果。

## 运行要求

- Python 3.10 或更高版本。
- 不需要 `pip install`。
- 不需要 npm。
- 不需要前端框架。

核心阅读器只使用 Python 标准库。

## 快速开始

生成默认中文 demo：

```powershell
python build_reader.py
```

打开：

```text
output/reader.html
```

默认命令会读取 `config/workspace.config.md`。

你也可以把配置文件放在脚本旁边，并显式传入：

```powershell
python build_reader.py workspace.config.md
```

本仓库两种方式都保留了：根目录的 `workspace.config.md` 是单配置示例，`config/` 是多配置 demo 组织方式。

生成英文界面 demo：

```powershell
python build_reader.py config/workspace.en.config.md
```

可选本地预览：

```powershell
python serve_reader.py
```

## 配置路径规则

路径以 `workspace_root` 为基准解析。

如果没有设置 `workspace_root`，默认就是配置文件所在目录。

两种配置摆放方式都可以。

简单单配置项目：

```yaml
workspace_root: .
source_dir: ./examples/basic/drafts
output: ./output/reader.html
```

集中配置文件夹：

```yaml
workspace_root: ..
source_dir: ./examples/basic/drafts
output: ./output/reader.html
```

`source_dir` 和 `output` 都必须留在 `workspace_root` 内。这样把脚本复制到别的项目时，读取范围和输出范围会更清楚。

本仓库采用集中配置方式，是因为我们有多个 demo 和文档配置。对只有一个配置的小项目来说，把 `workspace.config.md` 放在 `build_reader.py` 旁边仍然完全可以。

## 预期工作流

```text
收集或生成 Markdown/TXT 文件
  -> 打包 reader.html
  -> 本地阅读、筛选、审阅
  -> 复制或下载 review.md
  -> 把 review.md 交给 AI，或作为人工修改清单
  -> 在阅读器外修改源文件
  -> 重新打包 reader.html 检查结果
```

## 功能

- 读取配置目录下的 `.md` 和 `.txt` 文件。
- 生成单文件 `reader.html`。
- 不修改源文件。
- 支持标题、文件名、相对路径、正文搜索。
- 上一篇/下一篇基于当前筛选结果跳转。
- 支持字体大小、阅读宽度、主题、左右栏拖拽宽度。
- 支持 TXT 段落模式配置。
- 支持 UI 文案 labels 配置。
- 支持选中文本或段落加入批复。
- 批复保存到 `localStorage`。
- 支持按文件分组导出 `review.md`。

## 不做什么

- 不调用 AI API。
- 不从浏览器写回源文件。
- 不自动合并 AI 返回结果。
- 不依赖 React、Vue、npm 或前端构建链。
- 不在浏览器中直接解析 Office/PDF。
- 不承诺复杂 DOCX 版式完全还原。

## 在线 Demo

GitHub Pages 已启用：

- 中文基础 demo：`https://simonye2026.github.io/folder-book-review-reader/examples/generated/basic-reader.demo.html`
- 英文基础 demo：`https://simonye2026.github.io/folder-book-review-reader/examples/generated/basic-reader.en.demo.html`
- 中文项目文档 demo：`https://simonye2026.github.io/folder-book-review-reader/examples/generated/project-docs.demo.html`
- 英文项目文档 demo：`https://simonye2026.github.io/folder-book-review-reader/examples/generated/project-docs.en.demo.html`

同样的浏览器可打开示例也提交在 `examples/generated/`。

## 嵌入到其他项目

最小集成只需要复制：

- `build_reader.py`
- 按目标项目修改后的 `workspace.config.md`

可选复制：

- `serve_reader.py`：用于本地预览。
- `tools/convert_docs.py`：用于 DOCX 转换路径。
- `tests/smoke_test.py`：用于回归检查。

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

## 可选转换器

核心阅读器只接受 Markdown/TXT。

如果要处理非 Markdown/TXT 的来源，建议先转成 Markdown/TXT：

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

## 开发与发布维护

修改或发布前运行 smoke test：

```powershell
python tests/smoke_test.py
```

单独检查已生成 HTML 的页面质量：

```powershell
python tests/html_quality_check.py
```

刷新已提交的 demo HTML：

```powershell
python tools/build_demos.py
```

`output/` 是日常本地构建目录，不应提交。公开 demo HTML 放在 `examples/generated/`。

GitHub Actions 会在 push 和 pull request 时运行 smoke test。

## 安全提示

生成的 HTML 会包含源文件正文。如果源文件有敏感内容，不要公开分享生成的 `reader.html`。

浏览器阅读器不会写回源文件。

Markdown 链接默认禁用。TXT 内容会被转义。嵌入 JSON 做了脚本安全处理。图片 data URL 只允许常见 raster 格式。

即便有这些防护，也不建议打包来路不明的 Markdown/TXT 文件，也不建议对来路不明的 Office 文档运行可选转换器。陌生文本文件请先用普通文本编辑器检查。

## 许可证

MIT License。详见 `LICENSE`。

## 更多文档

- `docs/01-project-status.zh-CN.md` / `docs/01-project-status.en.md`：项目状态、边界和非目标。
- `docs/02-release-checklist.zh-CN.md` / `docs/02-release-checklist.en.md`：发布检查和测试覆盖。
- `docs/03-customization-guide.zh-CN.md` / `docs/03-customization-guide.en.md`：自定义指南。
- `docs/04-user-manual.zh-CN.md` / `docs/04-user-manual.en.md`：用户手册、快捷键、审阅板和导出流程。
- `docs/05-security-notes.zh-CN.md` / `docs/05-security-notes.en.md`：安全模型和不可信输入说明。
- `docs/06-developer-guide.zh-CN.md` / `docs/06-developer-guide.en.md`：代码架构和扩展建议。
