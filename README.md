# bio_fly

果蝇全脑连接组功能仿真与蘑菇体左右不对称研究工程。目标是复现 Eon Systems “赛博果蝇/embodied brain emulation”中的脑网络层，基于 Shiu 等全脑 LIF 模型做功能扰动，再把你们 FlyWire 统计发现转成可验证的记忆回路假设。

## 当前状态

- 已复现：`/unify/ydchen/unidit/bio_fly/external/Drosophila_brain_model` + FlyWire v783/v630 连接矩阵。
- 已配置：`/unify/ydchen/unidit/bio_fly/env` 为 Python 3.10 venv，`pip install -e ".[dev]"` 已补齐 `pytest`。
- 已验证：`/unify/ydchen/unidit/bio_fly/env/bin/python -m pytest -q` 通过，`/unify/ydchen/unidit/bio_fly/scripts/run_repro_smoke.py` 跑通 Brian2 smoke。
- 已解析：用户论文 zip 可输出 memory/lateralization claims 与 figure inventory。
- 已形成：`/unify/ydchen/unidit/bio_fly/docs/POST_RUN_REPORT_CN.md` 记录最近一次四卡正式运行的耗时、结论、结果文件和改进项。
- 已新增：`/unify/ydchen/unidit/bio_fly/docs/LATERALIZATION_BEHAVIOR_SIMULATION_CN.md` 记录侧化增强、对称救援、镜像翻转和长视频行为仿真实验。
- 已探索：`/unify/ydchen/unidit/bio_fly/docs/STRUCTURE_BEHAVIOR_LINKAGE_CN.md` 把结构侧化、四卡功能传播和 FlyGym 轨迹读出统一到同一张证据链。
- 已筛选：`/unify/ydchen/unidit/bio_fly/docs/TARGET_PRIORITIZATION_CN.md` 从四卡 top targets 中提取 MBON/DAN/APL/DPM/MBIN/OAN 记忆轴遗传操控候选。
- 已扩展：`/unify/ydchen/unidit/bio_fly/docs/OLFACTORY_PERTURBATION_MEMORY_CN.md` 显式扰动 CS+/CS- 强度、气味扩散、初始位姿、单侧嗅觉通道和长期记忆参数，并生成两条长视频。
- 已实现：结构不对称候选可转成 signed propagation 功能验证和可选 Brian2/LIF 扰动清单。

## 快速开始

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
pip install -e ".[dev]"
python /unify/ydchen/unidit/bio_fly/scripts/estimate_resources.py
python /unify/ydchen/unidit/bio_fly/scripts/run_repro_smoke.py
python /unify/ydchen/unidit/bio_fly/scripts/extract_paper_findings.py
python /unify/ydchen/unidit/bio_fly/scripts/run_functional_validation.py --top-n 2 --steps 2 --max-active 1000
python /unify/ydchen/unidit/bio_fly/scripts/download_flywire_data.py --prepare-annotations --download-small
python /unify/ydchen/unidit/bio_fly/scripts/analyze_kc_nt_lateralization.py
python /unify/ydchen/unidit/bio_fly/scripts/build_model_linkage.py --steps 3 --max-active 5000 --propagation-backend torch --device cuda:0
python /unify/ydchen/unidit/bio_fly/scripts/benchmark_gpu_propagation.py --device cuda:0 --steps 3 --max-active 5000 --max-specs 6
python /unify/ydchen/unidit/bio_fly/scripts/run_four_card_experiment_suite.py --devices cuda:0 cuda:1 cuda:2 cuda:3 --steps 3 --max-active 5000 --n-random-per-family 128 --output-dir /unify/ydchen/unidit/bio_fly/outputs/four_card_suite
python /unify/ydchen/unidit/bio_fly/scripts/run_behavior_memory_experiment.py --conditions control right_mb_serotonin_enriched --n-trials 1 --run-time 0.2
python /unify/ydchen/unidit/bio_fly/scripts/run_behavior_memory_experiment.py --condition-table /unify/ydchen/unidit/bio_fly/outputs/model_linkage/derived_behavior_conditions.csv --n-trials 1 --run-time 0.5 --output-dir /unify/ydchen/unidit/bio_fly/outputs/behavior_data_driven
python /unify/ydchen/unidit/bio_fly/scripts/run_lateralization_behavior_suite.py --stats /unify/ydchen/unidit/bio_fly/outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv --output-dir /unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite --render-devices 0 1 2 3 --dose-trials 2 --dose-run-time 0.8 --render-run-time 1.6 --camera-play-speed 0.12
python /unify/ydchen/unidit/bio_fly/scripts/analyze_structure_behavior_linkage.py
python /unify/ydchen/unidit/bio_fly/scripts/prioritize_memory_axis_targets.py
python /unify/ydchen/unidit/bio_fly/scripts/run_olfactory_perturbation_suite.py --output-dir /unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite --render-devices 0 1 2 3 --screen-trials 2 --screen-run-time 0.9 --render-run-time 2.0 --camera-play-speed 0.12
python /unify/ydchen/unidit/bio_fly/scripts/summarize_behavior_results.py
python /unify/ydchen/unidit/bio_fly/scripts/make_behavior_comparison_video.py --cs-plus-side left
python /unify/ydchen/unidit/bio_fly/scripts/write_full_project_guide.py
python /unify/ydchen/unidit/bio_fly/scripts/write_paper_upgrade_draft.py
python /unify/ydchen/unidit/bio_fly/scripts/write_nature_experiment_report.py
```

如果你已经有 FlyWire 注释导出表，可继续运行：

```bash
python /unify/ydchen/unidit/bio_fly/scripts/analyze_mushroom_body_asymmetry.py \
  --metadata /unify/ydchen/unidit/bio_fly/data/flywire_annotations.csv
```

## 主要模块

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/repro.py`：Shiu `Drosophila_brain_model` 最小封装。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/asymmetry.py`：左右成对 MB/KC/MBON 不对称统计。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/paper_zip.py`：论文 zip 文本 claims 与图清单提取。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/propagation.py`：全连接矩阵 signed multi-hop propagation。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/functional.py`：候选 pair → 扰动 manifest → propagation/LIF 验证。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/data_fetch.py`：FlyWire 注释与 Zenodo 数据下载/整理。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/nt_analysis.py`：KC 输入 NT 左右不对称分析。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/behavior.py`：FlyGym/MuJoCo 左右记忆偏置行为实验和视频渲染。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/lateralization_behavior.py`：侧化操控、剂量扫描、四卡 EGL 长视频和中文报告生成。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/olfactory_perturbation.py`：嗅觉输入强度、气味几何、初始状态、长期记忆和单侧嗅觉通道扰动实验。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/structure_behavior_linkage.py`：结构侧化、功能传播、行为轨迹的联动分析和候选假说筛选。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/target_prioritization.py`：从四卡 top targets 中筛选可转遗传/药理操控的记忆轴候选。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/model_linkage.py`：真实 KC-NT 侧化候选 → 功能传播扰动 → 数据驱动行为参数。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/experiment_suite.py`：四卡系统仿真、matched random controls、统计显著性、图表和动态机制视频。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/behavior_summary.py`：行为结果汇总表和论文草图。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/video.py`：多条件行为视频拼接和论文补充视频输出。
- `/unify/ydchen/unidit/bio_fly/NATURE_LEVEL_EXPERIMENT_REPORT.md`：单独的操作文档、输出解释和实验报告。
- `/unify/ydchen/unidit/bio_fly/docs/FULL_PROJECT_GUIDE.md`：目录结构、模块、依赖、四卡配置和一键复现指南。
- `/unify/ydchen/unidit/bio_fly/docs/NATURE_PAPER_UPGRADE_DRAFT.md`：Nature 风格论文升级稿、结果叙事和 figure legends。
- `/unify/ydchen/unidit/bio_fly/docs/research_plan.md`：Nature 级证据链与实验路线。
- `/unify/ydchen/unidit/bio_fly/docs/resource_estimate.md`：当前资源、存储和扩展估算。
- `/unify/ydchen/unidit/bio_fly/docs/reproduction_notes.md`：复现命令与输出说明。
- `/unify/ydchen/unidit/bio_fly/docs/behavior_experiment.md`：FlyGym 行为学实验、视频渲染和论文级扩展路线。
- `/unify/ydchen/unidit/bio_fly/docs/LATERALIZATION_BEHAVIOR_SIMULATION_CN.md`：侧化行为操控、剂量扫描、长视频和 paper 增强说明。
- `/unify/ydchen/unidit/bio_fly/docs/STRUCTURE_BEHAVIOR_LINKAGE_CN.md`：结构-功能-行为联动探索报告。
- `/unify/ydchen/unidit/bio_fly/docs/TARGET_PRIORITIZATION_CN.md`：记忆轴遗传操控候选靶点报告。
- `/unify/ydchen/unidit/bio_fly/docs/OLFACTORY_PERTURBATION_MEMORY_CN.md`：嗅觉输入扰动与长期记忆仿真实验报告。

## 最新探索发现

- `ser` 输入在全部主要 KC subtype 中右侧偏置，`glut` 输入在多数主要 KC subtype 中左侧偏置；结构效应集中在 α′β′ 和 KCab-s。
- 四卡 propagation 显示 `right_serotonin_kc_activate` 和 `left_glutamate_kc_activate` 均进入 memory-axis readout，关键指标 FDR q 约 `0.038`。
- FlyGym 行为读出中，二分类 CS+ choice rate 容易饱和；`mean_approach_margin`、`signed_final_y`、`path_length` 更适合连接结构组学和行为学。
- 当前最强结构-功能-行为候选是 `left_mb_glutamate_enriched`，对应 `left_glutamate_kc_activate`，在行为 approach margin 上最强，并保持 memory-axis propagation。
- 靶点优先级分析把 `DPM`、`APL`、`MBON03/09/12/13`、`PPL103` 等候选从全脑 top targets 中筛出；当前最高优先级是左侧 `DPM` 和左侧 `APL`，对应 `left_glutamate_kc_activate` 与 `left_mb_glutamate_enriched`。
- 嗅觉扰动实验显示 `weak_odor_high_memory` 在低浓度 CS+/CS- 条件下仍保持 `CS+ choice rate = 1.0`，提示长期记忆增益可能补偿弱气味输入。
- `cs_plus_weak_conflict` 将 CS+ 强度降到 `0.28`、CS- 保持 `1.0` 后出现一侧 CS- 选择，是“记忆能否覆盖即时强感觉输入”的关键冲突实验候选。
- `left_sensor_deprivation` 与 `right_sensor_deprivation` 把单侧嗅觉通道和蘑菇体侧化拆开，适合后续测试感觉输入侧化与记忆轴侧化是否可分离。
- `mirror_reversal`、`bilateral_memory_blunted` 和强侧化条件是下一轮真实行为学与 spike-level validation 的优先反事实对照。

## GitHub 发布边界

公开仓库只追踪源码、测试、文档、少量 PNG 图和代表性 MP4。`/unify/ydchen/unidit/bio_fly/data`、`/unify/ydchen/unidit/bio_fly/external`、`/unify/ydchen/unidit/bio_fly/env`、原始 FlyWire 数据、大型 parquet/feather/zip 和批量轨迹结果不进入 Git。需要完整复现时按文档重新下载或在本地准备数据。

## 关键限制

`/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip` 当前检测到 `root_id_hits = 0`，说明它是文稿/图包，不是可直接仿真的 root ID 数据包。要把论文发现转成真实功能仿真，需要额外提供 FlyWire/Codex 导出的 root ID 级 metadata 与 synapse-level NT input 表。

## GPU 状态

当前 `env` 已切到 `torch==2.11.0+cu129` / `torchvision==0.26.0+cu129`，匹配本机 `CUDA 12.9` driver/runtime；`torch.cuda.is_available()` 为 `True`，4 张 `NVIDIA H20Z` 均可用。真实 FlyWire signed propagation 可用 `--propagation-backend torch --device cuda:0` 走 PyTorch sparse GPU 后端，当前 6 个 KC-NT 扰动、3 hop、top5000 benchmark 约 `3.9 s`。
