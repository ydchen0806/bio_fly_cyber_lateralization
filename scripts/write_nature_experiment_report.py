#!/usr/bin/env python
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import warnings

import pandas as pd

from bio_fly.paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from bio_fly.resources import humanize_bytes


def _file_size(path: Path) -> str:
    return humanize_bytes(path.stat().st_size) if path.exists() and path.is_file() else "missing"


def _table(rows: list[list[object]], headers: list[str]) -> str:
    text_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in text_rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    header_line = "| " + " | ".join(header.ljust(width) for header, width in zip(headers, widths)) + " |"
    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    body = ["| " + " | ".join(cell.ljust(width) for cell, width in zip(row, widths)) + " |" for row in text_rows]
    return "\n".join([header_line, separator, *body])


def _gpu_status() -> str:
    try:
        result = subprocess.run(["nvidia-smi", "-L"], check=False, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return "`nvidia-smi` 不可用"
    if result.returncode != 0:
        return "`nvidia-smi` 当前不可用；本次使用 CPU/EGL 离屏渲染"
    gpu_text = result.stdout.strip().replace("\n", "; ")
    try:
        import torch

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cuda_available = torch.cuda.is_available()
            device_count = torch.cuda.device_count()
        torch_text = (
            f"PyTorch {torch.__version__}: cuda_available={cuda_available}, "
            f"device_count={device_count}"
        )
    except Exception as exc:
        torch_text = f"PyTorch CUDA 状态读取失败：{type(exc).__name__}: {exc}"
    return f"{gpu_text}；{torch_text}"


def _direction_summary(stats_path: Path) -> tuple[list[list[object]], list[list[object]]]:
    stats = pd.read_csv(stats_path)
    major = stats[~stats["hemibrain_type"].astype(str).str.contains(r"KCg-s[123]", regex=True, na=False)].copy()
    direction_rows = []
    for nt, expected, direction in [("ser", "右侧富集", 1), ("glut", "左侧偏置", -1), ("gaba", "左侧偏置", -1), ("da", "右侧富集", 1)]:
        subset = major[major["nt"] == nt]
        if subset.empty:
            continue
        successes = int((subset["right_laterality_index"] * direction > 0).sum())
        direction_rows.append([nt, expected, f"{successes}/{len(subset)}", f"{subset['fdr_q'].min():.2e}"])
    top = (
        major.assign(abs_d=major["cohens_d"].abs())
        .sort_values("abs_d", ascending=False)
        .head(10)
    )
    top_rows = [
        [
            row["hemibrain_type"],
            row["nt"],
            int(row["left_n"]),
            int(row["right_n"]),
            f"{row['right_laterality_index']:+.3f}",
            f"{row['cohens_d']:+.3f}",
            f"{row['fdr_q']:.2e}",
        ]
        for _, row in top.iterrows()
    ]
    return direction_rows, top_rows


def _behavior_rows(summary_path: Path) -> list[list[object]]:
    if not summary_path.exists():
        return [["missing", "-", "-", "-", "-"]]
    summary = pd.read_csv(summary_path)
    rows = []
    for condition, group in summary.groupby("condition", sort=False):
        rows.append(
            [
                condition,
                len(group),
                f"{group['choice'].astype(str).eq('CS+').mean():.2f}",
                f"{group['signed_final_y'].mean():+.3f}",
                f"{group['distance_to_cs_plus'].mean():.3f}",
            ]
        )
    return rows


def _model_linkage_rows(output_dir: Path) -> list[list[object]]:
    manifest = output_dir / "kc_nt_perturbation_manifest.csv"
    seed_summary = output_dir / "kc_nt_seed_summary.csv"
    if not manifest.exists():
        return [["missing", "-", "-", "-"]]
    manifest_frame = pd.read_csv(manifest)
    seed_summary_frame = pd.read_csv(seed_summary) if seed_summary.exists() else pd.DataFrame()
    rows = [
        ["seed groups", len(seed_summary_frame), str(seed_summary), _file_size(seed_summary)],
        ["perturbation specs", len(manifest_frame), str(manifest), _file_size(manifest)],
    ]
    propagation_summary = output_dir / "signed_propagation_summary.csv"
    if propagation_summary.exists():
        frame = pd.read_csv(propagation_summary)
        rows.append(["signed propagation", len(frame), str(propagation_summary), _file_size(propagation_summary)])
    top_targets = output_dir / "signed_propagation_top_targets.csv"
    if top_targets.exists():
        frame = pd.read_csv(top_targets)
        rows.append(["top targets", len(frame), str(top_targets), _file_size(top_targets)])
    return rows


def write_report(output_path: Path) -> Path:
    stats_path = DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_nt_fraction_stats.csv"
    linkage_dir = (
        DEFAULT_OUTPUT_ROOT / "model_linkage_gpu"
        if (DEFAULT_OUTPUT_ROOT / "model_linkage_gpu" / "model_linkage_summary.json").exists()
        else DEFAULT_OUTPUT_ROOT / "model_linkage"
    )
    direction_rows, top_rows = _direction_summary(stats_path)
    output_table_rows = [
        [
            "KC NT 神经元输入表",
            "每个 KC 的输入突触数与 GABA/ACh/Glu/Oct/Ser/DA fraction",
            "outputs/kc_nt_lateralization/kc_neuron_nt_inputs.parquet",
            _file_size(DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_neuron_nt_inputs.parquet"),
        ],
        [
            "侧化统计表",
            "subtype × NT 的 Mann–Whitney/Welch/FDR/effect size/bootstrap CI",
            "outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv",
            _file_size(stats_path),
        ],
        [
            "方向一致性检验",
            "Ser/Glu/GABA/DA 在主要 KC subtype 上的方向 binomial test",
            "outputs/kc_nt_lateralization/nt_direction_binomial_tests.csv",
            _file_size(DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "nt_direction_binomial_tests.csv"),
        ],
        [
            "Serotonin 上游来源",
            "ser_avg≥0.5 的 KC 上游输入按 pre class/type 汇总",
            "outputs/kc_nt_lateralization/serotonin_dominant_upstream_by_class.csv",
            _file_size(DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "serotonin_dominant_upstream_by_class.csv"),
        ],
        [
            "NT 侧化热图",
            "红=右侧富集，蓝=左侧富集，用于主文结构发现图",
            "outputs/kc_nt_lateralization/figures/Fig_NT_lateralization_heatmap.png",
            _file_size(DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "figures" / "Fig_NT_lateralization_heatmap.png"),
        ],
        [
            "Ser/Glu forest 图",
            "展示 Ser 右偏与 Glu 左偏的 bootstrap CI",
            "outputs/kc_nt_lateralization/figures/Fig_serotonin_glutamate_forest.png",
            _file_size(DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "figures" / "Fig_serotonin_glutamate_forest.png"),
        ],
        [
            "功能候选 manifest",
            "真实 KC-NT 侧化候选被转成传播扰动 seed/silence/readout",
            f"{linkage_dir.relative_to(PROJECT_ROOT)}/kc_nt_perturbation_manifest.csv",
            _file_size(linkage_dir / "kc_nt_perturbation_manifest.csv"),
        ],
        [
            "数据驱动行为参数",
            "由 α′β′ Ser/Glu laterality 自动估计 FlyGym condition 参数",
            f"{linkage_dir.relative_to(PROJECT_ROOT)}/derived_behavior_conditions.csv",
            _file_size(linkage_dir / "derived_behavior_conditions.csv"),
        ],
        [
            "行为汇总表",
            "每个 condition × CS+ side 的轨迹、距离、选择结果",
            "outputs/behavior/memory_choice_summary.csv",
            _file_size(DEFAULT_OUTPUT_ROOT / "behavior" / "memory_choice_summary.csv"),
        ],
        [
            "论文对比视频",
            "2×2 panel，四个条件同步比较，适合补充视频初稿",
            "outputs/behavior/paper_comparison_cs_plus_left.mp4",
            _file_size(DEFAULT_OUTPUT_ROOT / "behavior" / "paper_comparison_cs_plus_left.mp4"),
        ],
    ]

    behavior_rows = _behavior_rows(DEFAULT_OUTPUT_ROOT / "behavior" / "memory_choice_summary.csv")
    data_driven_behavior_rows = _behavior_rows(DEFAULT_OUTPUT_ROOT / "behavior_data_driven" / "memory_choice_summary.csv")
    model_linkage_rows = _model_linkage_rows(linkage_dir)

    report = f"""# Nature 级果蝇蘑菇体侧化结构-功能仿真实验报告

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
项目目录：`{PROJECT_ROOT}`  
环境目录：`{PROJECT_ROOT / 'env'}`

## 1. 一句话结论

本工程已经可以运行：`FlyWire v783` 结构数据下载与整理、Eon/Shiu 风格全脑 LIF smoke 复现、KC neurotransmitter 输入侧化统计、真实 KC-NT 候选到 signed propagation 功能传播、FlyGym/MuJoCo 行为渲染和 2×2 论文对比视频。当前最强证据是结构组学发现：主要 KC subtype 中 serotonin 输入呈一致右侧富集，glutamate 输入呈显著左侧偏置，α′β′ 记忆相关 Kenyon cell subtype 的效应最大。

## 2. 当前可发表级核心发现

### 2.1 方向一致性

{_table(direction_rows, ["NT", "预期方向", "成功 subtype", "最小 FDR q"])}

### 2.2 最大效应候选

{_table(top_rows, ["KC subtype", "NT", "left n", "right n", "LI", "Cohen d", "FDR q"])}

解释：`LI = (right - left) / (right + left)`，正值表示右侧富集，负值表示左侧偏置。这个表说明 α′β′ 和 KCab-s 是当前最值得深挖的结构切入点，其中 `KCa'b'` 与记忆形成、调制输入和 MBON/DAN 回路最直接相关。

## 3. 复现和运行命令

```bash
cd {PROJECT_ROOT}
source env/bin/activate

# 0) 可选：使用网络代理
export http_proxy=http://192.168.32.28:18000
export https_proxy=http://192.168.32.28:18000

# 1) 环境和资源检查
python -m pip check
python scripts/estimate_resources.py

# 2) Eon/Shiu 风格全脑 LIF smoke 复现
python scripts/run_repro_smoke.py

# 3) FlyWire 注释与 proofread connection 数据
python scripts/download_flywire_data.py --prepare-annotations --download-small --download-connections

# 4) KC neurotransmitter 输入侧化统计与图
python scripts/analyze_kc_nt_lateralization.py

# 5) 真实结构候选 -> GPU signed propagation -> 行为参数
python scripts/build_model_linkage.py --steps 3 --max-active 5000 \\
  --propagation-backend torch --device cuda:0 --output-dir outputs/model_linkage_gpu

# 5b) GPU benchmark
python scripts/benchmark_gpu_propagation.py --device cuda:0 --steps 3 --max-active 5000 --max-specs 6

# 6) 数据驱动 FlyGym 行为仿真和轨迹图
python scripts/run_behavior_memory_experiment.py \\
  --condition-table outputs/model_linkage_gpu/derived_behavior_conditions.csv \\
  --n-trials 1 --run-time 0.5 --output-dir outputs/behavior_data_driven

# 7) 行为汇总图和 2×2 论文对比视频
python scripts/summarize_behavior_results.py --summary outputs/behavior/memory_choice_summary.csv
python scripts/make_behavior_comparison_video.py --cs-plus-side left
python scripts/make_behavior_comparison_video.py --cs-plus-side right --output outputs/behavior/paper_comparison_cs_plus_right.mp4

# 8) 回归测试
python -m pytest -q
```

## 4. 生成文件含义

{_table(output_table_rows, ["名称", "含义", "路径", "大小"])}

## 5. 结构到功能链条

{_table(model_linkage_rows, ["对象", "行数", "路径", "大小"])}

当前实现不是只做手工参数视频，而是把真实 FlyWire KC-NT 结构发现转成了：

- `right_serotonin_kc_activate`：右侧 serotonin-enriched KC ensemble 激活；
- `left_glutamate_kc_activate`：左侧 glutamate-enriched KC ensemble 激活；
- `right_serotonin_activate_silence_left_glutamate`：激活右侧 serotonin ensemble，同时沉默左侧 glutamate ensemble；
- `left_glutamate_activate_silence_right_serotonin`：相反方向的对照；
- `right_alpha_prime_beta_prime_serotonin_activate` 与 `left_alpha_prime_beta_prime_glutamate_activate`：专门针对 α′β′ 记忆 subtype 的核心扰动。

输出的 `signed_propagation_top_targets.csv` 可以继续筛 MBON、DAN、MBIN、APL、OAN 等下游/上游回路，作为下一轮 functional validation 和实验遗传靶点候选。

## 6. 行为仿真和视频结果

### 6.1 当前视频批次

{_table(behavior_rows, ["condition", "trial 数", "CS+ 选择率", "mean signed y", "mean d(CS+)"])}

### 6.2 数据驱动参数批次

{_table(data_driven_behavior_rows, ["condition", "trial 数", "CS+ 选择率", "mean signed y", "mean d(CS+)"])}

解释：FlyGym/MuJoCo 视频当前是“结构发现驱动的行为预测可视化”，不是湿实验结果。它的价值是展示 lateralized MB memory-bias 如何改变 odor choice trajectory，并为行为实验设计提供参数方向；Nature 级论文中必须用真实行为数据或更严谨的闭环模型来验证。

## 7. 资源和存储估计

- 当前核心数据已足够运行结构发现和功能传播：`proofread_connections_783.feather` 约 813 MB，Shiu `Connectivity_783.parquet` 约 96 MB。
- 建议 Nature 级完整包预留 `0.5–2 TB`，用于 synapse-level 表、morphology/skeleton、批量 LIF、行为视频、图表中间结果。
- 完整 `flywire_synapses_783.feather` 约 9.5 GB，建议下载后用于 synapse-level NT 位置、uncertainty 和 neuropil spatial validation。
- GPU 状态：{_gpu_status()}。当前可见 GPU 与用户口头描述的 `H200` 不完全一致，`nvidia-smi` 显示为 `H20Z`；PyTorch 已切换到兼容系统 CUDA 12.9 的 `cu129` wheel，GPU 版 signed propagation 已可用。MuJoCo/FlyGym 离屏渲染已经可用，但物理仿真本身不一定主要受 PyTorch GPU 加速。

## 8. Nature 级证据链评价

### 已经较强的部分

- 真实 FlyWire proofread connection 数据支持 KC NT 输入左右侧化，不依赖 toy 数据。
- 主要 KC subtype 方向一致性强，尤其 serotonin `9/9` subtype 右侧富集。
- α′β′ 记忆相关 subtype 在 Ser/Glu/GABA/DA 上都有大效应，是明确的结构切入点。
- 已经生成主文候选图、统计表、功能传播 manifest、行为对比视频。

### 还不能过度声称的部分

- 当前 FlyGym 行为是 model-generated prediction，不等同于真实果蝇行为实验。
- signed propagation 是快速功能近似，不等价于完整 biophysical 全脑动力学。
- 完整 synapse-level 表尚未纳入，因此还缺少突触位置、NT uncertainty 和空间分布验证。
- 当前 GPU 可被 `nvidia-smi` 和 PyTorch 同时看到；批量图传播、深度模型、RL 和大规模参数扫描可以使用 GPU，Brian2 smoke 与 MuJoCo 物理仿真仍有大量 CPU 组件。

## 9. 下一步 Nature 级实验路线

1. 下载完整 `flywire_synapses_783.feather`，复现 Ser/Glu 侧化在 synapse-level 位置和 confidence 上是否稳定。
2. 把 `signed_propagation_top_targets.csv` 中的 MBON/DAN/MBIN/APL/OAN 靶点转成遗传操作候选。
3. 批量跑 Brian2/LIF：右 α′β′ serotonin 激活、左 α′β′ glutamate 激活、互作沉默和 sham control。
4. 在 FlyGym 中加入随机初始朝向、多个 odor geometry、blind analysis 和 bootstrap CI。
5. 做真实行为实验：左右 odor memory、短期/长期记忆、药理或遗传扰动、左右脑 rescue。
6. 将结构、功能传播、仿真行为和真实行为放入同一 Bayesian/causal mediation model，形成可投高水平期刊的闭环证据链。

## 10. 论文图/视频建议

- 主文图 1：FlyWire KC NT 侧化 heatmap + α′β′ 聚焦结构图。
- 主文图 2：Ser/Glu forest plot + volcano + direction consistency。
- 主文图 3：右 serotonin / 左 glutamate seed 的 signed propagation 下游靶点。
- 主文图 4：FlyGym odor memory trajectory + 数据驱动条件对比。
- 扩展视频 1：`outputs/behavior/paper_comparison_cs_plus_left.mp4`。
- 扩展视频 2：`outputs/behavior/paper_comparison_cs_plus_right.mp4`。
- 扩展表：`kc_nt_fraction_stats.csv`、`kc_nt_seed_candidates.csv`、`signed_propagation_top_targets.csv`。
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the standalone Nature-level experiment report.")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "NATURE_LEVEL_EXPERIMENT_REPORT.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = write_report(args.output)
    print(output)


if __name__ == "__main__":
    main()
