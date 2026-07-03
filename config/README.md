# 配置文件

这个文件夹保存本仓库可直接使用的多套配置。

使用 `config/` 文件夹是可选的。本仓库同时保留了根目录下的 `workspace.config.md`，用于展示更简单的单配置摆放方式。只有一套配置的小项目，可以把 `workspace.config.md` 放在 `build_reader.py` 旁边，然后运行：

```powershell
python build_reader.py workspace.config.md
```

本仓库把多套配置集中放在这里，是因为基础 demo、英文界面、项目文档阅读器和转换文档阅读器是不同的构建目标。

这里的配置都使用：

```yaml
workspace_root: ..
```

这表示即使配置文件放在 `config/` 文件夹里，`source_dir` 和 `output` 这类路径仍然从仓库根目录解析。

常用命令：

```powershell
python build_reader.py
python build_reader.py config/workspace.en.config.md
python build_reader.py config/workspace.docs.config.md
python build_reader.py config/workspace.docs.en.config.md
python build_reader.py config/workspace.converted.config.md
```

## English

This folder contains ready-to-use project configs.

Using a `config/` folder is optional. This repository also keeps a root-level `workspace.config.md` to show the simpler single-config layout. A small project can keep `workspace.config.md` beside `build_reader.py` and run:

```powershell
python build_reader.py workspace.config.md
```

This repository keeps multiple configs here because the demo, English UI, docs reader, and converted-doc reader are separate build targets.

Each config uses:

```yaml
workspace_root: ..
```

That means paths such as `source_dir` and `output` are resolved from the repository root, even though the config files live in this `config/` folder.
