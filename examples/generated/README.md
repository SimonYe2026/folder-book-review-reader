# 生成的 Demo HTML

这个文件夹保存可以直接在浏览器打开、并且适合提交到仓库的示例 HTML。

日常本地构建输出应保留在 `output/`，并继续被 Git 忽略。如果发布时需要一个用户无需运行构建命令就能打开的 HTML 示例，应把重新生成后的指定 demo 复制到这里，并说明：

- 来源配置；
- 构建命令；
- 生成日期或发布版本；
- 是否只包含公开示例内容。

当前选定 demo：

| 文件 | 来源配置 | 构建命令 | 内容 |
| --- | --- | --- | --- |
| `examples/generated/basic-reader.demo.html` | `config/workspace.config.md` | `python build_reader.py config/workspace.config.md --overwrite` | 只包含公开的中英双语示例草稿。 |
| `examples/generated/basic-reader.en.demo.html` | `config/workspace.en.config.md` | `python build_reader.py config/workspace.en.config.md --overwrite` | 公开示例草稿，界面标签为英文。 |
| `examples/generated/project-docs.demo.html` | `config/workspace.docs.config.md` | `python build_reader.py config/workspace.docs.config.md --overwrite` | 公开 README 和 docs 文件，界面标签为中文。 |
| `examples/generated/project-docs.en.demo.html` | `config/workspace.docs.en.config.md` | `python build_reader.py config/workspace.docs.en.config.md --overwrite` | 公开 README 和 docs 文件，界面标签为英文。 |

发布前刷新这些 demo：

```powershell
python tools/build_demos.py
```

本仓库也保留了根目录下的 `workspace.config.md` 作为简单单配置示例。也可以显式构建它：

```powershell
python build_reader.py workspace.config.md --overwrite
```

不要把个人批复文件、私人草稿或临时测试输出放到这里。

## English

## Generated Demo HTML

This folder contains selected browser-ready demo HTML files that are safe to commit.

Routine local build output should stay in `output/` and remain ignored by Git. If a release needs an HTML file that users can open directly without running the build command, copy a freshly generated demo here and document:

- source config;
- build command;
- generation date or release version;
- whether the file contains only public example content.

Current selected demos:

| File | Source config | Build command | Content |
| --- | --- | --- | --- |
| `examples/generated/basic-reader.demo.html` | `config/workspace.config.md` | `python build_reader.py config/workspace.config.md --overwrite` | Public bilingual example drafts only. |
| `examples/generated/basic-reader.en.demo.html` | `config/workspace.en.config.md` | `python build_reader.py config/workspace.en.config.md --overwrite` | Public bilingual example drafts with English UI labels. |
| `examples/generated/project-docs.demo.html` | `config/workspace.docs.config.md` | `python build_reader.py config/workspace.docs.config.md --overwrite` | Public README and docs files with Chinese UI labels. |
| `examples/generated/project-docs.en.demo.html` | `config/workspace.docs.en.config.md` | `python build_reader.py config/workspace.docs.en.config.md --overwrite` | Public README and docs files with English UI labels. |

Regenerate and refresh these demos before a release:

```powershell
python tools/build_demos.py
```

The repository also keeps a root-level `workspace.config.md` as a simple single-config example. It is valid to build that explicitly:

```powershell
python build_reader.py workspace.config.md --overwrite
```

Do not put personal review files, private drafts, or temporary test output here.
