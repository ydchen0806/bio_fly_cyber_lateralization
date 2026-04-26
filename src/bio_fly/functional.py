from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re

import pandas as pd

from .paths import DEFAULT_COMPLETENESS_PATH, DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT
from .propagation import (
    PropagationConfig,
    build_torch_propagation_graph,
    load_connectivity_edges,
    response_overlap,
    signed_multihop_response,
    signed_multihop_response_torch,
    summaries_to_frame,
    summarize_response,
)
from .repro import default_config, load_external_model, make_smoke_params


SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9_.-]+")


@dataclass(frozen=True)
class PerturbationSpec:
    exp_name: str
    pair_token: str
    label: str
    condition: str
    activate_ids: tuple[int, ...]
    silence_ids: tuple[int, ...] = ()
    readout_ids: tuple[int, ...] = ()


def safe_experiment_name(*parts: object) -> str:
    text = "_".join(str(part) for part in parts if str(part))
    return SAFE_NAME_PATTERN.sub("_", text).strip("_")


def load_pairwise_candidates(pairwise_path: Path) -> pd.DataFrame:
    pairwise = pd.read_csv(pairwise_path)
    required_columns = {"pair_token", "left_root_id", "right_root_id"}
    missing = required_columns - set(pairwise.columns)
    if missing:
        raise ValueError(f"pairwise table is missing columns: {sorted(missing)}")
    metric_columns = [
        column
        for column in ["out_laterality", "in_laterality", "signed_out_laterality"]
        if column in pairwise.columns
    ]
    if metric_columns:
        pairwise["candidate_score"] = pairwise[metric_columns].abs().max(axis=1)
    else:
        pairwise["candidate_score"] = 0.0
    return pairwise.sort_values("candidate_score", ascending=False).reset_index(drop=True)


def build_perturbation_specs(pairwise: pd.DataFrame, top_n: int = 10) -> list[PerturbationSpec]:
    specs: list[PerturbationSpec] = []
    candidates = pairwise.head(top_n)
    for _, row in candidates.iterrows():
        pair_token = str(row["pair_token"])
        label = str(row.get("label", "unknown"))
        left_id = int(row["left_root_id"])
        right_id = int(row["right_root_id"])
        pair_stub = safe_experiment_name(pair_token)
        specs.extend(
            [
                PerturbationSpec(
                    exp_name=safe_experiment_name(pair_stub, "left_activate"),
                    pair_token=pair_token,
                    label=label,
                    condition="left_activate",
                    activate_ids=(left_id,),
                    readout_ids=(right_id,),
                ),
                PerturbationSpec(
                    exp_name=safe_experiment_name(pair_stub, "right_activate"),
                    pair_token=pair_token,
                    label=label,
                    condition="right_activate",
                    activate_ids=(right_id,),
                    readout_ids=(left_id,),
                ),
                PerturbationSpec(
                    exp_name=safe_experiment_name(pair_stub, "left_activate_silence_right"),
                    pair_token=pair_token,
                    label=label,
                    condition="left_activate_silence_right",
                    activate_ids=(left_id,),
                    silence_ids=(right_id,),
                ),
                PerturbationSpec(
                    exp_name=safe_experiment_name(pair_stub, "right_activate_silence_left"),
                    pair_token=pair_token,
                    label=label,
                    condition="right_activate_silence_left",
                    activate_ids=(right_id,),
                    silence_ids=(left_id,),
                ),
            ]
        )
    return specs


def specs_to_frame(specs: list[PerturbationSpec]) -> pd.DataFrame:
    records = []
    for spec in specs:
        record = asdict(spec)
        record["activate_ids"] = ";".join(map(str, spec.activate_ids))
        record["silence_ids"] = ";".join(map(str, spec.silence_ids))
        record["readout_ids"] = ";".join(map(str, spec.readout_ids))
        records.append(record)
    return pd.DataFrame.from_records(records)


def run_signed_propagation_validation(
    specs: list[PerturbationSpec],
    connectivity_path: Path = DEFAULT_CONNECTIVITY_PATH,
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "functional_validation",
    config: PropagationConfig | None = None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = config or PropagationConfig()
    edges = load_connectivity_edges(connectivity_path)

    response_frames: list[pd.DataFrame] = []
    summaries = []
    for spec in specs:
        response = signed_multihop_response(
            edges=edges,
            seed_ids=spec.activate_ids,
            silence_ids=spec.silence_ids,
            config=config,
        )
        response["exp_name"] = spec.exp_name
        response["pair_token"] = spec.pair_token
        response["condition"] = spec.condition
        response_frames.append(response)
        summaries.append(
            summarize_response(
                condition=spec.condition,
                seed_ids=spec.activate_ids,
                silence_ids=spec.silence_ids,
                readout_ids=spec.readout_ids,
                response=response,
            )
        )

    summary_frame = summaries_to_frame(summaries)
    response_frame = pd.concat(response_frames, ignore_index=True) if response_frames else pd.DataFrame()
    overlap_frame = compute_pairwise_response_overlap(response_frame)

    summary_path = output_dir / "signed_propagation_summary.csv"
    response_path = output_dir / "signed_propagation_responses.parquet"
    overlap_path = output_dir / "left_right_response_overlap.csv"
    summary_frame.to_csv(summary_path, index=False)
    response_frame.to_parquet(response_path, index=False)
    overlap_frame.to_csv(overlap_path, index=False)
    return {"summary": summary_path, "responses": response_path, "overlap": overlap_path}


def run_torch_signed_propagation_validation(
    specs: list[PerturbationSpec],
    connectivity_path: Path = DEFAULT_CONNECTIVITY_PATH,
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "functional_validation",
    config: PropagationConfig | None = None,
    device: str = "cuda",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = config or PropagationConfig()
    graph = build_torch_propagation_graph(connectivity_path=connectivity_path, device=device)

    response_frames: list[pd.DataFrame] = []
    summaries = []
    for spec in specs:
        response = signed_multihop_response_torch(
            graph=graph,
            seed_ids=spec.activate_ids,
            silence_ids=spec.silence_ids,
            config=config,
        )
        response["exp_name"] = spec.exp_name
        response["pair_token"] = spec.pair_token
        response["condition"] = spec.condition
        response_frames.append(response)
        summaries.append(
            summarize_response(
                condition=spec.condition,
                seed_ids=spec.activate_ids,
                silence_ids=spec.silence_ids,
                readout_ids=spec.readout_ids,
                response=response,
            )
        )

    summary_frame = summaries_to_frame(summaries)
    response_frame = pd.concat(response_frames, ignore_index=True) if response_frames else pd.DataFrame()
    overlap_frame = compute_pairwise_response_overlap(response_frame)

    summary_path = output_dir / "signed_propagation_summary.csv"
    response_path = output_dir / "signed_propagation_responses.parquet"
    overlap_path = output_dir / "left_right_response_overlap.csv"
    summary_frame.to_csv(summary_path, index=False)
    response_frame.to_parquet(response_path, index=False)
    overlap_frame.to_csv(overlap_path, index=False)
    return {"summary": summary_path, "responses": response_path, "overlap": overlap_path}


def compute_pairwise_response_overlap(response_frame: pd.DataFrame) -> pd.DataFrame:
    if response_frame.empty:
        return pd.DataFrame(columns=["pair_token", "top200_jaccard"])
    records: list[dict[str, object]] = []
    for pair_token, pair_response in response_frame.groupby("pair_token", sort=False):
        left_response = pair_response[pair_response["condition"] == "left_activate"]
        right_response = pair_response[pair_response["condition"] == "right_activate"]
        if left_response.empty or right_response.empty:
            continue
        records.append(
            {
                "pair_token": pair_token,
                "top200_jaccard": response_overlap(left_response, right_response, top_n=200),
            }
        )
    return pd.DataFrame.from_records(records)


def run_lif_specs(
    specs: list[PerturbationSpec],
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "lif_validation",
    t_run_ms: int = 50,
    n_run: int = 1,
    rate_hz: int = 120,
    max_experiments: int = 2,
    force_overwrite: bool = False,
) -> list[Path]:
    from brian2 import Hz, ms, prefs

    prefs.codegen.target = "numpy"
    model = load_external_model()
    params = make_smoke_params()
    params["t_run"] = t_run_ms * ms
    params["n_run"] = n_run
    params["r_poi"] = rate_hz * Hz

    config = default_config(output_dir=output_dir)
    config["path_comp"] = str(DEFAULT_COMPLETENESS_PATH)
    config["path_con"] = str(DEFAULT_CONNECTIVITY_PATH)
    config["n_proc"] = 1
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths: list[Path] = []
    for spec in specs[:max_experiments]:
        model.run_exp(
            exp_name=spec.exp_name,
            neu_exc=list(spec.activate_ids),
            neu_slnc=list(spec.silence_ids),
            params=params,
            force_overwrite=force_overwrite,
            **config,
        )
        output_paths.append(output_dir / f"{spec.exp_name}.parquet")
    return output_paths
