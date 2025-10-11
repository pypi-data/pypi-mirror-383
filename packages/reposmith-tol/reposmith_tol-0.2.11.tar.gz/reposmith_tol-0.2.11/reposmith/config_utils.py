from __future__ import annotations

import json
from pathlib import Path


def load_or_create_config(project_root: Path) -> dict:
    """
    Load setup-config.json if present; otherwise create it with sane defaults.
    """
    cfg_path = project_root / "setup-config.json"
    if cfg_path.exists():
        return json.loads(cfg_path.read_text(encoding="utf-8"))

    defaults = {
        "project_name": project_root.name,
        "main_file": "main.py",
        "entry_point": None,
        "requirements_file": "requirements.txt",
        "venv_dir": ".venv",
        "python_version": "3.12",
        # ✅ expected by tests:
        "license": "MIT",
    }

    cfg_path.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
    print(f"[config] written: {cfg_path}")
    return defaults
