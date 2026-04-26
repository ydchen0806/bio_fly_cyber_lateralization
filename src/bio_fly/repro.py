from __future__ import annotations

import copy
import importlib.util
import os
from pathlib import Path
from types import ModuleType
from typing import Iterable

from .paths import DEFAULT_COMPLETENESS_PATH, DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from .runtime import configure_runtime_cache


SUGAR_NEURON_IDS = [
    720575940624963786,
    720575940630233916,
    720575940637568838,
]


def _load_module(module_name: str, module_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ensure_runtime_cache() -> Path:
    configure_runtime_cache()
    return Path(os.environ["MPLCONFIGDIR"])


def load_external_model(project_root: Path | None = None) -> ModuleType:
    ensure_runtime_cache()
    project_root = project_root or PROJECT_ROOT
    model_path = project_root / "external" / "Drosophila_brain_model" / "model.py"
    return _load_module("bio_fly_external_model", model_path)


def default_config(output_dir: Path | None = None) -> dict[str, object]:
    return {
        "path_res": str(output_dir or (DEFAULT_OUTPUT_ROOT / "repro")),
        "path_comp": str(DEFAULT_COMPLETENESS_PATH),
        "path_con": str(DEFAULT_CONNECTIVITY_PATH),
        "n_proc": 1,
    }


def make_smoke_params() -> dict[str, object]:
    model = load_external_model()
    from brian2 import Hz, ms, prefs

    prefs.codegen.target = "numpy"

    params = copy.deepcopy(model.default_params)
    params["n_run"] = 1
    params["t_run"] = 20 * ms
    params["r_poi"] = 120 * Hz
    return params


def run_smoke_test(
    neuron_ids: Iterable[int] | None = None,
    output_dir: Path | None = None,
    force_overwrite: bool = True,
) -> Path:
    model = load_external_model()
    config = default_config(output_dir=output_dir)
    params = make_smoke_params()
    selected_ids = list(neuron_ids or SUGAR_NEURON_IDS[:1])
    Path(config["path_res"]).mkdir(parents=True, exist_ok=True)
    model.run_exp(
        exp_name="smoke_test",
        neu_exc=selected_ids,
        params=params,
        force_overwrite=force_overwrite,
        **config,
    )
    return Path(config["path_res"]) / "smoke_test.parquet"
