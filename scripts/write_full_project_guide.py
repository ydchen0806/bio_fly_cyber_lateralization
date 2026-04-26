#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from bio_fly.paths import PROJECT_ROOT


def _run(command: list[str]) -> str:
    result = subprocess.run(command, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.stdout.strip() else result.stderr.strip()


def write_guide(output_path: Path) -> Path:
    tree = _run(["bash", "-lc", "find . -maxdepth 3 -type f | sort | sed 's#^./##' | head -260"])
    guide = f"""# bio_fly 完整使用指南与四卡复现手册

## 1. 项目定位

`bio_fly` 是一个面向果蝇 mushroom body 偏侧化、连接组结构发现、全脑功能传播、身体行为仿真的赛博果蝇研究工程。它以 FlyWire v783 连接组为结构底座，以 Shiu/Drosophila whole-brain LIF 模型复现为神经动力学底座，以 FlyGym/MuJoCo 为 embodied behavior 底座，围绕左右脑蘑菇体 α′β′ Kenyon cell 的 serotonin/glutamate 输入侧化建立可扰动、可统计、可渲染的计算实验体系。

## 2. 环境

```bash
cd {PROJECT_ROOT}
source env/bin/activate
python -m pip check
python - <<'PY'
import torch
print(torch.__version__, torch.version.cuda)
print(torch.cuda.is_available(), torch.cuda.device_count())
PY
```

当前环境重点版本：

- Python venv：`{PROJECT_ROOT / "env"}`
- PyTorch：`torch==2.11.0+cu129`
- CUDA：系统 `12.9`，PyTorch compiled CUDA `12.9`
- GPU：4 张 `NVIDIA H20Z` 可由 PyTorch 使用
- MuJoCo/FlyGym：使用 `MUJOCO_GL=egl` 离屏渲染

## 3. 一键复现完整流程

```bash
cd {PROJECT_ROOT}
source env/bin/activate

# 可选代理
export http_proxy=http://192.168.32.28:18000
export https_proxy=http://192.168.32.28:18000

# 基础验证
python -m pip check
python -m pytest -q
python scripts/run_repro_smoke.py

# FlyWire 数据与 KC NT 侧化
python scripts/download_flywire_data.py --prepare-annotations --download-small --download-connections
python scripts/analyze_kc_nt_lateralization.py

# 四卡系统仿真、统计、图、视频、报告
python scripts/run_four_card_experiment_suite.py \\
  --devices cuda:0 cuda:1 cuda:2 cuda:3 \\
  --steps 3 \\
  --max-active 5000 \\
  --n-random-per-family 32 \\
  --output-dir outputs/four_card_suite

# 数据驱动 FlyGym 行为视频
MUJOCO_GL=egl python scripts/run_behavior_memory_experiment.py \\
  --condition-table outputs/model_linkage_gpu/derived_behavior_conditions.csv \\
  --n-trials 1 \\
  --run-time 0.5 \\
  --output-dir outputs/behavior_data_driven
python scripts/summarize_behavior_results.py --summary outputs/behavior_data_driven/memory_choice_summary.csv
python scripts/make_behavior_comparison_video.py \\
  --summary outputs/behavior_data_driven/memory_choice_summary.csv \\
  --cs-plus-side left \\
  --output outputs/behavior_data_driven/paper_comparison_cs_plus_left.mp4
```

## 4. 四卡并行参数

- `--devices cuda:0 cuda:1 cuda:2 cuda:3`：四张 GPU 各加载一份 sparse connectome graph，并行处理 manifest 分片。
- `--steps 3`：传播 hop 数；2 用于快速筛选，3 用于论文级初稿，4+ 可做敏感性分析。
- `--max-active 5000`：每步保留绝对响应最大的 active nodes；增大可提高覆盖率但增加输出与时间。
- `--n-random-per-family 32`：每个 null family 的随机对照数；论文级建议 128–1000。
- `--top-fraction 0.2`：每个显著 subtype 取 NT fraction 最高的前 20% seed。
- `--max-per-subtype 30`：限制单 subtype seed 数，避免大 subtype 主导。

## 5. 目录与模块结构

```text
{tree}
```

## 6. 核心模块说明

- `src/bio_fly/nt_analysis.py`：FlyWire proofread connections 中 KC 输入 NT fraction 计算、统计检验、FDR、图表。
- `src/bio_fly/model_linkage.py`：把结构侧化发现转成 KC seed ensemble、propagation manifest 和数据驱动行为参数。
- `src/bio_fly/propagation.py`：CPU pandas 与 PyTorch sparse GPU 两套 signed multi-hop propagation。
- `src/bio_fly/functional.py`：扰动 spec、propagation/LIF 验证入口。
- `src/bio_fly/experiment_suite.py`：四卡系统仿真、随机/消融对照、统计、图表和动态视频。
- `src/bio_fly/behavior.py`：FlyGym/MuJoCo odor-memory proxy experiment。
- `src/bio_fly/video.py`：论文补充视频 2×2 panel 拼接。

## 7. 输出解释

- `outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv`：结构发现主表；用于 Ser/Glu/GABA/DA 左右侧化统计。
- `outputs/model_linkage_gpu/*`：GPU 版真实 KC-NT seed 到功能传播的快速核心结果。
- `outputs/four_card_suite/suite_perturbation_manifest.csv`：真实扰动 + subtype 扰动 + null controls 的完整 manifest。
- `outputs/four_card_suite/suite_response_metrics.csv`：每个扰动的 memory-axis、MBON、DAN、APL/DPM、response laterality 等指标。
- `outputs/four_card_suite/suite_empirical_significance.csv`：真实扰动相对 matched random controls 的 empirical p、effect z、FDR q。
- `outputs/four_card_suite/figures/*.png|*.pdf`：文章主图/扩展图候选。
- `outputs/four_card_suite/videos/cyber_fly_lateralized_memory_axis.mp4`：结构到功能机制动态演示视频。
- `outputs/behavior_data_driven/*.mp4`：FlyGym embodied behavior 补充视频候选。

## 8. 二次开发建议

1. 把 `n-random-per-family` 提高到 128–1000，获得更稳定的 empirical p。
2. 下载 `flywire_synapses_783.feather`，加入 synapse-level spatial/NT uncertainty validation。
3. 将 `suite_top_targets.csv` 中的 MBON/DAN/MBIN/APL/DPM 靶点导出为遗传实验候选。
4. 用 Brian2/LIF 替代快速 propagation，对核心候选做 spike-level causal simulation。
5. 扩展 FlyGym：随机初始朝向、多个 odor geometry、长时记忆/短时记忆、多 seed 行为统计。
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(guide)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write the full bio_fly project guide.")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "docs" / "FULL_PROJECT_GUIDE.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(write_guide(args.output))


if __name__ == "__main__":
    main()
