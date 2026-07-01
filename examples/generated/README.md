# Generated Demo HTML

This folder contains selected browser-ready demo HTML files that are safe to commit.

Routine local build output should stay in `output/` and remain ignored by Git. If a release needs an HTML file that users can open directly without running the build command, copy a freshly generated demo here and document:

- source config;
- build command;
- generation date or release version;
- whether the file contains only public example content.

Current selected demos:

| File | Source config | Build command | Content |
| --- | --- | --- | --- |
| `basic-reader.demo.html` | `workspace.config.md` | `python build_reader.py workspace.config.md --overwrite` | Public bilingual example drafts only. |
| `basic-reader.en.demo.html` | `workspace.en.config.md` | `python build_reader.py workspace.en.config.md --overwrite` | Public bilingual example drafts with English UI labels. |
| `project-docs.demo.html` | `workspace.docs.config.md` | `python build_reader.py workspace.docs.config.md --overwrite` | Public README and docs files with Chinese UI labels. |
| `project-docs.en.demo.html` | `workspace.docs.en.config.md` | `python build_reader.py workspace.docs.en.config.md --overwrite` | Public README and docs files with English UI labels. |

Regenerate and refresh these demos before a release:

```powershell
python build_reader.py workspace.config.md --overwrite
python build_reader.py workspace.en.config.md --overwrite
python build_reader.py workspace.docs.config.md --overwrite
python build_reader.py workspace.docs.en.config.md --overwrite
Copy-Item output/reader.html examples/generated/basic-reader.demo.html
Copy-Item output/reader.en.html examples/generated/basic-reader.en.demo.html
Copy-Item output/project-docs.html examples/generated/project-docs.demo.html
Copy-Item output/project-docs.en.html examples/generated/project-docs.en.demo.html
```

Or run:

```powershell
python tools/build_demos.py
```

Do not put personal review files, private drafts, or temporary test output here.
