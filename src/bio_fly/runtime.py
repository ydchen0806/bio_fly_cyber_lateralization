from __future__ import annotations

import os
from pathlib import Path

from .paths import PROJECT_ROOT


def configure_runtime_cache(mujoco_gl: str | None = None) -> dict[str, str]:
    cache_root = PROJECT_ROOT / ".cache"
    paths = {
        "MPLCONFIGDIR": cache_root / "matplotlib",
        "XDG_CACHE_HOME": cache_root / "xdg",
        "MESA_SHADER_CACHE_DIR": cache_root / "mesa_shader_cache",
    }
    for env_key, path in paths.items():
        path.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault(env_key, str(path))
    if mujoco_gl:
        os.environ.setdefault("MUJOCO_GL", mujoco_gl)
        if mujoco_gl == "egl":
            os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
    return {key: os.environ[key] for key in paths}
