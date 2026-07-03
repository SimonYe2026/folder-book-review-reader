#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEMOS = [
    ("config/workspace.config.md", ROOT / "output" / "reader.html", ROOT / "examples" / "generated" / "basic-reader.demo.html"),
    ("config/workspace.en.config.md", ROOT / "output" / "reader.en.html", ROOT / "examples" / "generated" / "basic-reader.en.demo.html"),
    ("config/workspace.docs.config.md", ROOT / "output" / "project-docs.html", ROOT / "examples" / "generated" / "project-docs.demo.html"),
    ("config/workspace.docs.en.config.md", ROOT / "output" / "project-docs.en.html", ROOT / "examples" / "generated" / "project-docs.en.demo.html"),
]


def run_build(config: str) -> None:
    subprocess.run(
        [sys.executable, "build_reader.py", config, "--overwrite"],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    for config, source, target in DEMOS:
        run_build(config)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        print(f"Updated {target.relative_to(ROOT)} from {config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
