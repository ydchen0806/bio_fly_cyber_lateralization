# bio_fly 完整使用指南与四卡复现手册

## 1. 项目定位

`bio_fly` 是一个面向果蝇 mushroom body 偏侧化、连接组结构发现、全脑功能传播、身体行为仿真的赛博果蝇研究工程。它以 FlyWire v783 连接组为结构底座，以 Shiu/Drosophila whole-brain LIF 模型复现为神经动力学底座，以 FlyGym/MuJoCo 为 embodied behavior 底座，围绕左右脑蘑菇体 α′β′ Kenyon cell 的 serotonin/glutamate 输入侧化建立可扰动、可统计、可渲染的计算实验体系。

## 2. 环境

```bash
cd /unify/ydchen/unidit/bio_fly
source env/bin/activate
python -m pip check
python - <<'PY'
import torch
print(torch.__version__, torch.version.cuda)
print(torch.cuda.is_available(), torch.cuda.device_count())
PY
```

当前环境重点版本：

- Python venv：`/unify/ydchen/unidit/bio_fly/env`
- PyTorch：`torch==2.11.0+cu129`
- CUDA：系统 `12.9`，PyTorch compiled CUDA `12.9`
- GPU：4 张 `NVIDIA H20Z` 可由 PyTorch 使用
- MuJoCo/FlyGym：使用 `MUJOCO_GL=egl` 离屏渲染

## 3. 一键复现完整流程

```bash
cd /unify/ydchen/unidit/bio_fly
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
python scripts/run_four_card_experiment_suite.py \
  --devices cuda:0 cuda:1 cuda:2 cuda:3 \
  --steps 3 \
  --max-active 5000 \
  --n-random-per-family 32 \
  --output-dir outputs/four_card_suite

# 数据驱动 FlyGym 行为视频
MUJOCO_GL=egl python scripts/run_behavior_memory_experiment.py \
  --condition-table outputs/model_linkage_gpu/derived_behavior_conditions.csv \
  --n-trials 1 \
  --run-time 0.5 \
  --output-dir outputs/behavior_data_driven
python scripts/summarize_behavior_results.py --summary outputs/behavior_data_driven/memory_choice_summary.csv
python scripts/make_behavior_comparison_video.py \
  --summary outputs/behavior_data_driven/memory_choice_summary.csv \
  --cs-plus-side left \
  --output outputs/behavior_data_driven/paper_comparison_cs_plus_left.mp4

# 从已有 FlyGym raw videos 生成培养皿/糖滴/气味杯场景版 food-memory paper videos
python scripts/make_food_memory_assay_scene_videos.py \
  --summary /unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/rendered_trials/memory_choice_summary.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/videos \
  --paper-video-dir /unify/ydchen/unidit/bio_fly/paper/video \
  --replace-paper-defaults

# OCT/MCH 镜像摆放早期动力学正式套件
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50 \
  --n-trials 50 \
  --run-time 0.2 \
  --max-workers 4 \
  --mirror-sides
```

## 4. 四卡并行参数

- `--devices cuda:0 cuda:1 cuda:2 cuda:3`：四张 GPU 各加载一份 sparse connectome graph，并行处理 manifest 分片。
- `--steps 3`：传播 hop 数；2 用于快速筛选，3 用于论文级初稿，4+ 可做敏感性分析。
- `--max-active 5000`：每步保留绝对响应最大的 active nodes；增大可提高覆盖率但增加输出与时间。
- `--n-random-per-family 32`：每个 null family 的随机对照数；论文级建议 128–1000。
- `--top-fraction 0.2`：每个显著 subtype 取 NT fraction 最高的前 20% seed。
- `--max-per-subtype 30`：限制单 subtype seed 数，避免大 subtype 主导。

FlyGym/MuJoCo 行为套件的并行参数不同于 PyTorch sparse propagation：

- `/unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py --max-workers 4`：启动 4 个 Python worker 并行跑 MuJoCo trial；无渲染时主要消耗 CPU，不会显著占满 H20Z/H200 GPU。
- `--mirror-sides`：每个条件同时运行 `CS+` 左侧和右侧，适合正式比较 MB 左右侧化扰动。
- `--early-fraction 0.25`：把每条轨迹前 25% 用作早期转向窗口，输出 `mean_early_expected_lateral_velocity`。
- `--commit-y-threshold 0.75`：到达预期横向区域的阈值，单位为 mm。
- `--render --render-devices 0 1 2 3`：仅在需要视频时启用，渲染使用 EGL 和 `MUJOCO_EGL_DEVICE_ID` 分配 GPU。正式统计不建议渲染全部 trial。

## 5. 目录与模块结构

```text
.cache/matplotlib/fontlist-v390.json
.pytest_cache/.gitignore
.pytest_cache/CACHEDIR.TAG
.pytest_cache/README.md
NATURE_LEVEL_EXPERIMENT_REPORT.md
README.md
Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip
data/processed/flywire_mushroom_body_annotations.parquet
data/processed/flywire_neuron_annotations.parquet
data/processed/kc_subtype_hemisphere_summary.csv
data/processed/mushroom_body_top_nt_by_side.csv
data/raw/flywire_zenodo_10676866_manifest.json
data/raw/zenodo_10676866_downloads.csv
docs/archive/behavior_experiment.md
docs/archive/reproduction_notes.md
docs/archive/research_plan.md
docs/archive/resource_estimate.md
env/bin/Activate.ps1
env/bin/activate
env/bin/activate.csh
env/bin/activate.fish
env/bin/cygdb
env/bin/cython
env/bin/cythonize
env/bin/debugpy
env/bin/debugpy-adapter
env/bin/dotenv
env/bin/f2py
env/bin/fabric
env/bin/flyvis
env/bin/fonttools
env/bin/futurize
env/bin/httpx
env/bin/imageio_download_bin
env/bin/imageio_remove_bin
env/bin/ipython
env/bin/ipython3
env/bin/isympy
env/bin/jlpm
env/bin/jsonpointer
env/bin/jsonschema
env/bin/jupyter
env/bin/jupyter-console
env/bin/jupyter-dejavu
env/bin/jupyter-events
env/bin/jupyter-execute
env/bin/jupyter-kernel
env/bin/jupyter-kernelspec
env/bin/jupyter-lab
env/bin/jupyter-labextension
env/bin/jupyter-labhub
env/bin/jupyter-migrate
env/bin/jupyter-nbconvert
env/bin/jupyter-notebook
env/bin/jupyter-run
env/bin/jupyter-server
env/bin/jupyter-troubleshoot
env/bin/jupyter-trust
env/bin/normalizer
env/bin/numba
env/bin/numpy-config
env/bin/pasteurize
env/bin/pip
env/bin/pip3
env/bin/pip3.10
env/bin/proton
env/bin/proton-viewer
env/bin/py.test
env/bin/pyav
env/bin/pybabel
env/bin/pyftmerge
env/bin/pyftsubset
env/bin/pygmentize
env/bin/pygrun
env/bin/pyjson5
env/bin/pytest
env/bin/send2trash
env/bin/torchfrtrace
env/bin/torchrun
env/bin/tqdm
env/bin/ttx
env/bin/wsdump
env/pyvenv.cfg
external/Drosophila_brain_model/.gitignore
external/Drosophila_brain_model/2023_03_23_completeness_630_final.csv
external/Drosophila_brain_model/2023_03_23_connectivity_630_final.parquet
external/Drosophila_brain_model/Completeness_783.csv
external/Drosophila_brain_model/Connectivity_783.parquet
external/Drosophila_brain_model/LICENSE
external/Drosophila_brain_model/Readme.md
external/Drosophila_brain_model/environment.yml
external/Drosophila_brain_model/environment_full.yml
external/Drosophila_brain_model/example.ipynb
external/Drosophila_brain_model/figures.ipynb
external/Drosophila_brain_model/model.py
external/Drosophila_brain_model/sez_neurons.pickle
external/Drosophila_brain_model/utils.py
external/flywire_annotations/.gitignore
external/flywire_annotations/README.md
external/flywire_annotations/flywire_annotations.Rproj
outputs/asymmetry/mushroom_body_pairwise_asymmetry.csv
outputs/asymmetry/mushroom_body_pairwise_asymmetry_summary.json
outputs/behavior/behavior_summary_barplots.png
outputs/behavior/behavior_summary_metrics.csv
outputs/behavior/bilateral_memory_blunted_trial0_choice_left.mp4
outputs/behavior/bilateral_memory_blunted_trial0_choice_left_trajectory.csv
outputs/behavior/bilateral_memory_blunted_trial0_choice_left_trajectory.png
outputs/behavior/bilateral_memory_blunted_trial0_choice_right.mp4
outputs/behavior/bilateral_memory_blunted_trial0_choice_right_trajectory.csv
outputs/behavior/bilateral_memory_blunted_trial0_choice_right_trajectory.png
outputs/behavior/control_trial0_choice_left.mp4
outputs/behavior/control_trial0_choice_left_trajectory.csv
outputs/behavior/control_trial0_choice_left_trajectory.png
outputs/behavior/control_trial0_choice_right.mp4
outputs/behavior/control_trial0_choice_right_trajectory.csv
outputs/behavior/control_trial0_choice_right_trajectory.png
outputs/behavior/flygym_egl_smoke.mp4
outputs/behavior/left_mb_glutamate_enriched_trial0_choice_left.mp4
outputs/behavior/left_mb_glutamate_enriched_trial0_choice_left_trajectory.csv
outputs/behavior/left_mb_glutamate_enriched_trial0_choice_left_trajectory.png
outputs/behavior/left_mb_glutamate_enriched_trial0_choice_right.mp4
outputs/behavior/left_mb_glutamate_enriched_trial0_choice_right_trajectory.csv
outputs/behavior/left_mb_glutamate_enriched_trial0_choice_right_trajectory.png
outputs/behavior/memory_choice_summary.csv
outputs/behavior/paper_comparison_cs_plus_left.mp4
outputs/behavior/paper_comparison_cs_plus_right.mp4
outputs/behavior/right_mb_serotonin_enriched_trial0_choice_left.mp4
outputs/behavior/right_mb_serotonin_enriched_trial0_choice_left_trajectory.csv
outputs/behavior/right_mb_serotonin_enriched_trial0_choice_left_trajectory.png
outputs/behavior/right_mb_serotonin_enriched_trial0_choice_right.mp4
outputs/behavior/right_mb_serotonin_enriched_trial0_choice_right_trajectory.csv
outputs/behavior/right_mb_serotonin_enriched_trial0_choice_right_trajectory.png
outputs/behavior_data_driven/behavior_summary_barplots.png
outputs/behavior_data_driven/behavior_summary_metrics.csv
outputs/behavior_data_driven/bilateral_memory_blunted_trial0_choice_left.mp4
outputs/behavior_data_driven/bilateral_memory_blunted_trial0_choice_left_trajectory.csv
outputs/behavior_data_driven/bilateral_memory_blunted_trial0_choice_left_trajectory.png
outputs/behavior_data_driven/bilateral_memory_blunted_trial0_choice_right.mp4
outputs/behavior_data_driven/bilateral_memory_blunted_trial0_choice_right_trajectory.csv
outputs/behavior_data_driven/bilateral_memory_blunted_trial0_choice_right_trajectory.png
outputs/behavior_data_driven/control_trial0_choice_left.mp4
outputs/behavior_data_driven/control_trial0_choice_left_trajectory.csv
outputs/behavior_data_driven/control_trial0_choice_left_trajectory.png
outputs/behavior_data_driven/control_trial0_choice_right.mp4
outputs/behavior_data_driven/control_trial0_choice_right_trajectory.csv
outputs/behavior_data_driven/control_trial0_choice_right_trajectory.png
outputs/behavior_data_driven/left_mb_glutamate_enriched_trial0_choice_left.mp4
outputs/behavior_data_driven/left_mb_glutamate_enriched_trial0_choice_left_trajectory.csv
outputs/behavior_data_driven/left_mb_glutamate_enriched_trial0_choice_left_trajectory.png
outputs/behavior_data_driven/left_mb_glutamate_enriched_trial0_choice_right.mp4
outputs/behavior_data_driven/left_mb_glutamate_enriched_trial0_choice_right_trajectory.csv
outputs/behavior_data_driven/left_mb_glutamate_enriched_trial0_choice_right_trajectory.png
outputs/behavior_data_driven/memory_choice_summary.csv
outputs/behavior_data_driven/paper_comparison_cs_plus_left.mp4
outputs/behavior_data_driven/paper_comparison_cs_plus_right.mp4
outputs/behavior_data_driven/right_mb_serotonin_enriched_trial0_choice_left.mp4
outputs/behavior_data_driven/right_mb_serotonin_enriched_trial0_choice_left_trajectory.csv
outputs/behavior_data_driven/right_mb_serotonin_enriched_trial0_choice_left_trajectory.png
outputs/behavior_data_driven/right_mb_serotonin_enriched_trial0_choice_right.mp4
outputs/behavior_data_driven/right_mb_serotonin_enriched_trial0_choice_right_trajectory.csv
outputs/behavior_data_driven/right_mb_serotonin_enriched_trial0_choice_right_trajectory.png
outputs/behavior_oriented/bilateral_memory_blunted_trial0_choice_left.mp4
outputs/behavior_oriented/bilateral_memory_blunted_trial0_choice_left_trajectory.csv
outputs/behavior_oriented/bilateral_memory_blunted_trial0_choice_left_trajectory.png
outputs/behavior_oriented/bilateral_memory_blunted_trial0_choice_right.mp4
outputs/behavior_oriented/bilateral_memory_blunted_trial0_choice_right_trajectory.csv
outputs/behavior_oriented/bilateral_memory_blunted_trial0_choice_right_trajectory.png
outputs/behavior_oriented/control_trial0_choice_left.mp4
outputs/behavior_oriented/control_trial0_choice_left_trajectory.csv
outputs/behavior_oriented/control_trial0_choice_left_trajectory.png
outputs/behavior_oriented/control_trial0_choice_right.mp4
outputs/behavior_oriented/control_trial0_choice_right_trajectory.csv
outputs/behavior_oriented/control_trial0_choice_right_trajectory.png
outputs/behavior_oriented/left_mb_glutamate_enriched_trial0_choice_left.mp4
outputs/behavior_oriented/left_mb_glutamate_enriched_trial0_choice_left_trajectory.csv
outputs/behavior_oriented/left_mb_glutamate_enriched_trial0_choice_left_trajectory.png
outputs/behavior_oriented/left_mb_glutamate_enriched_trial0_choice_right.mp4
outputs/behavior_oriented/left_mb_glutamate_enriched_trial0_choice_right_trajectory.csv
outputs/behavior_oriented/left_mb_glutamate_enriched_trial0_choice_right_trajectory.png
outputs/behavior_oriented/memory_choice_summary.csv
outputs/behavior_oriented/right_mb_serotonin_enriched_trial0_choice_left.mp4
outputs/behavior_oriented/right_mb_serotonin_enriched_trial0_choice_left_trajectory.csv
outputs/behavior_oriented/right_mb_serotonin_enriched_trial0_choice_left_trajectory.png
outputs/behavior_oriented/right_mb_serotonin_enriched_trial0_choice_right.mp4
outputs/behavior_oriented/right_mb_serotonin_enriched_trial0_choice_right_trajectory.csv
outputs/behavior_oriented/right_mb_serotonin_enriched_trial0_choice_right_trajectory.png
outputs/behavior_screen/bilateral_memory_blunted_trial0_choice_left_trajectory.csv
outputs/behavior_screen/bilateral_memory_blunted_trial0_choice_left_trajectory.png
outputs/behavior_screen/bilateral_memory_blunted_trial0_choice_right_trajectory.csv
outputs/behavior_screen/bilateral_memory_blunted_trial0_choice_right_trajectory.png
outputs/behavior_screen/bilateral_memory_blunted_trial1_choice_left_trajectory.csv
outputs/behavior_screen/bilateral_memory_blunted_trial1_choice_left_trajectory.png
outputs/behavior_screen/bilateral_memory_blunted_trial1_choice_right_trajectory.csv
outputs/behavior_screen/bilateral_memory_blunted_trial1_choice_right_trajectory.png
outputs/behavior_screen/bilateral_memory_blunted_trial2_choice_left_trajectory.csv
outputs/behavior_screen/bilateral_memory_blunted_trial2_choice_left_trajectory.png
outputs/behavior_screen/bilateral_memory_blunted_trial2_choice_right_trajectory.csv
outputs/behavior_screen/bilateral_memory_blunted_trial2_choice_right_trajectory.png
outputs/behavior_screen/control_trial0_choice_left_trajectory.csv
outputs/behavior_screen/control_trial0_choice_left_trajectory.png
outputs/behavior_screen/control_trial0_choice_right_trajectory.csv
outputs/behavior_screen/control_trial0_choice_right_trajectory.png
outputs/behavior_screen/control_trial1_choice_left_trajectory.csv
outputs/behavior_screen/control_trial1_choice_left_trajectory.png
outputs/behavior_screen/control_trial1_choice_right_trajectory.csv
outputs/behavior_screen/control_trial1_choice_right_trajectory.png
outputs/behavior_screen/control_trial2_choice_left_trajectory.csv
outputs/behavior_screen/control_trial2_choice_left_trajectory.png
outputs/behavior_screen/control_trial2_choice_right_trajectory.csv
outputs/behavior_screen/control_trial2_choice_right_trajectory.png
outputs/behavior_screen/left_mb_glutamate_enriched_trial0_choice_left_trajectory.csv
outputs/behavior_screen/left_mb_glutamate_enriched_trial0_choice_left_trajectory.png
outputs/behavior_screen/left_mb_glutamate_enriched_trial0_choice_right_trajectory.csv
outputs/behavior_screen/left_mb_glutamate_enriched_trial0_choice_right_trajectory.png
outputs/behavior_screen/left_mb_glutamate_enriched_trial1_choice_left_trajectory.csv
outputs/behavior_screen/left_mb_glutamate_enriched_trial1_choice_left_trajectory.png
outputs/behavior_screen/left_mb_glutamate_enriched_trial1_choice_right_trajectory.csv
outputs/behavior_screen/left_mb_glutamate_enriched_trial1_choice_right_trajectory.png
outputs/behavior_screen/left_mb_glutamate_enriched_trial2_choice_left_trajectory.csv
outputs/behavior_screen/left_mb_glutamate_enriched_trial2_choice_left_trajectory.png
outputs/behavior_screen/left_mb_glutamate_enriched_trial2_choice_right_trajectory.csv
outputs/behavior_screen/left_mb_glutamate_enriched_trial2_choice_right_trajectory.png
outputs/behavior_screen/memory_choice_summary.csv
outputs/behavior_screen/right_mb_serotonin_enriched_trial0_choice_left_trajectory.csv
outputs/behavior_screen/right_mb_serotonin_enriched_trial0_choice_left_trajectory.png
outputs/behavior_screen/right_mb_serotonin_enriched_trial0_choice_right_trajectory.csv
outputs/behavior_screen/right_mb_serotonin_enriched_trial0_choice_right_trajectory.png
outputs/behavior_screen/right_mb_serotonin_enriched_trial1_choice_left_trajectory.csv
outputs/behavior_screen/right_mb_serotonin_enriched_trial1_choice_left_trajectory.png
outputs/behavior_screen/right_mb_serotonin_enriched_trial1_choice_right_trajectory.csv
outputs/behavior_screen/right_mb_serotonin_enriched_trial1_choice_right_trajectory.png
outputs/behavior_screen/right_mb_serotonin_enriched_trial2_choice_left_trajectory.csv
outputs/behavior_screen/right_mb_serotonin_enriched_trial2_choice_left_trajectory.png
outputs/behavior_screen/right_mb_serotonin_enriched_trial2_choice_right_trajectory.csv
outputs/behavior_screen/right_mb_serotonin_enriched_trial2_choice_right_trajectory.png
outputs/demo_metadata.csv
outputs/four_card_suite/CYBER_FLY_NATURE_UPGRADE_REPORT.md
outputs/four_card_suite/gpu_worker_assignment.csv
outputs/four_card_suite/gpu_worker_results.csv
outputs/four_card_suite/suite_empirical_significance.csv
outputs/four_card_suite/suite_perturbation_manifest.csv
outputs/four_card_suite/suite_response_by_step_side_class.csv
outputs/four_card_suite/suite_response_metrics.csv
outputs/four_card_suite/suite_run_info.json
outputs/four_card_suite/suite_seed_candidates.csv
outputs/four_card_suite/suite_signed_propagation_responses.parquet
outputs/four_card_suite/suite_signed_propagation_summary.csv
outputs/four_card_suite/suite_top_targets.csv
outputs/four_card_suite_smoke/CYBER_FLY_NATURE_UPGRADE_REPORT.md
outputs/four_card_suite_smoke/gpu_worker_assignment.csv
outputs/four_card_suite_smoke/gpu_worker_results.csv
outputs/four_card_suite_smoke/suite_empirical_significance.csv
outputs/four_card_suite_smoke/suite_perturbation_manifest.csv
outputs/four_card_suite_smoke/suite_response_by_step_side_class.csv
outputs/four_card_suite_smoke/suite_response_metrics.csv
outputs/four_card_suite_smoke/suite_run_info.json
outputs/four_card_suite_smoke/suite_seed_candidates.csv
outputs/four_card_suite_smoke/suite_signed_propagation_responses.parquet
outputs/four_card_suite_smoke/suite_signed_propagation_summary.csv
outputs/four_card_suite_smoke/suite_top_targets.csv
```

## 6. 核心模块说明

- `src/bio_fly/nt_analysis.py`：FlyWire proofread connections 中 KC 输入 NT fraction 计算、统计检验、FDR、图表。
- `src/bio_fly/model_linkage.py`：把结构侧化发现转成 KC seed ensemble、propagation manifest 和数据驱动行为参数。
- `src/bio_fly/propagation.py`：CPU pandas 与 PyTorch sparse GPU 两套 signed multi-hop propagation。
- `src/bio_fly/functional.py`：扰动 spec、propagation/LIF 验证入口。
- `src/bio_fly/experiment_suite.py`：四卡系统仿真、随机/消融对照、统计、图表和动态视频。
- `src/bio_fly/behavior.py`：FlyGym/MuJoCo odor-memory proxy experiment。
- `src/bio_fly/video.py`：论文补充视频 2×2 panel 拼接。
- `scripts/make_food_memory_assay_scene_videos.py`：从已有 FlyGym food-memory rendered trials 生成 assay-scene 论文视频，不需要重跑 MuJoCo。

## 7. 输出解释

- `outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv`：结构发现主表；用于 Ser/Glu/GABA/DA 左右侧化统计。
- `outputs/model_linkage_gpu/*`：GPU 版真实 KC-NT seed 到功能传播的快速核心结果。
- `outputs/four_card_suite/suite_perturbation_manifest.csv`：真实扰动 + subtype 扰动 + null controls 的完整 manifest。
- `outputs/four_card_suite/suite_response_metrics.csv`：每个扰动的 memory-axis、MBON、DAN、APL/DPM、response laterality 等指标。
- `outputs/four_card_suite/suite_empirical_significance.csv`：真实扰动相对 matched random controls 的 empirical p、effect z、FDR q。
- `outputs/four_card_suite/figures/*.png|*.pdf`：文章主图/扩展图候选。
- `outputs/four_card_suite/videos/cyber_fly_lateralized_memory_axis.mp4`：结构到功能机制动态演示视频。
- `outputs/behavior_data_driven/*.mp4`：FlyGym embodied behavior 补充视频候选。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_left.mp4` 和 `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_right.mp4`：培养皿/糖滴/气味杯场景版 food-memory 补充视频。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/*`：OCT/MCH mirror-side `n=50` 早期动力学正式套件；总计 800 条短时程 trial，包含 side-balanced valence memory 和 MB 扰动 WT 比较。
- `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_MIRROR_KINEMATICS_CN.md`：上述套件的中文解释、变量定义、结果和边界。

## 8. 二次开发建议

1. 把 `n-random-per-family` 提高到 128–1000，获得更稳定的 empirical p。
2. 下载 `flywire_synapses_783.feather`，加入 synapse-level spatial/NT uncertainty validation。
3. 将 `suite_top_targets.csv` 中的 MBON/DAN/MBIN/APL/DPM 靶点导出为遗传实验候选。
4. 用 Brian2/LIF 替代快速 propagation，对核心候选做 spike-level causal simulation。
5. 扩展 FlyGym：随机初始朝向、多个 odor geometry、长时记忆/短时记忆、多 seed 行为统计。
