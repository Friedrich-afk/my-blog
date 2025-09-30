"""Executable entry point for running the Publication Scout app."""
from __future__ import annotations

from pathlib import Path

from streamlit.web import bootstrap


def main() -> None:
    """Launch the Streamlit UI programmatically.

    This wrapper allows bundling the application with tools like PyInstaller,
    so that the resulting executable can boot the Streamlit server directly.
    """

    app_path = Path(__file__).resolve().with_name("app.py")
    bootstrap.run(
        str(app_path),
        "streamlit run",
        [],
        flag_options={"server.headless": True},
    )


if __name__ == "__main__":
    main()
