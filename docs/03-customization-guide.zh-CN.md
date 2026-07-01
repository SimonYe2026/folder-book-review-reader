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

Python 脚本负责扫描文件、转换 Markdown/TXT、生成 HTML。

HTML 阅读器负责浏览器里的阅读、筛选、翻页、批复和导出。

## 嵌入到现有项目

这个工具不要求用户采用本仓库的完整目录结构。

如果只是想把阅读器能力接入自己的项目，最小做法是：

```text
复制 build_reader.py
复制或新建 workspace.config.md
把 source_dir 指向自己的 md/txt 文件夹
把 output 指向自己的输出目录
运行 python build_reader.py workspace.config.md
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

在配置文件中修改：

```yaml
source_dir: ./examples/basic/drafts
recursive: true
include:
  - "*.md"
  - "*.txt"
exclude:
  - "*private*"
```

`source_dir` 必须位于配置文件所在目录之内。

### 改输出路径

```yaml
output: ./output/reader.html
overwrite: false
```

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

核心阅读器只承诺 `.md` / `.txt`。

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
