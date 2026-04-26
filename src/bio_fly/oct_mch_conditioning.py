from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
import yaml

from .paths import DEFAULT_OUTPUT_ROOT


@dataclass(frozen=True)
class OctMchCondition:
    name: str
    cs_plus_odor: str
    cs_minus_odor: str
    unconditioned_stimulus: str
    cs_plus_side: str
    cs_plus_intensity: float
    cs_minus_intensity: float
    training_epochs: int
    memory_phase: str
    mb_perturbation: str
    expected_behavior: str
    biological_question: str


def build_oct_mch_conditioning_table() -> pd.DataFrame:
    conditions = [
        OctMchCondition(
            name="oct_sucrose_appetitive_wt",
            cs_plus_odor="OCT_3-octanol",
            cs_minus_odor="MCH_4-methylcyclohexanol",
            unconditioned_stimulus="sucrose_reward",
            cs_plus_side="left",
            cs_plus_intensity=1.0,
            cs_minus_intensity=1.0,
            training_epochs=3,
            memory_phase="acute_memory",
            mb_perturbation="wild_type_connectome",
            expected_behavior="approach_CS_plus",
            biological_question="baseline appetitive odor memory with OCT as rewarded odor",
        ),
        OctMchCondition(
            name="mch_sucrose_appetitive_wt_counterbalanced",
            cs_plus_odor="MCH_4-methylcyclohexanol",
            cs_minus_odor="OCT_3-octanol",
            unconditioned_stimulus="sucrose_reward",
            cs_plus_side="right",
            cs_plus_intensity=1.0,
            cs_minus_intensity=1.0,
            training_epochs=3,
            memory_phase="acute_memory",
            mb_perturbation="wild_type_connectome",
            expected_behavior="approach_CS_plus",
            biological_question="odor identity counterbalance to separate memory from odor-specific bias",
        ),
        OctMchCondition(
            name="oct_shock_aversive_wt",
            cs_plus_odor="OCT_3-octanol",
            cs_minus_odor="MCH_4-methylcyclohexanol",
            unconditioned_stimulus="electric_shock",
            cs_plus_side="left",
            cs_plus_intensity=1.0,
            cs_minus_intensity=1.0,
            training_epochs=3,
            memory_phase="acute_memory",
            mb_perturbation="wild_type_connectome",
            expected_behavior="avoid_CS_plus",
            biological_question="aversive memory should reverse the sign of CS+ approach",
        ),
        OctMchCondition(
            name="oct_sucrose_left_mb_silenced",
            cs_plus_odor="OCT_3-octanol",
            cs_minus_odor="MCH_4-methylcyclohexanol",
            unconditioned_stimulus="sucrose_reward",
            cs_plus_side="left",
            cs_plus_intensity=1.0,
            cs_minus_intensity=1.0,
            training_epochs=3,
            memory_phase="acute_memory",
            mb_perturbation="left_MB_gain_0.25",
            expected_behavior="reduced_or_shifted_CS_plus_approach",
            biological_question="test whether left MB feedback contributes to appetitive memory stability",
        ),
        OctMchCondition(
            name="oct_sucrose_right_mb_silenced",
            cs_plus_odor="OCT_3-octanol",
            cs_minus_odor="MCH_4-methylcyclohexanol",
            unconditioned_stimulus="sucrose_reward",
            cs_plus_side="right",
            cs_plus_intensity=1.0,
            cs_minus_intensity=1.0,
            training_epochs=3,
            memory_phase="acute_memory",
            mb_perturbation="right_MB_gain_0.25",
            expected_behavior="altered_output_or_choice_bias",
            biological_question="test whether right DAN-MBON output axis controls expression bias",
        ),
        OctMchCondition(
            name="oct_sucrose_mb_symmetrized",
            cs_plus_odor="OCT_3-octanol",
            cs_minus_odor="MCH_4-methylcyclohexanol",
            unconditioned_stimulus="sucrose_reward",
            cs_plus_side="left",
            cs_plus_intensity=1.0,
            cs_minus_intensity=1.0,
            training_epochs=3,
            memory_phase="acute_memory",
            mb_perturbation="left_right_MB_weights_averaged",
            expected_behavior="reduced_lateralization_index",
            biological_question="causal control for structural asymmetry rather than total MB strength",
        ),
        OctMchCondition(
            name="oct_sucrose_mb_swapped",
            cs_plus_odor="OCT_3-octanol",
            cs_minus_odor="MCH_4-methylcyclohexanol",
            unconditioned_stimulus="sucrose_reward",
            cs_plus_side="left",
            cs_plus_intensity=1.0,
            cs_minus_intensity=1.0,
            training_epochs=3,
            memory_phase="acute_memory",
            mb_perturbation="left_right_MB_weights_swapped",
            expected_behavior="reversed_lateralization_prediction",
            biological_question="strongest in-silico causal test for MB lateralization mechanism",
        ),
        OctMchCondition(
            name="weak_oct_strong_mch_conflict",
            cs_plus_odor="OCT_3-octanol",
            cs_minus_odor="MCH_4-methylcyclohexanol",
            unconditioned_stimulus="sucrose_reward",
            cs_plus_side="left",
            cs_plus_intensity=0.35,
            cs_minus_intensity=1.0,
            training_epochs=3,
            memory_phase="retrieval_under_sensory_conflict",
            mb_perturbation="wild_type_connectome",
            expected_behavior="memory_dependent_CS_plus_rescue",
            biological_question="test whether memory can overcome weaker immediate sensory plume",
        ),
    ]
    return pd.DataFrame.from_records([asdict(condition) for condition in conditions])


def write_oct_mch_conditioning_plan(output_dir: Path = DEFAULT_OUTPUT_ROOT / "oct_mch_conditioning") -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    table = build_oct_mch_conditioning_table()
    csv_path = output_dir / "oct_mch_condition_table.csv"
    yaml_path = output_dir / "oct_mch_condition_table.yaml"
    report_path = output_dir / "OCT_MCH_CONDITIONING_PLAN_CN.md"
    metadata_path = output_dir / "suite_metadata.json"
    table.to_csv(csv_path, index=False)
    yaml_path.write_text(yaml.safe_dump(table.to_dict(orient="records"), sort_keys=False, allow_unicode=True), encoding="utf-8")
    report_path.write_text(
        f"""# OCT/MCH 嗅觉条件化记忆实验计划

保存路径：`{report_path}`

## 目的

这一组配置把“闻到了什么”明确写成经典果蝇嗅觉条件化气味：`OCT_3-octanol` 和 `MCH_4-methylcyclohexanol`。每个条件都有 `CS+`、`CS-`、`US`、左右摆放、蘑菇体扰动和预期行为，后续可以直接接入 FlyGym 行为仿真或真实果蝇行为实验。

## 关键变量

- `CS+`：训练时与 unconditioned stimulus 配对的气味。若 `US=sucrose_reward`，测试时应趋近 CS+；若 `US=electric_shock`，测试时应回避 CS+。
- `CS-`：训练时未与 US 配对的对照气味。
- `US`：unconditioned stimulus，即不需要学习就有生物意义的刺激。这里包括糖奖励 `sucrose_reward` 和电击惩罚 `electric_shock`。
- `OCT_3-octanol`：经典果蝇嗅觉记忆实验常用气味之一。
- `MCH_4-methylcyclohexanol`：经典对照气味之一。
- `mb_perturbation`：蘑菇体左右侧化扰动，包括左侧抑制、右侧抑制、左右平均化和左右互换。

## 条件表

{table.to_string(index=False)}

## 输出

- CSV 条件表：`{csv_path}`
- YAML 条件表：`{yaml_path}`

## 下一步如何接入仿真

当前 FlyGym 行为层已经能放置两个气味源，并用 `cs_plus_intensity`、`cs_minus_intensity`、`cs_plus_side` 表示条件化气味竞争。下一步需要把 `cs_plus_odor` 和 `cs_minus_odor` 接到更具体的 ORN/PN/KC sensory encoder，而不是只作为视频标签。这样才能从“两个抽象气味源”升级为“OCT/MCH 气味身份特异性输入”。
""",
        encoding="utf-8",
    )
    paths = {"csv": csv_path, "yaml": yaml_path, "report": report_path}
    metadata_path.write_text(json.dumps({k: str(v) for k, v in paths.items()}, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["metadata"] = metadata_path
    return paths

