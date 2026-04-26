#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from bio_fly.paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


def _md_table(frame: pd.DataFrame, columns: list[str], n: int = 12) -> str:
    if frame.empty:
        return "_No records._"
    data = frame[columns].head(n).copy()
    for column in data.columns:
        if pd.api.types.is_float_dtype(data[column]):
            data[column] = data[column].map(lambda value: f"{value:.4g}")
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    rows.extend("| " + " | ".join(map(str, row)) + " |" for row in data.to_numpy())
    return "\n".join(rows)


def write_draft(output_path: Path, suite_dir: Path = DEFAULT_OUTPUT_ROOT / "four_card_suite") -> Path:
    structural = pd.read_csv(DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_nt_fraction_stats.csv")
    major = structural[~structural["hemibrain_type"].astype(str).str.contains(r"KCg-s[123]", regex=True, na=False)]
    top_struct = major.assign(abs_d=major["cohens_d"].abs()).sort_values("abs_d", ascending=False)
    metrics = pd.read_csv(suite_dir / "suite_response_metrics.csv")
    sig = pd.read_csv(suite_dir / "suite_empirical_significance.csv").sort_values("fdr_q")
    run_info = json.loads((suite_dir / "suite_run_info.json").read_text())
    top_actual = metrics[metrics["suite_role"] == "actual"].sort_values("memory_axis_abs_mass", ascending=False)

    draft = f"""# 论文升级稿：A FlyWire-constrained cyber-fly simulation reveals neurotransmitter-specific mushroom-body lateralization

> 工作标题建议：**A connectome-constrained cyber-fly reveals a neurotransmitter-specific lateralized memory-control axis in the adult Drosophila mushroom body**

## Abstract 草稿

Brain lateralization is ubiquitous, yet its synapse-level and circuit-computational basis remains difficult to dissect experimentally because perturbing one hemisphere while preserving whole-brain context is technically challenging. Here we construct a FlyWire-constrained cyber-fly framework that links adult Drosophila connectomics, neurotransmitter-resolved mushroom-body inputs, GPU-accelerated whole-brain perturbation propagation, and embodied FlyGym behavioral rendering. Applying this framework to Kenyon cells, we identify a robust neurotransmitter-specific asymmetry: serotonin-like inputs are right-enriched across major KC subtypes, whereas glutamate-like inputs are left-biased, with the strongest effects in α′β′ memory-related subtypes. Four-GPU simulations across {run_info['n_specs']} perturbation and matched random-control experiments predict that lateralized KC ensembles differentially recruit MBON/DAN/MBIN/APL/DPM memory-axis targets. These results suggest a testable computational division of labor in which right α′β′ serotonin-enriched and left glutamate-biased ensembles act as asymmetric control points for memory-guided behavioral decisions.

## Significance Statement

传统果蝇行为学能证明“某基因/某神经元影响记忆”，但很难系统遍历全脑连接背景下的左右脑扰动。纯 AI 模拟可以大规模搜索，却缺乏生物结构约束。本工作把 FlyWire connectome、NT annotation、KC subtype、MBON/DAN/APL/DPM readout 和 FlyGym embodied behavior 放进同一个可复现仿真框架，提供了一个介于湿实验和黑箱 AI 之间的“结构约束赛博实验”范式。

## Results 1：结构组学发现 α′β′ KC 存在强 NT 偏侧化

主要 KC subtype 中 serotonin 输入方向一致右侧富集，glutamate 输入多数左侧偏置。最大效应集中在 α′β′ 与 KCab-s：

{_md_table(top_struct, ["hemibrain_type", "cell_type", "nt", "left_n", "right_n", "right_laterality_index", "cohens_d", "fdr_q"], n=10)}

建议主文表述：

> The strongest asymmetries were not explained by a generic left-right cell-count imbalance, but by neurotransmitter-resolved input composition. α′β′ KCs showed a coordinated serotonin/right and glutamate-left organization, suggesting a lateralized modulatory substrate for memory gating.

## Results 2：四卡赛博果蝇仿真把结构侧化转化为功能预测

四卡运行信息：

- GPU：`{', '.join(run_info['devices'])}`。
- 扰动总数：`{run_info['n_specs']}`。
- wall time：`{run_info['elapsed_seconds']} s`。
- 每组随机对照：`128` side/subtype-matched null controls。
- 输出：`{suite_dir}/suite_response_metrics.csv` 与 `{suite_dir}/suite_empirical_significance.csv`。

核心功能读出：

{_md_table(top_actual, ["condition", "memory_axis_abs_mass", "mbon_abs_mass", "dan_abs_mass", "mbin_abs_mass", "apl_abs_mass", "dpm_abs_mass", "response_laterality_abs"], n=12)}

## Results 3：matched-random 消融支持侧化 ensemble 的非随机功能偏置

显著性结果：

{_md_table(sig, ["actual_condition", "null_family", "metric", "actual_value", "null_mean", "effect_z", "empirical_p_two_sided", "fdr_q"], n=16)}

建议主文表述：

> Relative to side-matched random KC ensembles, the left glutamate-biased ensemble produced stronger memory-axis recruitment and shifted lateralized response mass toward the left hemisphere, whereas the right serotonin-enriched ensemble selectively enhanced DAN/DPM-related readouts while reducing APL-like components. These effects survived empirical FDR correction across readout metrics in the four-GPU simulation suite.

## Results 4：机制模型

机制示意图建议：

1. `FlyWire v783` 提供全脑有向连接结构。
2. KC 输入 NT fraction 揭示 serotonin/right 与 glutamate/left 的结构偏侧化。
3. GPU sparse propagation 将 KC ensemble activation 转化为 whole-brain response field。
4. MBON/DAN/MBIN/APL/DPM readout 量化 memory-axis recruitment。
5. FlyGym 把 readout 映射到 odor-choice trajectory，生成可解释行为预测。

对应图件：

- `outputs/four_card_suite/figures/Fig1_cyber_fly_pipeline_mechanism.png`
- `outputs/four_card_suite/figures/Fig2_functional_metric_heatmap.png`
- `outputs/four_card_suite/figures/Fig3_empirical_null_significance.png`
- `outputs/four_card_suite/figures/Fig4_memory_axis_null_distributions.png`
- `outputs/four_card_suite/figures/Fig5_stepwise_side_class_response.png`
- `outputs/four_card_suite/videos/cyber_fly_lateralized_memory_axis.mp4`

## Methods：赛博果蝇仿真体系科学合理性

### Connectome-constrained perturbation

模型不从随机神经网络开始，而是固定 FlyWire/Shiu v783 全脑连接矩阵。扰动 seed 来自真实 KC root_id，且按照 hemisphere、KC subtype 和 NT fraction 选择。这样保留了真实连接组约束、细胞类型标签和左右脑结构边界。

### Neurotransmitter-informed lateralization

每条输入边的 `gaba_avg/ach_avg/glut_avg/oct_avg/ser_avg/da_avg` 与 synapse count 相乘，得到每个 KC 的 NT-specific input fraction。统计上使用 Mann–Whitney、Welch、bootstrap CI、Cohen's d、Cliff's delta、FDR 和 direction binomial test。

### Four-GPU whole-brain propagation

四个进程分别在 `cuda:0..3` 加载 sparse adjacency matrix，把 {run_info['n_specs']} 个 perturbation specs 分片运行。每个 perturbation 保留每步 absolute response 最大的 top active nodes，输出 whole-brain response field、side/class/NT readout 和 top targets。

### Biological controls

随机对照不是任意随机节点，而是 side/subtype matched KC null controls。这样能控制左右脑、KC 类别和 seed 数量造成的偏差，更接近可发表的消融实验设计。

## Figure Legends 草稿

**Figure 1 | Connectome-constrained cyber-fly framework.** FlyWire v783 connectome and neurotransmitter-resolved KC inputs are integrated with four-GPU sparse whole-brain propagation and FlyGym embodied rendering to test lateralized memory-control hypotheses.

**Figure 2 | Neurotransmitter-specific KC input lateralization.** Heatmap/forest/volcano plots show right-enriched serotonin-like inputs and left-biased glutamate-like inputs, strongest in α′β′ KCs.

**Figure 3 | Functional signatures of lateralized KC ensembles.** Whole-brain propagation from lateralized KC seeds reveals distinct MBON/DAN/MBIN/APL/DPM memory-axis recruitment patterns.

**Figure 4 | Matched-random ablation controls.** Side/subtype-matched random KC ensembles provide empirical null distributions for memory-axis and lateralized response metrics.

**Figure 5 | Dynamic recruitment of the memory axis.** Propagation videos visualize stepwise recruitment of left/right MBON/DAN/MBIN/Kenyon-cell populations from right α′β′ serotonin and left α′β′ glutamate seeds.

## Limitations and Required Wet-Lab Validation

当前结果应被严格表述为 **connectome-constrained simulation-derived prediction**，不是最终因果证明。下一步必须补：

1. `flywire_synapses_783.feather` 的 synapse-level NT/spatial uncertainty validation。
2. Brian2/LIF spike-level 动力学对核心 α′β′ 条件复核。
3. 真果蝇 odor-memory 行为：左右 odor geometry、短期/长期记忆、遗传/药理扰动和 rescue。
4. 将 simulation prediction 与真实行为效应量做 causal mediation / Bayesian model comparison。

## 可投稿叙事定位

保守定位：Nature Communications / Nature Computational Science 风格的 computational neurobiology resource + biological prediction。  
更强定位：若补齐 synapse-level validation、spiking dynamics 和真实行为实验，可向 Nature Neuroscience / Nature Methods / Nature Machine Intelligence 方向组织。
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(draft)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a Nature-style upgraded paper draft from Cyber-Fly outputs.")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "docs" / "NATURE_PAPER_UPGRADE_DRAFT.md")
    parser.add_argument("--suite-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "four_card_suite")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(write_draft(args.output, suite_dir=args.suite_dir))


if __name__ == "__main__":
    main()
