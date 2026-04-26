# bio_fly：赛博果蝇连接组-功能-行为仿真项目

本项目目录是 `/unify/ydchen/unidit/bio_fly`。目标是把论文 zip 中的 FlyWire 结构组学发现，转成可复现、可统计、可渲染视频的功能仿真证据链，用于研究果蝇左右脑蘑菇体不对称性与嗅觉记忆行为之间的关系。

## 一句话结论

当前版本已经完成从“结构发现”到“功能传播”再到“行为视频”的闭环原型：

1. 论文 zip `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip` 主要是文稿和图包，不是 root-id 级可直接仿真的原始连接组数据包。
2. 项目已接入 `/unify/ydchen/unidit/bio_fly/external/Drosophila_brain_model` 与 FlyWire v783/v630 连接矩阵，可运行 signed propagation 与 Brian2 smoke test。
3. 四卡 GPU 功能传播正式套件已在 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite` 生成结果，`534` 个扰动规格、`3` hop、每步最多 `5000` 个活跃节点，总耗时约 `11.089` 秒。
4. 最新嗅觉记忆仿真套件在 `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite` 生成，按文件时间估计从 `2026-04-26 12:09:56` 到 `2026-04-26 12:21:51`，约 `11.9` 分钟，其中包含屏幕筛选、四卡渲染、统计图和两个长视频。
5. 快速回归测试已通过：在 `/unify/ydchen/unidit/bio_fly` 下运行 `/unify/ydchen/unidit/bio_fly/env/bin/python -m pytest -q`，结果为 `25 passed, 1 warning in 14.93s`。

## 给非生物背景老师的背景解释

### 果蝇为什么适合做这个问题

果蝇大脑小，但有完整的感觉、学习、记忆、运动决策系统。FlyWire 数据集给出了果蝇全脑神经元连接图。连接图类似一张超大“电路图”：节点是神经元，边是突触连接。我们关心的是：左右脑连接结构是否不完全对称，以及这种不对称是否真的会改变行为。

### 蘑菇体是什么

蘑菇体（mushroom body，简称 MB）是果蝇学习和记忆的核心脑区，尤其与嗅觉条件化记忆相关。一个典型实验是：

- 给果蝇闻一种气味 A，同时给予奖励或惩罚；气味 A 叫 `CS+`。
- 给果蝇闻另一种气味 B，不给予奖励或惩罚；气味 B 叫 `CS-`。
- 训练后测试果蝇更接近 `CS+` 还是 `CS-`，就能读出记忆。

### 本项目中的“左右不对称”是什么意思

左右不对称不是说左右脑完全不同，而是指同一类神经元或同一条通路在左半脑和右半脑的连接强度、神经递质输入、传播影响或行为读出上有系统偏差。例如：右侧 serotonin 输入更强，左侧 glutamate 输入更强，这可能造成不同侧的蘑菇体在记忆检索时发挥不同作用。

### 为什么需要仿真

纯结构统计只能说明“接线不一样”，不能直接说明“行为会不一样”。仿真用于补上中间因果链：

`结构不对称 -> 功能传播差异 -> 记忆轴读出差异 -> 行为轨迹差异`

这条链如果成立，就比单纯画连接图更接近可发表的机制性结论。

## 关键变量解释

### 嗅觉记忆变量

- `CS+`：conditioned stimulus positive，训练时与奖励或安全关联的气味。在当前行为仿真中，果蝇应倾向接近它。
- `CS-`：conditioned stimulus negative，训练时未被奖励或与负性关联的气味。在当前行为仿真中，果蝇应相对回避它。
- `cs_plus_intensity`：CS+ 气味强度。数值越大，气味信号越强。
- `cs_minus_intensity`：CS- 气味强度。
- `diffuse_exponent`：气味羽流扩散指数。数值越大，气味空间梯度越陡，果蝇更容易依赖局部嗅觉梯度。
- `spawn_y`：果蝇初始横向位置，用于测试起点偏置是否改变结果。
- `spawn_heading`：果蝇初始朝向，用于测试初始姿态偏置。
- `memory_mode`：记忆状态标签，例如急性记忆、长期记忆、记忆衰退、感觉-记忆冲突等。
- `attractive_gain`：CS+ 对行为吸引项的增益。绝对值越大，记忆驱动越强。
- `aversive_gain`：CS- 对行为排斥或竞争项的增益。
- `lateral_memory_bias`：左右记忆通路偏置。正负号表示偏向不同侧，绝对值越大，侧化越强。

### 行为读出变量

- `n_trials`：该条件下重复试验数。
- `cs_plus_choice_rate`：选择 CS+ 的比例。`1.0` 表示所有试验都选择 CS+，`0.5` 接近随机或左右条件相互抵消。
- `mean_distance_to_cs_plus`：终点或平均轨迹到 CS+ 的距离，越小表示越接近 CS+。
- `mean_approach_margin`：接近 CS+ 相对 CS- 的优势，越大表示更偏向 CS+。
- `mean_signed_final_y`：终点横向位置的带符号坐标，用于表示左右选择方向。
- `mean_path_length`：轨迹总长度，用于判断行为是否只是静止或运动不足造成。
- `left_cs_plus_margin` / `right_cs_plus_margin`：CS+ 放在左侧或右侧时分别计算的接近优势。
- `side_specific_margin_shift`：左右摆放 CS+ 后行为优势的差值，用于检测侧化或空间偏差。

### 功能传播变量

- `condition`：扰动条件名称，例如 `right_serotonin_kc_activate` 表示激活右侧 serotonin 相关 KC 输入。
- `KC`：Kenyon cell，蘑菇体主要内在神经元，是嗅觉记忆编码核心。
- `MBON`：mushroom body output neuron，蘑菇体输出神经元，把记忆状态传给下游决策网络。
- `DAN`：dopaminergic neuron，多巴胺神经元，常参与奖励、惩罚和记忆更新。
- `APL`：anterior paired lateral neuron，蘑菇体内广泛抑制调控细胞。
- `DPM`：dorsal paired medial neuron，与记忆维持和蘑菇体调控相关。
- `memory_axis_abs_mass`：扰动传播到记忆相关轴的总绝对响应量。
- `mbon_abs_mass`、`dan_abs_mass`、`apl_abs_mass`、`dpm_abs_mass`：分别传播到 MBON、DAN、APL、DPM 的响应量。
- `response_laterality_abs`：功能响应的左右偏侧化强度。
- `effect_z`：实际扰动相对随机对照的 z 分数。绝对值越大，偏离随机越明显。
- `fdr_q`：多重比较校正后的显著性值。通常 `fdr_q < 0.05` 可作为统计显著候选，但仍需真实实验验证。

## 当前目录结构与含义

- `/unify/ydchen/unidit/bio_fly/README.md`：项目总入口，解释目标、变量、命令和结果。
- `/unify/ydchen/unidit/bio_fly/env`：Python 虚拟环境，已包含 PyTorch CUDA、FlyGym/MuJoCo、Brian2、统计和绘图库。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly`：核心 Python 包。
- `/unify/ydchen/unidit/bio_fly/scripts`：一键运行脚本。
- `/unify/ydchen/unidit/bio_fly/tests`：回归测试。
- `/unify/ydchen/unidit/bio_fly/data`：本地数据目录，不建议提交到 Git。
- `/unify/ydchen/unidit/bio_fly/external`：外部模型和注释仓库，不建议提交到 Git。
- `/unify/ydchen/unidit/bio_fly/outputs`：所有仿真、统计、图表、视频输出。
- `/unify/ydchen/unidit/bio_fly/docs`：中文技术报告和实验报告。
- `/unify/ydchen/unidit/bio_fly/paper`：按 Nature 子刊叙事整理的论文草稿、图表清单和补充材料说明。

## 主要代码模块

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/repro.py`：复现 Shiu 等 Drosophila brain model 的最小封装。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/paper_zip.py`：解析用户论文 zip 中的 tex、markdown 和 figure inventory。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/asymmetry.py`：蘑菇体左右结构不对称统计。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/nt_analysis.py`：KC 输入神经递质比例的左右差异分析。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/propagation.py`：基于连接矩阵的 signed multi-hop propagation，可走 CPU 或 PyTorch CUDA。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/functional.py`：把结构候选转成功能扰动 manifest。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/model_linkage.py`：把真实 KC-NT 侧化候选连接到行为参数。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/experiment_suite.py`：四卡并行扰动、随机对照、显著性统计和机制视频。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/behavior.py`：FlyGym/MuJoCo 行为仿真、轨迹记录和视频渲染。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/lateralization_behavior.py`：侧化剂量扫描、镜像翻转、对称救援和长视频。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/olfactory_perturbation.py`：明确 CS+/CS- 气味强度、长期记忆、单侧嗅觉通道和冲突实验。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/structure_behavior_linkage.py`：结构-功能-行为联动统计。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/target_prioritization.py`：从全脑传播结果筛选可实验验证的 MBON/DAN/APL/DPM 靶点。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/video.py`：拼接论文补充视频。

## 上一个主要命令运行多久、得到什么

### 四卡功能传播正式套件

命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
python /unify/ydchen/unidit/bio_fly/scripts/run_four_card_experiment_suite.py --devices cuda:0 cuda:1 cuda:2 cuda:3 --steps 3 --max-active 5000 --n-random-per-family 128 --output-dir /unify/ydchen/unidit/bio_fly/outputs/four_card_suite
```

运行结论：

- 总扰动规格 `n_specs = 534`。
- GPU 设备：`cuda:0, cuda:1, cuda:2, cuda:3`。
- 总耗时 `11.089` 秒。
- 四个 worker 分别耗时：`8.537`、`8.657`、`8.218`、`8.704` 秒。
- 输出目录：`/unify/ydchen/unidit/bio_fly/outputs/four_card_suite`。

关键结果文件：

- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_run_info.json`：运行参数和每张 GPU 的耗时。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv`：真实扰动对随机对照的经验显著性。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_top_targets.csv`：全脑 top target 候选。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_signed_propagation_responses.parquet`：每个扰动传播到目标神经元的响应矩阵。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/CYBER_FLY_NATURE_UPGRADE_REPORT.md`：四卡套件自动报告。

统计发现：

| actual_condition            | metric                  |   actual_value |   effect_z |   empirical_p_two_sided |   n_null |     fdr_q |
|:----------------------------|:------------------------|---------------:|-----------:|------------------------:|---------:|----------:|
| right_serotonin_kc_activate | dan_abs_mass            |       0.186214 |    4.23566 |               0.0155039 |      128 | 0.0381634 |
| right_serotonin_kc_activate | apl_abs_mass            |       0.148781 |   -4.04281 |               0.0155039 |      128 | 0.0381634 |
| right_serotonin_kc_activate | dpm_abs_mass            |       0.126599 |    4.01922 |               0.0155039 |      128 | 0.0381634 |
| right_serotonin_kc_activate | response_laterality_abs |       0.842948 |   -2.70813 |               0.0155039 |      128 | 0.0381634 |
| right_serotonin_kc_activate | max_abs_target_score    |       0.148627 |   -3.82696 |               0.0155039 |      128 | 0.0381634 |
| left_glutamate_kc_activate  | memory_axis_abs_mass    |       1.14883  |    3.08075 |               0.0155039 |      128 | 0.0381634 |
| left_glutamate_kc_activate  | mbon_abs_mass           |       0.349468 |   -5.35489 |               0.0155039 |      128 | 0.0381634 |
| left_glutamate_kc_activate  | dan_abs_mass            |       0.190758 |    7.18757 |               0.0155039 |      128 | 0.0381634 |
| left_glutamate_kc_activate  | mbin_abs_mass           |       0.3043   |    2.92339 |               0.0155039 |      128 | 0.0381634 |
| left_glutamate_kc_activate  | apl_abs_mass            |       0.150568 |   -4.01147 |               0.0155039 |      128 | 0.0381634 |
| left_glutamate_kc_activate  | dpm_abs_mass            |       0.153731 |    7.18411 |               0.0155039 |      128 | 0.0381634 |
| left_glutamate_kc_activate  | response_laterality_abs |      -0.830021 |    6.99079 |               0.0155039 |      128 | 0.0381634 |
| left_glutamate_kc_activate  | max_abs_target_score    |       0.153376 |   -2.65301 |               0.0155039 |      128 | 0.0381634 |

### 最新嗅觉记忆扰动套件

命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
python /unify/ydchen/unidit/bio_fly/scripts/run_olfactory_perturbation_suite.py --output-dir /unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite --render-devices 0 1 2 3 --screen-trials 2 --screen-run-time 0.9 --render-run-time 2.0 --camera-play-speed 0.12
```

运行结论：

- 按文件时间估算总耗时约 `11.9` 分钟。
- 使用渲染设备：`0, 1, 2, 3`。
- 屏幕筛选每条件 `2` 次重复，运行时间 `0.9` 秒。
- 长视频渲染运行时间 `2.0` 秒，相机播放速度 `0.12`，帧率 `30` fps。
- 输出目录：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite`。

关键结果文件：

- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/conditions/olfactory_condition_table.csv`：所有嗅觉条件和参数。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/olfactory_behavior_summary.csv`：每个条件的行为统计。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/figures/Fig_olfactory_perturbation_summary.png`：论文图草稿。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_left_long.mp4`：CS+ 在左侧时的对比视频。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_right_long.mp4`：CS+ 在右侧时的对比视频。
- `/unify/ydchen/unidit/bio_fly/docs/OLFACTORY_PERTURBATION_MEMORY_CN.md`：完整中文报告。

嗅觉条件结果摘要：

| condition                     |   n_trials |   cs_plus_choice_rate |   mean_approach_margin |   mean_signed_final_y |   cs_plus_intensity |   cs_minus_intensity | memory_mode             |
|:------------------------------|-----------:|----------------------:|-----------------------:|----------------------:|--------------------:|---------------------:|:------------------------|
| acute_balanced_memory         |          6 |              0.833333 |                3.99337 |               3.68749 |                1    |                 1    | acute                   |
| cs_plus_weak_conflict         |          6 |              0.833333 |                3.78446 |               3.26733 |                0.28 |                 1    | sensory_memory_conflict |
| initial_state_mirror          |          6 |              1        |                5.36599 |               5.20606 |                1    |                 1    | initial_state_control   |
| left_sensor_deprivation       |          6 |              1        |                5.08019 |               4.40312 |                1    |                 1    | sensory_asymmetry       |
| long_term_memory_consolidated |          6 |              0.833333 |                3.96725 |               3.52861 |                1    |                 1    | long_term               |
| long_term_memory_decay        |          6 |              1        |                5.29904 |               4.76429 |                1    |                 1    | long_term_decay         |
| narrow_plume_high_gradient    |          4 |              1        |                4.51364 |               4.01492 |                1    |                 1    | plume_geometry          |
| right_sensor_deprivation      |          6 |              0.833333 |                4.07821 |               3.78071 |                1    |                 1    | sensory_asymmetry       |
| weak_odor_high_memory         |          6 |              1        |                5.0327  |               4.37376 |                0.35 |                 0.35 | weak_cue_retrieval      |
| wide_plume_low_gradient       |          4 |              1        |                8.21895 |               5.19931 |                1    |                 1    | plume_geometry          |

## 目前验证了论文 zip 的哪些结论

已验证或支持的方向：

1. `右侧 serotonin 相关 KC 输入` 和 `左侧 glutamate 相关 KC 输入` 不是普通随机扰动；它们对 DAN/APL/DPM/response laterality 等记忆轴指标有 FDR 校正后的显著差异。
2. 结构-功能-行为联动表明 `left_mb_glutamate_enriched` 条件在 approach margin 上较强，说明左侧 glutamate 相关结构差异可以映射到行为读出。
3. 嗅觉实验把“闻到什么”明确成 CS+/CS- 两种气味源，并通过强度、扩散、起点、长期记忆和单侧感觉剥夺做反事实控制。
4. 靶点优先级把论文中的宏观结构差异落到可操作神经元家族：`DPM`、`APL`、`MBON03`、`MBON09`、`MBON12`、`MBON13`、`PPL103`。

尚未完成、不能夸大的部分：

1. 当前 zip 未提供 root-id 级原始可仿真数据，因此 zip 内所有结构发现还不能逐个神经元完全复算。
2. 当前行为模型是可解释的低维 FlyGym 行为读出，不是全脑 spike-level closed-loop embodied emulation。
3. 当前结果达到“论文假说生成 + 预实验仿真证据”级别，距离 Nature 级结论仍需要真实行为实验、遗传操控、钙成像或电生理验证。

## 当前最重要的开放性科学假说

### 假说 H1：左右蘑菇体的神经递质侧化形成记忆检索的双轴控制

右侧 serotonin 相关 KC 输入可能更强地调节 DAN/DPM/APL 记忆轴，左侧 glutamate 相关 KC 输入可能更强地影响 approach margin。这个结果提示左右蘑菇体不是简单冗余，而可能分别承担不同的记忆更新和行为读出权重。

### 假说 H2：长期记忆增益可以补偿弱气味输入

`weak_odor_high_memory` 在低浓度 CS+/CS- 下仍保持较高 CS+ 选择，说明当感觉输入弱时，记忆增益可能主导行为。

### 假说 H3：强 CS- 感觉输入可以挑战 CS+ 记忆

`cs_plus_weak_conflict` 把 `cs_plus_intensity` 降到 `0.28`，同时保持 `cs_minus_intensity = 1.0`，出现一部分 CS- 选择。这个条件适合设计真实行为实验：检测记忆是否能覆盖即时感觉优势。

### 假说 H4：单侧嗅觉感觉通道与蘑菇体记忆侧化可以被拆分

`left_sensor_deprivation` 和 `right_sensor_deprivation` 分别削弱单侧嗅觉输入，允许区分“感觉输入偏侧化”和“记忆回路偏侧化”。如果两者可分离，将是比单纯结构不对称更强的机制性结果。

## Nature 子刊级后续实验设计

### 真实行为实验

- 气味 A：建议用 `3-octanol` 或 `isoamyl acetate` 作为 CS+。
- 气味 B：建议用另一种可区分气味作为 CS-。
- 训练：CS+ 与糖奖励或电击惩罚配对，CS- 不配对。
- 测试：T-maze 或虚拟现实闭环装置中同时呈现 CS+ 和 CS-。
- 关键对照：交换 CS+/CS- 左右位置，交换气味身份，设置弱 CS+ 强 CS- 冲突条件，设置训练后延迟以测试长期记忆。

### 神经操控实验

- 左侧 glutamate 相关 KC 输入增强或抑制。
- 右侧 serotonin 相关 KC 输入增强或抑制。
- APL、DPM、MBON03/09/12/13、PPL103 定点操控。
- 读出指标包括选择率、轨迹、速度、转向偏置、钙成像响应。

### 统计标准

- 每个条件至少 `n >= 30` 只果蝇或独立轨迹。
- 主指标预注册为 `approach margin` 和 `side-specific margin shift`，不要只看 `choice rate`，因为 choice rate 容易饱和。
- 所有多重比较使用 FDR 校正。
- 报告 effect size、置信区间和随机化/镜像反事实对照。

## 资源与存储

当前磁盘占用：

- `/unify/ydchen/unidit/bio_fly`：`11G`
- `/unify/ydchen/unidit/bio_fly/outputs`：`277M`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite`：`110M`
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite`：`60M`
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite`：`83M`
- `/unify/ydchen/unidit/bio_fly/env`：`9.0G`
- `/unify/ydchen/unidit/bio_fly/external`：`421M`
- `/unify/ydchen/unidit/bio_fly/data`：`839M`

本机 GPU 状态已能使用四张卡。当前观测到 4 张 `NVIDIA H20Z`，每张约 `143771 MiB` 显存。四卡 propagation 对当前规模已经足够；更大规模瓶颈主要是 I/O、parquet 写入和视频渲染，不是矩阵传播本身。

## 一键复现命令

```bash
export http_proxy=http://192.168.32.28:18000
export https_proxy=http://192.168.32.28:18000
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python -m pytest -q
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_four_card_experiment_suite.py --devices cuda:0 cuda:1 cuda:2 cuda:3 --steps 3 --max-active 5000 --n-random-per-family 128 --output-dir /unify/ydchen/unidit/bio_fly/outputs/four_card_suite
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_lateralization_behavior_suite.py --stats /unify/ydchen/unidit/bio_fly/outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv --output-dir /unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite --render-devices 0 1 2 3 --dose-trials 2 --dose-run-time 0.8 --render-run-time 1.6 --camera-play-speed 0.12
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_olfactory_perturbation_suite.py --output-dir /unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite --render-devices 0 1 2 3 --screen-trials 2 --screen-run-time 0.9 --render-run-time 2.0 --camera-play-speed 0.12
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/analyze_structure_behavior_linkage.py
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/prioritize_memory_axis_targets.py
```

## 论文与报告入口

- `/unify/ydchen/unidit/bio_fly/paper/NATURE_STYLE_DRAFT_CN.md`：面向 Nature 子刊的中文论文草稿。
- `/unify/ydchen/unidit/bio_fly/paper/FIGURE_AND_VIDEO_INDEX_CN.md`：图和视频材料索引。
- `/unify/ydchen/unidit/bio_fly/docs/RUN_FINDINGS_AND_IMPROVEMENTS_CN.md`：本次整理的完整发现、改进和下一步计划。
- `/unify/ydchen/unidit/bio_fly/docs/OLFACTORY_PERTURBATION_MEMORY_CN.md`：嗅觉记忆实验报告。
- `/unify/ydchen/unidit/bio_fly/docs/LATERALIZATION_BEHAVIOR_SIMULATION_CN.md`：侧化行为仿真报告。
- `/unify/ydchen/unidit/bio_fly/docs/STRUCTURE_BEHAVIOR_LINKAGE_CN.md`：结构-功能-行为联动报告。

## 当前最需要补充的数据

要把结果从“仿真支持假说”推进到“可冲击顶刊的发现”，需要补充：

1. `/unify/ydchen/unidit/bio_fly/data/raw/flywire_root_id_metadata.csv`：每个神经元 root id、左右侧、cell type、super class、脑区。
2. `/unify/ydchen/unidit/bio_fly/data/raw/flywire_synapse_nt_inputs.csv`：每个 KC 或 MB 相关神经元的输入突触、神经递质预测、权重和左右侧。
3. 真实行为实验数据：每只果蝇每次试验的气味、训练范式、左右位置、轨迹和选择。
4. 真实神经操控或成像数据：左/右 glutamate、serotonin、APL、DPM、MBON、DAN 的响应。

## 不应在论文中夸大的表述

可以写：本框架把结构侧化发现转化为可检验的功能传播和行为假说，并发现若干通过随机对照显著的记忆轴候选。

不应写：已经证明了果蝇左右蘑菇体在真实生物中必然承担某种功能分工。这个结论需要真实实验验证。

## 最新数据下载与 MB 连接组深挖

本轮已从公开数据源下载并确认完整 FlyWire v783 数据：Zenodo `https://zenodo.org/records/10676866` 与 GitHub `https://github.com/flyconnectome/flywire_annotations`。

新增本地数据：

- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/per_neuron_neuropil_count_post_783.feather`
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/flywire_synapses_783.feather`
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866_downloads_extended.csv`

新增分析与仿真：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/mb_connectome_discovery.py`：真实 FlyWire v783 连接表驱动的蘑菇体侧化挖掘。
- `/unify/ydchen/unidit/bio_fly/scripts/run_mb_connectome_discovery.py`：一键生成结构图、候选表和机制视频。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/MB_CONNECTOME_DISCOVERY_CN.md`：自动报告。
- `/unify/ydchen/unidit/bio_fly/docs/DATA_DOWNLOAD_AND_MB_DISCOVERY_CN.md`：面向论文补充的中文报告。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/videos/mb_lateralization_mechanism.mp4`：结构机制视频。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior/videos/mb_discovery_behavior_cs_plus_left.mp4`：新结构候选行为仿真视频，CS+ 左侧。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior/videos/mb_discovery_behavior_cs_plus_right.mp4`：新结构候选行为仿真视频，CS+ 右侧。

新增发现：直接挖掘 FlyWire v783 聚合连接表后，`KC→KC`、`APL→KC`、`KC→DPM`、`DPM→KC` 等反馈/内在环路整体偏左，而 `DAN→MBON` 与 `MBON→DAN` 有轻度右偏；`KC→MBON` 总体近似平衡。这支持一个更具体的论文假说：左右蘑菇体侧化可能不是全局强弱差异，而是左侧偏反馈稳定、右侧偏调制输出。

新增复现命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/download_flywire_data.py --prepare-annotations --download-all
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_mb_connectome_discovery.py --output-dir /unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery
```

## 食物气味记忆功能仿真与文章修改

本轮已把 `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip` 解压到 `/unify/ydchen/unidit/bio_fly/paper`，并修改主文 `/unify/ydchen/unidit/bio_fly/paper/main_merged.tex`。新增内容把原文“KC 输入 NT 侧化”扩展为“左侧 KC-APL-DPM 反馈稳定 / 右侧 DAN-MBON 输出调制”的功能环路模型。

新增食物气味记忆仿真：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/food_memory.py`
- `/unify/ydchen/unidit/bio_fly/scripts/run_food_memory_suite.py`
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/FOOD_MEMORY_SIMULATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/food_memory_behavior_summary.csv`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`

这里的“食物”被实现为糖奖励相关气味源 `CS+`，竞争气味为 `CS-`。FlyGym 当前环境没有真实可摄取糖滴对象，因此该实验是食物气味记忆仿真，不应在论文中写成真实进食行为。主指标建议使用 `mean_food_approach_margin`、`mean_signed_final_y` 和 `mean_path_length`，因为 `food_choice_rate` 在当前小样本中容易饱和。

复现命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_food_memory_suite.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/food_memory_suite \
  --paper-video-dir /unify/ydchen/unidit/bio_fly/paper/video \
  --n-trials 1 --run-time 0.9 --render-device 0
```

详细说明见 `/unify/ydchen/unidit/bio_fly/docs/ARTICLE_REVISION_AND_FUNCTIONAL_SIMULATION_CN.md`。
