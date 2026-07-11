# 本地 Markdown/TXT/CSV 审阅阅读器

[English README](README.md)

一个本地优先的小工具，用来阅读和审阅一个文件夹里的 Markdown/TXT/CSV 文件。

它会把文件夹打包成一个自包含的 `reader.html`。你可以在浏览器里像读一本书一样连续阅读多个文件，按关键词形成临时书单，标记段落，并导出按文件分组的 `review.md`，交给 AI 或作为人工修改清单继续处理。

默认界面是中文：`locale: zh-CN`。英文界面保留在 `config/workspace.en.config.md`。

## 适合什么场景

当你手里有很多本地 Markdown/TXT/CSV 文件，例如草稿、AI 输出、笔记、表格清单、转换后的文档、项目说明文件，并且想要：

- 连续阅读，而不修改源文件；
- 搜索并只在当前筛选结果里翻篇；
- 阅读时收集批复；
- 把 `review.md` 交给 AI，或自己按清单修改；
- 修改源文件后重新打包检查整体结果；

这个工具就适合使用。

阅读器本身不调用 AI、不修改源文件、不合并 AI 返回结果。

## 审阅交接包

当一轮审阅涉及几十份、乃至九十多份材料时，压缩包或网盘目录只能把文件送到对方手里：审阅者仍要自己理解目录、逐份打开、记住位置，再用零散消息反馈。`reader.html` 把这一批材料变成一个可直接打开的审阅现场：连续阅读、搜索筛选、按文件和内容块批复、审阅板复查都在同一个包中完成。

导出的 `review.md` 不是泛泛的意见清单。它保留文件路径、内容块位置、引用原文、动作、目标和说明，因此中心侧能把每条意见带回正确上下文，交给人工维护或外部 AI 工作流继续处理。这个链路解决的是四件事：分发大量文件；集中查看；对具体位置精准批复；回收结构化回执。

这也是多方审阅协作的基础用法：协调者按批次、角色或展示范围分别打包 `reader.html`，审阅者只返回各自的 `review.md`，再由中心或后续 AI 汇总意见并决定修改。协作单位是“定位明确的批复”，不是多人共同编辑源文件或同步同一份浏览器状态。

几位审阅者或小团队可以直接按此方式协作。参与人数、批次数和审阅轮次增加后，可用认领范围、文件命名、审阅者标识、截止时间和集中回收等约定保持交接清楚。阅读器提供的是分包、定位和回执这一层；源文件和最终采纳权始终保留在中心侧。

构建者需要 Python 来生成审阅包，但审阅参与者不需要。审阅参与者只负责阅读、判断、批复和导出 `review.md`；打包、回收归并、AI 处理、源文件修改和最终采纳始终留在中心侧。对方不需要懂 AI、提示词、Python、代码仓库或源目录，也不需要安装项目依赖；收到文件后，用任意现代浏览器打开 `reader.html` 即可。这把复杂文本处理中的参与门槛从“会操作工具链”降到“会打开浏览器并给出判断”。

## 运行要求

- Python 3.10 或更高版本。
- 不需要 `pip install`。
- 不需要 npm。
- 不需要前端框架。

核心阅读器只使用 Python 标准库。

上面的 Python 要求只属于构建者。收到已生成 `reader.html` 的审阅者只需要现代浏览器。

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

多个配置不只适合多个源文件夹，也适合为同一项目准备不同批次或不同展示范围的审阅包。每份配置都可以指定自己的 `source_dir`、匹配规则和 `output`。这使协调者可以按主题、角色、轮次或交付范围发出不同的审阅视图。需要保密的内容不应打包进会分发给审阅者的 HTML；在浏览器里隐藏内容不构成权限控制。

## 预期工作流

```text
收集或生成 Markdown/TXT/CSV 文件
  -> 打包 reader.html
  -> 本地阅读、筛选、审阅
  -> 复制或下载 review.md
  -> 把 review.md 交给 AI，或作为人工修改清单
  -> 在阅读器外修改源文件
  -> 重新打包 reader.html 检查结果
```

## 功能

- 读取配置目录下的 `.md`、`.txt` 和 `.csv` 文件。
- 生成单文件 `reader.html`。
- 不修改源文件。
- 支持标题、文件名、相对路径、正文搜索。
- 支持把 CSV 渲染为 HTML 表格，并按行加入批复。
- 上一篇/下一篇基于当前筛选结果跳转。
- 支持字体大小、阅读宽度、主题、左右栏拖拽宽度。
- 支持 TXT 段落模式配置。
- 支持 UI 文案 labels 配置。
- 支持选中文本或段落加入批复。
- 未选中文本时，书签和批复会定位到正文可视区域中心最近的内容块；CSV 保留当前激活行优先。
- 支持内容块级书签、回跳，以及在书签栏中删除或清空书签。
- 区分精确的选中文本/内容块批复与阅读视口批复，并导出有界的附近上下文，避免后续人工或 AI 只凭一段锚点文字猜测整章意图。
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

然后选择一种配置摆放方式：

- 单配置方式：复制 `workspace.template.config.md`，并改名为 `workspace.config.md`。
- 集中配置方式：复制 `config/workspace.template.config.md`，并改名为 `config/workspace.config.md`。

可选复制：

- `serve_reader.py`：用于本地预览。
- `tools/convert_docs.py`：用于 DOCX 转换路径。
- `tests/smoke_test.py`：用于回归检查。

推荐嵌入流程：

```text
你的项目文件
  -> build_reader.py
  -> workspace.config.md 或 config/workspace.config.md
  -> 本地 reader.html
  -> 人工审阅
  -> review.md
  -> AI 在阅读器外辅助修改
  -> 重新打包 reader.html
```

## 可选转换器

核心阅读器接受 Markdown/TXT/CSV。

如果要处理其他来源，建议先转成 Markdown/TXT/CSV：

```text
原始文档 -> 转换器 -> md/txt/csv -> build_reader.py -> reader.html
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

如果你正在修改前端交互，可以安装开发依赖并运行真实浏览器点击流检查：

```powershell
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/browser_smoke_test.py
```

这个动态脚本会用 Chromium 打开中英文公开 demo，检查筛选与排序、CSV 行和普通内容块批复、无选区时按正文视觉中心定位书签和批复、附近上下文导出、审阅板编辑/复制/下载/删除/清空、批复与书签回跳、localStorage 恢复、阅读偏好、左右栏和窄屏基本可用性。它只是开发检查依赖，不是普通使用 reader 的依赖。

刷新已提交的 demo HTML：

```powershell
python tools/build_demos.py
```

`output/` 是日常本地构建目录，不应提交。公开 demo HTML 放在 `examples/generated/`。

GitHub Actions 会在 push 和 pull request 时运行 smoke test。

## 安全提示

生成的 HTML 会包含源文件正文。如果源文件有敏感内容，不要公开分享生成的 `reader.html`。

浏览器阅读器不会写回源文件。

Markdown 链接默认禁用。TXT 内容会被转义。CSV 单元格会被转义为普通表格文本，公式样内容不会执行。嵌入 JSON 做了脚本安全处理。图片 data URL 只允许常见 raster 格式。

即便有这些防护，也不建议打包来路不明的 Markdown/TXT/CSV 文件，也不建议对来路不明的 Office 文档运行可选转换器。陌生文本文件请先用普通文本编辑器检查。

## 许可证

MIT License。详见 `LICENSE`。

## 更多文档

- `docs/01-project-status.zh-CN.md` / `docs/01-project-status.en.md`：项目状态、边界和非目标。
- `docs/02-release-checklist.zh-CN.md` / `docs/02-release-checklist.en.md`：发布检查和测试覆盖。
- `docs/03-customization-guide.zh-CN.md` / `docs/03-customization-guide.en.md`：自定义指南。
- `docs/04-user-manual.zh-CN.md` / `docs/04-user-manual.en.md`：用户手册、快捷键、审阅板和导出流程。
- `docs/05-security-notes.zh-CN.md` / `docs/05-security-notes.en.md`：安全模型和不可信输入说明。
- `docs/06-developer-guide.zh-CN.md` / `docs/06-developer-guide.en.md`：代码架构和扩展建议。
- `docs/07-review-handoff-workflow.zh-CN.md` / `docs/07-review-handoff-workflow.en.md`：审阅交接、分包与多人回执工作流。
