# 给非生物/AI 背景老师的赛博果蝇项目汇报

保存路径：`/unify/ydchen/unidit/bio_fly/docs/TEACHER_BRIEFING_CN.md`

最后更新：`2026-04-27`

## 1. 这个项目在研究什么

本项目目录是 `/unify/ydchen/unidit/bio_fly`。核心问题是：

**果蝇左右脑蘑菇体的连接结构不对称，是否会造成嗅觉记忆和行为选择的不对称？**

把这句话拆开：

- `果蝇`：一个神经系统很小但行为丰富的模式动物。
- `连接组`：神经元之间的接线图。节点是神经元，边是突触连接。
- `蘑菇体`：果蝇学习和记忆的核心脑区，尤其与气味记忆有关。
- `左右脑不对称`：左半脑和右半脑并不是完全镜像，某些神经递质输入、连接强度或下游输出可能不同。
- `嗅觉记忆`：果蝇闻到一种气味后，如果这种气味曾经和糖奖励或惩罚配对，果蝇会改变接近或回避行为。
- `赛博果蝇`：把真实果蝇连接组、仿真神经传播和 FlyGym/NeuroMechFly 身体模型组合起来，形成可以跑实验、出统计、渲染视频的计算系统。

## 2. Eon/CyberFly 原文结论应该怎样理解

Eon 的公开说明是 `https://eon.systems/updates/embodied-brain-emulation`。它的思想是把 FlyWire 全脑连接组、感觉输入、下降神经元读出、身体仿真和控制器组合起来，测试果蝇行为。

需要严谨区分两件事：

- 可以严谨复现的部分：用公开 FlyWire 数据做连接组传播；把嗅觉、视觉、味觉、机械感觉输入映射到下游 readout；用 FlyGym/NeuroMechFly 渲染可解释行为代理。
- 不能直接从公开资料复现的部分：Eon 内部完整 DN 列表、所有传感器到神经元的精确输入映射、DN-to-motor 参数、训练好的闭环控制权重、完整行为 benchmark 权重。

所以本项目不能把结果写成“只给连接组就自动涌现完整果蝇行为”。更准确的表述是：

**公开可复现的赛博果蝇系统目前是分层闭环：真实连接组负责功能传播，下降神经元/目标神经元负责行为 readout，FlyGym/NeuroMechFly 和低维控制器负责身体运动。**

这不是削弱项目价值，反而是发表时必须写清楚的方法学边界。否则容易被审稿人质疑“把控制器行为说成连接组涌现”。

## 3. 当前已经下载和准备了哪些数据

本地数据目录是 `/unify/ydchen/unidit/bio_fly/data`，外部仓库目录是 `/unify/ydchen/unidit/bio_fly/external`。

已经存在的关键文件：

- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/proofread_root_ids_783.npy`：FlyWire v783 proofread 神经元 root id 列表，大小约 `1.1 MB`。
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/proofread_connections_783.feather`：proofread 连接表，大小约 `852 MB`。
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/flywire_synapses_783.feather`：突触表，大小约 `9.5 GB`。
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/per_neuron_neuropil_count_pre_783.feather`：每个神经元各脑区 presynaptic 计数，大小约 `16.9 MB`。
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/per_neuron_neuropil_count_post_783.feather`：每个神经元各脑区 postsynaptic 计数，大小约 `234 MB`。
- `/unify/ydchen/unidit/bio_fly/data/processed/flywire_neuron_annotations.parquet`：整理后的 FlyWire 神经元注释，大小约 `8.8 MB`。
- `/unify/ydchen/unidit/bio_fly/data/processed/flywire_mushroom_body_annotations.parquet`：蘑菇体相关神经元注释，大小约 `0.4 MB`。
- `/unify/ydchen/unidit/bio_fly/external/flywire_annotations`：FlyWire 注释仓库。
- `/unify/ydchen/unidit/bio_fly/external/Drosophila_brain_model`：Shiu 等 Drosophila brain model 公开实现。

这些数据已经足够继续做：

- 左右蘑菇体结构不对称统计。
- KC、MBON、DAN、APL、DPM 等记忆轴神经元的 readout。
- 多 hop signed propagation。
- 随机扰动对照和经验显著性估计。
- 连接组结构发现到行为代理视频的可解释验证链。

它们还不足以做：

- Eon 内部闭环权重的逐参数复刻。
- 完整 DN-to-motor 行为控制器复刻。
- 无代理层的 spike-level 全脑-全身端到端行为涌现。

## 4. 关键变量解释

`CS+` 是 conditioned stimulus positive，指训练时和奖励或正性意义配对的气味。本项目的视频中，`CS+ sugar/food odour` 表示糖奖励相关的食物气味。

`CS-` 是 conditioned stimulus negative，指未奖励、中性或竞争性气味。本项目的视频中，`CS- decoy odour` 表示诱饵气味。

`KC` 是 Kenyon cell，是蘑菇体主要内在神经元，负责稀疏编码气味。

`MBON` 是 mushroom body output neuron，是蘑菇体输出神经元，把学习/记忆状态传给下游决策网络。

`DAN` 是 dopaminergic neuron，多巴胺神经元，常用于奖励、惩罚和记忆更新信号。

`APL` 是 anterior paired lateral neuron，蘑菇体内广泛抑制神经元，影响稀疏编码和反馈抑制。

`DPM` 是 dorsal paired medial neuron，与记忆维持和蘑菇体调控相关。

`DN` 是 descending neuron，下降神经元，把脑内决策信号传到胸神经节和运动系统。

`readout` 是读出指标。这里不是说直接看到果蝇想法，而是把连接组传播后的响应聚合到某类神经元，例如 DN、MBON、DAN 或 mechanosensory target。

`absolute_mass` 是传播响应绝对值总量，反映某个感觉扰动在连接组里造成的总体影响强度。

`signed_mass` 是带正负号的响应总量，正负号来自兴奋/抑制或 signed propagation 的方向约定。

`food_choice_rate` 是食物气味选择率，等于选择 `CS+` 的 trial 比例。

`mean_food_approach_margin` 是接近 CS+ 相对 CS- 的优势，计算思路是 `distance_to_cs_minus - distance_to_cs_plus`；越大代表最终位置更接近 CS+。

`mean_signed_final_y` 是把左右 CS+ 位置统一到同一符号后得到的终点偏移，越大代表越偏向 CS+ 所在侧。

`proxy` 是代理模型。意思是某些行为视频不是完整生物力学行为复刻，而是用可解释控制器把连接组 readout 映射成视觉可懂的动作。

`OCT` 是 `3-octanol`，`MCH` 是 `4-methylcyclohexanol`，二者是经典果蝇嗅觉条件化实验中常用的一对气味。

`mirror-side` 是镜像摆放。意思是同一个条件既跑 `CS+` 在左侧，也跑 `CS+` 在右侧，用来排除“只是气味放在左边/右边”造成的假侧化。

`mean_expected_laterality_index` 是按实验预期方向校正后的横向位移除以路径长度。奖励任务中，朝 `CS+` 走为正；电击任务中，远离 `CS+` 走为正。

`mean_early_expected_lateral_velocity` 是轨迹前 `25%` 时间里朝预期方向的横向速度，用来观察果蝇早期转向，而不是只看最终停在哪里。

`mean_physical_laterality_index` 不做 `CS+` 方向校正，直接看身体真实向左还是向右漂移。这个变量用来检查是否存在纯粹的运动侧偏。

## 5. 当前代码结构

核心包目录：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/propagation.py`：GPU/CPU signed multi-hop 连接组传播。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/eon_multimodal_benchmark.py`：Eon/CyberFly 风格嗅觉、视觉、味觉、机械感觉多模态 benchmark。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/food_memory.py`：食物气味 CS+/CS- 记忆套件。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/behavior.py`：FlyGym 嗅觉行为仿真和轨迹/视频保存。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/video.py`：论文视频拼接和 CS+/CS- 可视化标注。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/olfactory_perturbation.py`：嗅觉扰动、长期记忆、弱气味、单侧感觉剥夺实验。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/lateralization_behavior.py`：左右侧化剂量扫描和镜像/救援对照。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/structure_behavior_linkage.py`：结构-功能-行为相关分析。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/target_prioritization.py`：可实验验证靶点排序。

关键脚本目录：

- `/unify/ydchen/unidit/bio_fly/scripts/download_flywire_data.py`：下载 FlyWire 公开数据和注释。
- `/unify/ydchen/unidit/bio_fly/scripts/run_eon_multimodal_benchmark.py`：运行多模态复现。
- `/unify/ydchen/unidit/bio_fly/scripts/run_food_memory_suite.py`：运行食物气味记忆视频和统计。
- `/unify/ydchen/unidit/bio_fly/scripts/run_four_card_experiment_suite.py`：四卡连接组传播和随机对照。
- `/unify/ydchen/unidit/bio_fly/scripts/run_olfactory_perturbation_suite.py`：嗅觉扰动实验。
- `/unify/ydchen/unidit/bio_fly/scripts/run_lateralization_behavior_suite.py`：侧化行为实验。

论文和视频目录：

- `/unify/ydchen/unidit/bio_fly/paper/NATURE_STYLE_DRAFT_CN.md`：中文 Nature 风格论文草稿。
- `/unify/ydchen/unidit/bio_fly/paper/FIGURE_AND_VIDEO_INDEX_CN.md`：图和视频索引。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`：CS+ 在左侧的食物气味记忆视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`：CS+ 在右侧的食物气味记忆视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_left.mp4`：培养皿/糖滴/气味杯场景版，CS+ 在左侧。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_right.mp4`：培养皿/糖滴/气味杯场景版，CS+ 在右侧。
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_visual_object_tracking.mp4`：视觉目标跟踪视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_front_leg_grooming_proxy.mp4`：前足梳理代理视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_multimodal_reproduction_summary.mp4`：四宫格多模态总览视频。

## 6. 本轮新增/改进了什么

本轮主要做了三件事。

第一，重新运行 Eon/CyberFly 风格多模态复现：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
python /unify/ydchen/unidit/bio_fly/scripts/run_eon_multimodal_benchmark.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark \
  --render-device 0 \
  --propagation-device cuda:0
```

该命令本轮耗时约 `1 分 34 秒`。关键输出是：

- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_readout_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_top_targets.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_connectome_multimodal_readout_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_top_target_classes.png`
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_visual_object_tracking.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_front_leg_grooming_proxy.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_multimodal_reproduction_summary.mp4`

第二，重新运行食物气味记忆套件：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
python /unify/ydchen/unidit/bio_fly/scripts/run_food_memory_suite.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/food_memory_suite \
  --paper-video-dir /unify/ydchen/unidit/bio_fly/paper/video \
  --n-trials 1 \
  --run-time 0.9 \
  --render-device 1 \
  --camera-play-speed 0.14
```

该命令本轮耗时约 `5 分 15 秒`。关键输出是：

- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/conditions/food_memory_conditions.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/rendered_trials/memory_choice_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/food_memory_behavior_summary.csv`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`

第三，改进视频可读性：

- 修改文件：`/unify/ydchen/unidit/bio_fly/src/bio_fly/video.py`
- 新增脚本：`/unify/ydchen/unidit/bio_fly/scripts/make_food_memory_assay_scene_videos.py`
- 新增 assay-scene 场景层：培养皿/agar 背景、糖滴、气味杯、滤纸片、半透明气味羽流和比例尺。
- 新版默认 paper 视频已经替换为 `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4` 和 `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`。
- 在视频中明确标注这些物体是 post-render paper-readable scene overlay，避免误导为 FlyGym 原生食物物体。

第四，新增 OCT/MCH mirror-side 早期动力学正式套件：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50 \
  --n-trials 50 \
  --run-time 0.2 \
  --max-workers 4 \
  --mirror-sides
```

该套件总共跑了 `800` 条短时程轨迹，输出在 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50`，解释文档在 `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_MIRROR_KINEMATICS_CN.md`。

## 7. 当前关键结果

多模态连接组 readout 结果来自 `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_readout_summary.csv`。

主要数值：

| condition | n_seed_neurons | active_response_neurons | absolute_mass | descending_abs_mass | memory_axis_abs_mass | visual_projection_abs_mass | gustatory_abs_mass | mechanosensory_abs_mass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| olfactory_food_memory | 255 | 7376 | 2.664589 | 0.011488 | 0.245349 | 1.320785 | 0.000028 | 0.000000 |
| visual_object_tracking | 255 | 11152 | 1.577666 | 0.203957 | 0.075750 | 0.885637 | 0.005476 | 0.005376 |
| gustatory_feeding | 256 | 6895 | 1.645239 | 0.255412 | 0.004189 | 0.945583 | 0.225318 | 0.118458 |
| mechanosensory_grooming | 256 | 7802 | 1.878642 | 0.463450 | 0.001634 | 1.111238 | 0.027579 | 0.146880 |

解释：

- 嗅觉食物记忆输入能传播到记忆轴，`memory_axis_abs_mass = 0.245349`。
- 视觉输入对 visual projection readout 很强，`visual_projection_abs_mass = 0.885637`。
- 味觉输入对 gustatory readout 和 descending readout 较明显，支持 feeding proxy 的方向。
- 机械感觉输入对 descending 和 mechanosensory readout 明显，支持 grooming proxy 的方向。

食物气味行为结果来自 `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/food_memory_behavior_summary.csv`。

主要数值：

| condition | n_trials | food_choice_rate | mean_food_approach_margin | mean_signed_final_y |
|---|---:|---:|---:|---:|
| food_weak_sugar_strong_decoy | 2 | 1.0 | 5.527546 | 3.923511 |
| food_right_dan_mbon_output | 2 | 1.0 | 5.364938 | 4.075781 |
| food_naive_balanced_search | 2 | 1.0 | 5.338616 | 3.836297 |
| food_learned_sugar_memory | 2 | 1.0 | 5.247917 | 3.965852 |
| food_left_kc_apl_dpm_feedback | 2 | 1.0 | 5.135733 | 3.617102 |

严谨解释：

- 这轮食物记忆视频主要是展示性质：所有条件都选择了 CS+。
- 它证明当前环境能把明确的食物相关气味 `CS+` 和诱饵气味 `CS-` 可视化，并用 FlyGym 生成可解释轨迹。
- 它还不能单独证明左右蘑菇体侧化造成显著行为差异，因为每个条件只有左右各 1 次 trial，且 choice rate 已经天花板化。
- 更适合做统计结论的是 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite`、`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite` 和 `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite` 里的多条件对照结果。

OCT/MCH mirror-side 正式结果来自 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_condition_summary.csv`。

主要数值：

| condition | n_trials | expected_choice_rate | mean_approach_margin | expected_choice_fdr_q |
| --- | ---: | ---: | ---: | ---: |
| `oct_sucrose_appetitive_wt` | 100 | 0.86 | 0.265371 | 9.468e-14 |
| `mch_sucrose_appetitive_wt_counterbalanced` | 100 | 0.85 | 0.245904 | 4.825e-13 |
| `oct_shock_aversive_wt` | 100 | 0.86 | -0.244407 | 9.468e-14 |
| `weak_oct_strong_mch_conflict` | 100 | 0.88 | 0.264908 | 3.823e-15 |

给非生物老师的解释：

- 奖励任务中，果蝇代理应该靠近 `CS+`；电击任务中，果蝇代理应该远离 `CS+`。这个方向在 `800` 条短时程轨迹中显著成立。
- mirror-side 后，`CS+` 左右摆放被平衡，所以这个结果不是单纯由左/右空间偏置造成。
- 但是，左侧 MB 抑制、右侧 MB 抑制、左右 MB 平均化、左右 MB 互换相对 WT 的差异仍未通过 FDR。最强曲率趋势的 q 值为 `0.170533`，不足以作为显著发现。
- 因此当前可以说“代理系统能表达 OCT/MCH 记忆方向”，但不能说“代理系统已经证明 MB 侧化扰动导致行为差异”。

## 8. 用四卡 GPU 的方法

当前机器能看到 4 张 H20Z GPU。检查命令：

```bash
nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader
```

四卡连接组传播命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
python /unify/ydchen/unidit/bio_fly/scripts/run_four_card_experiment_suite.py \
  --devices cuda:0 cuda:1 cuda:2 cuda:3 \
  --steps 3 \
  --max-active 5000 \
  --n-random-per-family 128 \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/four_card_suite
```

多模态连接组传播目前用 `--propagation-device cuda:0`。如果要扩展到四卡，需要把不同 sensory spec 或不同 random/null specs 分配到 `cuda:0` 到 `cuda:3`。四卡套件已经在 `/unify/ydchen/unidit/bio_fly/src/bio_fly/experiment_suite.py` 中实现了这种并行思路。

渲染用的 GPU 由 `MUJOCO_EGL_DEVICE_ID` 或脚本参数 `--render-device` 控制。食物记忆这轮用了 `--render-device 1`，多模态复现用了 `--render-device 0`。

需要注意：无渲染的 FlyGym/MuJoCo rollout 主要消耗 CPU 和 Python worker 时间，不会像 PyTorch sparse propagation 那样占满 H20Z/H200 GPU。GPU 最适合用于四卡连接组传播和带 EGL 的视频渲染。

## 9. 如何一键复现

基础环境：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
export http_proxy=http://192.168.32.28:18000
export https_proxy=http://192.168.32.28:18000
```

准备数据：

```bash
python /unify/ydchen/unidit/bio_fly/scripts/download_flywire_data.py \
  --prepare-annotations \
  --download-small \
  --download-connections \
  --download-neuropil-post
```

如果需要完整 synapse 表：

```bash
python /unify/ydchen/unidit/bio_fly/scripts/download_flywire_data.py \
  --download-synapses
```

运行 Eon/CyberFly 风格多模态复现：

```bash
python /unify/ydchen/unidit/bio_fly/scripts/run_eon_multimodal_benchmark.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark \
  --render-device 0 \
  --propagation-device cuda:0
```

运行食物气味记忆视频：

```bash
python /unify/ydchen/unidit/bio_fly/scripts/run_food_memory_suite.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/food_memory_suite \
  --paper-video-dir /unify/ydchen/unidit/bio_fly/paper/video \
  --n-trials 1 \
  --run-time 0.9 \
  --render-device 1 \
  --camera-play-speed 0.14
```

运行 OCT/MCH mirror-side 论文视频：

```bash
python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview \
  --n-trials 1 \
  --run-time 0.8 \
  --max-workers 4 \
  --mirror-sides \
  --render \
  --keep-trajectories \
  --render-devices 0 1 2 3

python /unify/ydchen/unidit/bio_fly/scripts/make_oct_mch_assay_scene_videos.py \
  --summary /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/oct_mch_formal_trials.csv \
  --aggregate /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_condition_summary.csv \
  --comparisons /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_wt_comparisons.csv
```

视频结果入口：

- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_key_conditions.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_mb_perturbations.mp4`
- `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_ASSAY_VIDEO_RENDERING_CN.md`

运行回归测试：

```bash
python -m pytest -q
```

## 10. 可以写进论文的结论

可以写：

- 公开 FlyWire 连接组可以支持多模态 sensory-to-readout 功能传播。
- 嗅觉食物记忆输入能传播到蘑菇体记忆轴 readout。
- 视觉、味觉、机械感觉输入显示出不同 readout profile，说明系统不是只为一个嗅觉任务手工画图。
- 左右蘑菇体结构侧化可以被映射到可解释行为参数，并通过 CS+/CS- 气味选择任务生成反事实视频。
- 右侧 serotonin 相关 KC 输入和左侧 glutamate 相关 KC 输入在之前四卡套件中对 DAN/APL/DPM 和 response laterality 等指标显示了 FDR 校正后的显著差异。
- OCT/MCH mirror-side `n=50` 行为代理稳定表达奖励趋近、惩罚回避和弱 CS+ 冲突下的记忆方向。
- OCT/MCH mirror-side 视频已经把代表性轨迹、左右摆放、OCT/MCH 气味身份、糖奖励/电击和正式 `n=100` 统计 inset 放到同一个画面，适合给非生物背景评审解释“果蝇闻到了什么、预期做什么、统计证据在哪里”。

不能写：

- 连接组单独自动涌现了完整果蝇行为。
- 当前系统已经复刻 Eon 内部所有实验权重。
- 当前视频中的“食物”是真实可摄取糖滴力学对象。
- 当前 2 个 trial 的食物视频足以证明行为显著性。
- 当前 calibrated motor bridge 已经证明 MB 侧化扰动产生显著行为差异。
- OCT/MCH 单条视频 trial 本身已经证明显著性；显著性应引用 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50` 的正式统计表。

## 11. Nature 级别还差什么

如果目标是 Nature 正刊或 Nature 子刊，需要补齐以下证据。

第一，真实生物实验：

- 用真实果蝇做 `3-octanol` 和 `isoamyl acetate` 等气味的 CS+/CS- 条件化。
- 用糖奖励或电击惩罚建立记忆。
- 用 T-maze 或闭环虚拟现实记录选择率、轨迹、转向和速度。
- 做左右蘑菇体相关神经元的遗传操控或光遗传/热遗传扰动。

第二，神经活动验证：

- 对 KC、MBON、DAN、APL、DPM 做钙成像或电生理。
- 验证仿真预测的左/右侧响应差异是否存在。
- 验证右侧 serotonin 和左侧 glutamate 相关通路是否真的调节记忆检索或行为读出。

第三，计算模型升级：

- 获取或重建 Eon 级 DN-to-motor mapping。
- 把视觉、feeding、grooming 从 proxy 升级为可量化行为 benchmark。
- 对每个行为引入真实实验基线，而不是只做演示视频。
- 增加跨个体或 bootstrap 稳健性分析。

第四，统计标准：

- 每个关键条件至少几十到上百个 trial。
- 明确效应量、置信区间、FDR 或层级贝叶斯模型。
- 对照包括随机连接、左右镜像、对称救援、感觉剥夺、记忆增益消融。

## 12. 当前最重要的隐患

- `Eon 内部权重未公开`：公开资料不足以逐参数复现 Eon 系统。
- `行为代理层可能主导视频外观`：视频不能直接等同于连接组自动涌现。
- `食物记忆演示存在天花板效应`：本轮 5 个条件都选 CS+，不能用这组视频证明差异显著。
- `视觉 FlyGym 接口仍可能 fallback`：如果本地 camera binding 失败，视觉视频是 proxy，但连接组传播仍是真实。
- `论文 zip 不是 root-id 原始数据包`：zip 中的结构发现需要进一步和 FlyWire root id 表逐项对齐。
- `Nature 级别需要真实实验闭环`：计算仿真可以形成强假说和预注册实验设计，但不能替代真实行为/成像验证。

## 13. 下一步建议

最有发表潜力的路线不是继续把视频做得更花，而是把“结构侧化 -> 连接组传播 -> 神经 readout -> 行为选择 -> 真实实验验证”打穿。

建议优先做三组实验：

1. `CS+/CS- 弱气味冲突实验`：把 CS+ 浓度降低、CS- 浓度提高，观察记忆是否能压过即时感觉强度。
2. `左右感觉剥夺 vs 左右蘑菇体扰动`：区分外周嗅觉输入偏侧化和中枢记忆回路偏侧化。
3. `右 serotonin / 左 glutamate 通路操控`：根据四卡传播结果，优先验证 DAN、APL、DPM、MBON 相关靶点。

这些实验最容易形成 Nature 风格叙事：不是“我们搭了一个仿真器”，而是“我们用连接组约束仿真预测了一个左右脑记忆分工机制，并用行为/神经实验验证”。
