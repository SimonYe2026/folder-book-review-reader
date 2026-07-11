# 自定义指南

本文件说明后来者可以怎样修改这个项目，以及修改时应避免破坏哪些边界。

对应英文文件：`03-customization-guide.en.md`

## 最小心智模型

这个项目只有三层：

```text
配置文件
  -> Python 构建脚本
  -> 自包含 HTML 阅读器
```

配置文件决定读哪里、怎么排序、界面文案和批复选项。

Python 脚本负责扫描文件、转换 Markdown/TXT/CSV、生成 HTML。

HTML 阅读器负责浏览器里的阅读、筛选、翻页、批复和导出。

## 嵌入到现有项目

这个工具不要求用户采用本仓库的完整目录结构。

如果只是想把阅读器能力接入自己的项目，最小做法是：

```text
复制 build_reader.py
复制 workspace.template.config.md，并改名为 workspace.config.md
如果配置文件不在项目根目录，把 workspace_root 指向项目根目录
把 source_dir 指向自己的 md/txt/csv 文件夹
把 output 指向自己的输出目录
运行 python build_reader.py path/to/workspace.config.md
```

如果不需要 DOCX 转换器，就不必复制 `tools/convert_docs.py`。

如果不需要本地 HTTP 预览，也不必复制 `serve_reader.py`。

嵌入后的推荐工作流是：

```text
任意来源文件
  -> 打包成 reader.html
  -> 人审阅并产生 review.md
  -> AI 根据 review.md 修改或生成新版本
  -> 再次打包 reader.html 检查结果
```

## 常见自定义点

### 改源目录

建议从 `workspace.template.config.md` 复制出自己的 `workspace.config.md`，然后修改：

```yaml
workspace_root: .
source_dir: ./examples/basic/drafts
recursive: true
include:
  - "*.md"
  - "*.txt"
  - "*.csv"
exclude:
  - "*private*"
```

`workspace_root` 默认是配置文件所在目录。`source_dir` 会从 `workspace_root` 解析，并且必须留在它里面。

两种方式都有效。只有一个配置的小项目，可以把 `workspace.config.md` 放在 `build_reader.py` 旁边，并使用 `workspace_root: .` 或直接省略它。如果你把配置文件放在子目录，可以让 `workspace_root` 指回项目根目录：

```yaml
workspace_root: ..
source_dir: ./docs
output: ./output/reader.html
```

本仓库采用子目录方式，是因为它有多个可直接使用的配置文件放在 `config/` 下。这适合多配置项目，但不是每个用户都必须这样组织。

### 为多个批次打包审阅范围

多个配置不仅可以服务多个文件夹，也可以服务同一项目的多个审阅批次。面对几十或九十多份材料时，这种分包让协调者不必把一个压缩包和一串目录说明交给审阅者，而是直接交付可浏览、可筛选、可精确批复的审阅包。例如，可以为不同主题、角色或交付范围分别准备配置，并输出不同的 HTML：

```yaml
workspace_root: ..
source_dir: ./review-batches/batch-a
include:
  - "*.md"
  - "*.txt"
  - "*.csv"
output: ./output/batch-a.reader.html
```

审阅者打开分配给自己的包，导出 `review.md` 后交回中心。这样形成的是完整的多方审阅协作：多人贡献带文件、位置和引用的结构化批复，中心或后续 AI 负责汇总和修改，而不要求审阅者接触源目录或修改源文件。

一个实用的协作约定可以是：每个包有明确的批次或轮次；每份回执带审阅者和批次标识；中心在截止时间后统一收集 `review.md` 并按文件或问题整理。少量人员可以用简单表格或约定管理。

这是一种打包前的展示范围控制，不是运行时权限系统。任何拿到 `reader.html` 的人都能看到其中嵌入的内容；不应分发的内容必须在打包前排除。

### 改输出路径

```yaml
output: ./output/reader.html
overwrite: false
```

`output` 同样从 `workspace_root` 解析，并且必须留在它里面。

当 `overwrite: false` 且目标文件已存在时，脚本会生成带时间戳的新文件。

### 改界面语言

```yaml
locale: zh-CN
```

或：

```yaml
locale: en
```

也可以用 `labels:` 覆盖单个文案。

### 改批复动作和目标

```yaml
review:
  enabled: true
  actions:
    - 修改
    - 总结
    - 提取
    - 登记
  targets:
    - 原文段落
    - 审阅队列
    - 笔记
    - 待办清单
```

这些字段不需要程序理解成复杂枚举。它们最终会进入导出的 `review.md`，供用户或 AI 理解。

### 改 TXT 分段方式

```yaml
text:
  paragraph_mode: line
```

可选：

- `line`：一行一个可批复段落。
- `blank_line`：空行分段。

## 转换器扩展

核心阅读器承诺 `.md` / `.txt` / `.csv`。

CSV 会作为表格型章节展示，支持全文搜索和按行批复，但不在浏览器里编辑源 CSV。

如果要支持更多格式，建议增加独立转换器：

```text
source.docx
  -> tools/convert_docs.py
  -> converted/source.docx.md
  -> build_reader.py
```

不要让浏览器直接解析本地 Office/PDF 文件。

## 渲染规则扩展

可以在 `build_reader.py` 中扩展 Markdown 渲染规则。

建议优先保持：

- 输出 HTML 安全。
- 链接默认不激活。
- 复杂结构失败时回退为可读文本。
- 不让单个坏文件中断整个项目。

## 审阅导出扩展

导出的 `review.md` 可以被改成团队需要的格式。

修改位置在 HTML 内嵌 JavaScript 的 `reviewMarkdown()` 逻辑。

建议保留：

- 文件路径。
- 标题。
- 段落编号。
- 动作。
- 目标。
- 引用原文。
- 用户批复。
- 创建时间。

这些字段能让 AI 或人工后续处理更容易定位上下文。

## 不建议改的边界

不建议在第一波自定义中加入：

- 浏览器写回源文件。
- 自动调用 AI API。
- 自动合并 AI 修改。
- 后台服务依赖。
- npm 前端构建链。
- 复杂图表库。

这些都可以另开分支探索，但不适合塞进这个小工具的默认路径。

## 一个好的自定义版本应该是什么样

一个好的自定义版本应该：

- 仍然一条命令可构建。
- 仍然不修改源文件。
- 仍然能用 smoke test 验证核心路径。
- README 写清楚自己改了什么。
- 示例文件能让陌生人快速理解用途。
