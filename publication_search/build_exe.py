"""Utility helpers to bundle the Publication Scout app as a Windows executable."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_pyinstaller() -> str:
    """Return the pyinstaller executable path or exit with a helpful error."""

    pyinstaller = shutil.which("pyinstaller")
    if pyinstaller:
        return pyinstaller
    raise SystemExit(
        "PyInstaller 未安装。请先运行 `pip install pyinstaller` 或"
        " `pip install -r requirements-publication.txt` 安装依赖。"
    )


def build() -> Path:
    """Invoke PyInstaller to create a standalone executable."""

    project_dir = Path(__file__).resolve().parent
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"

    # Clean previous builds so repeated executions start from a known state.
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    pyinstaller = ensure_pyinstaller()

    data_file = project_dir / "data_sources.json"
    data_spec = f"{data_file}{os.pathsep}publication_search"

    cmd = [
        pyinstaller,
        "--name",
        "PublicationScout",
        "--onefile",
        "--noconfirm",
        "--clean",
        "--collect-all",
        "streamlit",
        "--collect-all",
        "altair",
        "--add-data",
        data_spec,
        str(project_dir / "__main__.py"),
    ]

    subprocess.check_call(cmd, cwd=project_dir)

    exe_name = "PublicationScout.exe" if sys.platform.startswith("win") else "PublicationScout"
    exe_path = dist_dir / exe_name
    if not exe_path.exists():
        raise FileNotFoundError(
            "未能找到生成的可执行文件。请检查 PyInstaller 输出以排查问题。"
        )

    return exe_path


def main() -> None:
    exe_path = build()
    print(f"✅ 打包完成：{exe_path}")


if __name__ == "__main__":
    main()
