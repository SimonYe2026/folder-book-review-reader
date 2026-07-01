---
title: 转换器测试文档审阅 Demo
locale: zh-CN
source_dir: ./examples/conversion-fixtures/converted
recursive: false
flatten: true
include:
  - "*.docx.md"
exclude:
  - "__never_match__"
order: natural
output: ./output/reader.converted.html
overwrite: true
display:
  show_file_name: true
  show_word_count: true
  default_font_size: 18
  default_width: full
  theme: light
features:
  search: true
  next_prev: true
  keyboard_nav: true
  reverse_order: true
review:
  enabled: true
  shortcut: r
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
text:
  paragraph_mode: line
labels:
  search_placeholder: 搜索标题、路径或正文
  toc: 目录
  review_panel: 审阅板
  previous: 上一篇
  next: 下一篇
  add_review: 加入批复
  review: 批复
  copy_review: 复制 review.md
  clear: 清空
  download: 下载
tables:
  enabled: true
  sticky_header: true
  horizontal_scroll: true
  copy_button: false
stats:
  enabled: false
  show_file_count: true
  show_word_count: true
  show_folder_distribution: false
  show_ext_distribution: false
---

# 转换器测试文档审阅 Demo

这个配置用于把 `examples/conversion-fixtures/converted/` 里的 DOCX 转换结果打包成独立阅读器。

它的目的不是替代人工抽检，而是让 `.docx -> .md` 的产物进入同一套阅读、搜索、筛选和审阅流程。
