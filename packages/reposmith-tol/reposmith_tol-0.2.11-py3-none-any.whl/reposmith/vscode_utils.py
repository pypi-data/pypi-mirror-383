from __future__ import annotations

import json
import os
from pathlib import Path

from .core.fs import write_file


def get_python_interpreter_path(project_root: Path) -> str:
    """
    Return the Python interpreter path for Visual Studio Code.

    If a virtual environment exists at `.venv`, prefer its interpreter.
    Otherwise, fall back to 'python.exe' on Windows or 'python3' elsewhere.
    """
    venv = project_root / ".venv"
    if os.name == "nt":
        venv_python = venv / "Scripts" / "python.exe"
        fallback = "python.exe"
    else:
        venv_python = venv / "bin" / "python"
        fallback = "python3"

    return str(venv_python) if venv_python.exists() else fallback


def update_vscode_files(project_root: Path, main_file: str = "main.py", *, force: bool = False) -> None:
    """
    Create or update VS Code files under .vscode/ and project.code-workspace.
    """
    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)

    interpreter = get_python_interpreter_path(project_root)

    # settings.json
    settings = {
        "python.defaultInterpreterPath": interpreter,
        "python.analysis.typeCheckingMode": "basic",
    }
    write_file(vscode_dir / "settings.json", json.dumps(settings, indent=2) + "\n", force=force)

    # launch.json
    launch = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Run Entry",
                "type": "python",
                "request": "launch",
                "program": f"{Path(main_file).name}",
                "console": "integratedTerminal",
                "python": interpreter,
            }
        ],
    }
    write_file(vscode_dir / "launch.json", json.dumps(launch, indent=2) + "\n", force=force)

    # workspace
    workspace = {
        "folders": [{"path": "."}],
        "settings": {"python.defaultInterpreterPath": interpreter},
    }
    write_file(project_root / "project.code-workspace", json.dumps(workspace, indent=2) + "\n", force=force)

    print("VS Code files updated: settings.json, launch.json, project.code-workspace")


def create_vscode_files(
    project_root: Path,
    venv_path: Path | None = None,
    *,
    main_file: str = "main.py",
    force: bool = False,
) -> None:
    """
    Backward-compatible entrypoint for creating VS Code configuration.

    Historically accepted:
        create_vscode_files(project_root, venv_path, main_file="main.py", force=False)
    """
    # اختر المفسّر: فضّل venv_path إن توفر وكان صالحًا، وإلا fallback
    if venv_path is not None:
        if os.name == "nt":
            candidate = venv_path / "Scripts" / "python.exe"
        else:
            candidate = venv_path / "bin" / "python3"
        interpreter = str(candidate) if candidate.exists() else get_python_interpreter_path(project_root)
    else:
        interpreter = get_python_interpreter_path(project_root)

    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)

    # settings.json
    settings = {
        "python.defaultInterpreterPath": interpreter,
        "python.analysis.typeCheckingMode": "basic",
    }
    write_file(vscode_dir / "settings.json", json.dumps(settings, indent=2) + "\n", force=force)

    # launch.json (الاختبار يريد اسم الملف فقط)
    launch = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Run Entry",
                "type": "python",
                "request": "launch",
                "program": f"{Path(main_file).name}",
                "console": "integratedTerminal",
                "python": interpreter,
            }
        ],
    }
    write_file(vscode_dir / "launch.json", json.dumps(launch, indent=2) + "\n", force=force)

    # project.code-workspace
    workspace = {
        "folders": [{"path": "."}],
        "settings": {"python.defaultInterpreterPath": interpreter},
    }
    write_file(project_root / "project.code-workspace", json.dumps(workspace, indent=2) + "\n", force=force)

    print("VS Code files updated: settings.json, launch.json, project.code-workspace")
