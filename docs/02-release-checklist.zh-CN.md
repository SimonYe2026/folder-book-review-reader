# 发布检查清单

本文件记录当前版本发布前应完成或确认的检查项。

对应英文文件：`02-release-checklist.en.md`

## 构建检查

- 运行默认中文构建：

```powershell
python build_reader.py workspace.config.md --overwrite
```

- 运行英文界面构建：

```powershell
python build_reader.py workspace.en.config.md --overwrite
```

- 运行转换器样例构建：

```powershell
python build_reader.py workspace.converted.config.md --overwrite
```

- 运行文档状态构建：

```powershell
python build_reader.py workspace.docs.config.md --overwrite
```

- 运行英文界面文档状态构建：

```powershell
python build_reader.py workspace.docs.en.config.md --overwrite
```

- 刷新公开 demo HTML：

```powershell
python tools/build_demos.py
```

## 自动测试

- 运行 smoke test：

```powershell
python tests/smoke_test.py
```

当前 smoke test 覆盖：

- 配置解析。
- Markdown/TXT 基础渲染。
- TXT 渲染不会激活 HTML、Markdown 链接或图片语法。
- Markdown 链接禁用和本地化占位。
- 常见 raster 图片 data URL 仍可显示。
- SVG data image 被禁用。
- 图片 data URL 不被行内格式破坏。
- 坏 `docx-table` 回退为代码块。
- 嵌入 `<script>` 的 JSON 安全转义。
- `dry-run` 不写文件。
- `overwrite: false` 不覆盖已有输出。
- 缺少 `source_dir` 的错误提示。
- 空目录和匹配不到文件的错误提示。
- 主阅读器、英文阅读器、中英文文档阅读器、转换器阅读器构建。
- DOCX 转换器基础质量。
- 递归转换同名文件时不覆盖。
- 选择性提交的生成示例 HTML 存在，并且不包含本地绝对路径或私人批复标记。
- README 中列出的 generated demo 链接都指向已提交文件。

## 手动检查

- 三栏布局在大屏、半屏、窄屏下可用。
- 目录栏和审阅栏折叠后不会遮挡正文。
- 搜索后上一篇/下一篇基于当前筛选结果。
- 字体大小、阅读宽度、主题和栏宽刷新后保留。
- 审阅弹窗可以添加批复。
- Edge 等浏览器出现选中文本迷你菜单时，浮动批复按钮仍可作为 `R` 快捷键的替代入口。
- 审阅板可以编辑、删除、清空批复。
- 复制和下载的 `review.md` 按文件分组。
- 下载的 `review.md` 可以重新打包为普通 Markdown 阅读器。
- 链接占位、图片显示、转换器行内格式在浏览器中看起来正常。

## GitHub Pages 检查

如果启用了 GitHub Pages，推送后打开：

- 中文基础 demo：`https://simonye2026.github.io/folder-book-review-reader/examples/generated/basic-reader.demo.html`
- 英文基础 demo：`https://simonye2026.github.io/folder-book-review-reader/examples/generated/basic-reader.en.demo.html`
- 中文项目文档 demo：`https://simonye2026.github.io/folder-book-review-reader/examples/generated/project-docs.demo.html`
- 英文项目文档 demo：`https://simonye2026.github.io/folder-book-review-reader/examples/generated/project-docs.en.demo.html`

每个公开 demo 至少确认：

- 搜索可用。
- 上一篇/下一篇遵循当前筛选结果。
- 审阅弹窗可打开。
- `review.md` 可以复制或下载。

## 安全检查

- 构建过程不修改源文件。
- 浏览器阅读器不写回源文件。
- Markdown 链接不会生成可点击 `<a href=...>`。
- TXT 内容只做转义展示，不激活 HTML 或 Markdown 语法。
- 生成 HTML 包含源文件内容，README 已提示敏感内容风险。
- 可选转换器只读取源文档并写入转换结果。
- README 和安全说明已提醒：不推荐打包来路不明的 Markdown/TXT，也不推荐对来路不明的 Office 文档运行转换器。

## 当前已知限制

- DOCX 转换器适合基础文本、标题、列表、表格、图片和部分行内样式，不承诺复杂版式。
- 导出的 `review.md` 是批复文本，不是可逆结构文件。
- 复杂图表、字符画、流程图只做普通内容展示，不自动重绘。
- 链接默认不激活，这是安全取舍，不是 Markdown 站点功能。

## 发布前建议

- 不提交日常构建产生的整个 `output/` 目录。
- 如果仓库需要一个可直接打开的 HTML 示例，应选择性提交重新生成的 demo 文件，例如放到 `examples/generated/`，并在文档中写清楚生成命令和来源配置。
- 发布前保持 `examples/generated/basic-reader.demo.html`、`examples/generated/basic-reader.en.demo.html`、`examples/generated/project-docs.demo.html` 和 `examples/generated/project-docs.en.demo.html` 一起刷新。
- 保持测试样例小而可读。
- README 中保留中文为主、英文国际化的说明。
- 不把开发治理日志、个人工作记录放进开源目录。
- 确认 MIT `LICENSE` 文件存在。
- 发布前重新跑一次 smoke test。
