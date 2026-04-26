# 论文草稿：果蝇蘑菇体左右侧化连接组预测嗅觉记忆行为

保存路径：`/unify/ydchen/unidit/bio_fly/paper/NATURE_STYLE_DRAFT_CN.md`

## 标题

连接组侧化揭示果蝇蘑菇体嗅觉记忆检索的左右分工

## 摘要

左右脑不对称是神经系统组织的基本原则，但在小型全脑连接组中，结构侧化如何转化为记忆行为差异仍缺乏可计算的机制链条。我们构建了 `/unify/ydchen/unidit/bio_fly` 赛博果蝇仿真框架，将 FlyWire 蘑菇体结构发现、signed multi-hop functional propagation、FlyGym 行为轨迹和嗅觉 CS+/CS- 记忆任务连接起来。基于论文 zip `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip` 中的蘑菇体左右结构假说，我们系统扰动右侧 serotonin 相关 KC 输入和左侧 glutamate 相关 KC 输入，并使用 matched random controls 估计经验显著性。四卡 GPU 套件完成 `534` 个扰动规格，显示候选侧化扰动在 DAN、APL、DPM 和 response laterality 上达到 FDR 显著。进一步的行为仿真表明，左侧 glutamate-enriched 条件增强 CS+ approach margin，而弱 CS+ 强 CS- 冲突、长期记忆衰退和单侧嗅觉剥夺可作为区分感觉侧化与记忆侧化的关键实验。该框架提出了一个可实验检验的模型：左右蘑菇体并非简单冗余，而是通过不同神经递质输入和记忆轴下游调控形成可分离的嗅觉记忆控制通道。

## 引言

果蝇蘑菇体是研究学习和记忆的经典系统。传统实验已经证明 Kenyon cell、MBON、多巴胺神经元、APL 和 DPM 等成分共同参与气味关联学习。然而，很多研究默认左右蘑菇体近似对称，或者只把左右差异作为技术噪声处理。FlyWire 全脑连接组使我们能够重新审视这一假设：如果左右蘑菇体在神经递质输入、连接拓扑和下游读出上存在系统差异，那么这种差异是否会影响记忆检索行为？

本研究的问题不是“连接是否不对称”本身，而是“这种不对称是否有功能意义”。为此，我们建立从结构到行为的四层证据链：

1. 结构层：从论文 zip 和 FlyWire 相关数据中提取蘑菇体左右侧化候选。
2. 功能层：在全脑连接矩阵上进行 signed propagation，估计扰动对记忆轴的影响。
3. 行为层：在 FlyGym/MuJoCo 中用 CS+/CS- 嗅觉任务读出轨迹和选择。
4. 统计层：用随机对照、镜像对照、剂量扫描和 FDR 校正避免把普通网络噪声误判为机制。

## 方法

### 数据来源

- 项目根目录：`/unify/ydchen/unidit/bio_fly`。
- 论文 zip：`/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip`。
- 外部全脑模型：`/unify/ydchen/unidit/bio_fly/external/Drosophila_brain_model`。
- 输出目录：`/unify/ydchen/unidit/bio_fly/outputs`。

zip 文件包含 tex 文稿和图，而不是 root-id 级神经元表，因此我们将其作为结构假说来源，而不是直接可仿真的原始数据源。

### 变量定义

- `CS+`：训练时与奖励或安全关联的气味，测试时应被接近。
- `CS-`：未奖励或负性关联的气味，测试时应相对回避。
- `KC`：Kenyon cell，蘑菇体主要记忆编码神经元。
- `MBON`：蘑菇体输出神经元，向下游决策区传递记忆读出。
- `DAN`：多巴胺神经元，参与奖励、惩罚和记忆更新。
- `APL`：蘑菇体广泛抑制神经元，调节 KC 稀疏编码。
- `DPM`：与记忆维持相关的蘑菇体调控神经元。
- `memory_axis_abs_mass`：扰动传播到记忆相关细胞家族的总响应强度。
- `response_laterality_abs`：功能响应在左右半脑上的不对称强度。
- `mean_approach_margin`：行为轨迹对 CS+ 的接近优势，是主要连续行为指标。
- `cs_plus_choice_rate`：选择 CS+ 的比例，是直观但容易饱和的二分类指标。

### 四卡功能传播

命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
python /unify/ydchen/unidit/bio_fly/scripts/run_four_card_experiment_suite.py --devices cuda:0 cuda:1 cuda:2 cuda:3 --steps 3 --max-active 5000 --n-random-per-family 128 --output-dir /unify/ydchen/unidit/bio_fly/outputs/four_card_suite
```

该实验使用四张 GPU 并行计算真实扰动与 matched random controls。真实扰动包括 `right_serotonin_kc_activate`、`left_glutamate_kc_activate` 及其组合；随机对照保持侧别或细胞族规模相近，用于估计经验 p 值。

### 嗅觉记忆行为任务

命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
python /unify/ydchen/unidit/bio_fly/scripts/run_olfactory_perturbation_suite.py --output-dir /unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite --render-devices 0 1 2 3 --screen-trials 2 --screen-run-time 0.9 --render-run-time 2.0 --camera-play-speed 0.12
```

行为任务中，虚拟果蝇处于两个气味源之间：一个是 `CS+`，另一个是 `CS-`。模型记录轨迹、终点、路径长度和靠近哪种气味。通过调节 `cs_plus_intensity`、`cs_minus_intensity`、`lateral_memory_bias`、`spawn_y` 和单侧感觉剥夺，可以区分记忆驱动、感觉驱动和空间偏置。

## 结果

### 结果 0：公开可复现的 CyberFly 不是“纯连接组自动涌现”，而是连接组约束的分层闭环

我们重新核查了 Eon/CyberFly 公开说明，并在 `/unify/ydchen/unidit/bio_fly/src/bio_fly/eon_multimodal_benchmark.py` 中实现公开可复现版本。该版本把系统拆成四层：FlyWire sensory seed 到全脑 signed propagation，目标神经元/readout family 聚合，DN 或行为代理读出，以及 FlyGym/NeuroMechFly 身体视频渲染。这个分层非常关键，因为 walking、grooming、feeding 和 steering 的可见运动并不是由连接组单独产生，而是依赖行为 readout 和低维/训练控制器。

本轮多模态复现命令为：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
python /unify/ydchen/unidit/bio_fly/scripts/run_eon_multimodal_benchmark.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark \
  --render-device 0 \
  --propagation-device cuda:0
```

该命令本轮耗时约 `1 分 34 秒`，输出目录为 `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark`。连接组 readout 表位于 `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_readout_summary.csv`。

| condition | n_seed_neurons | active_response_neurons | absolute_mass | descending_abs_mass | memory_axis_abs_mass | visual_projection_abs_mass | gustatory_abs_mass | mechanosensory_abs_mass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| olfactory_food_memory | 255 | 7376 | 2.664589 | 0.011488 | 0.245349 | 1.320785 | 0.000028 | 0.000000 |
| visual_object_tracking | 255 | 11152 | 1.577666 | 0.203957 | 0.075750 | 0.885637 | 0.005476 | 0.005376 |
| gustatory_feeding | 256 | 6895 | 1.645239 | 0.255412 | 0.004189 | 0.945583 | 0.225318 | 0.118458 |
| mechanosensory_grooming | 256 | 7802 | 1.878642 | 0.463450 | 0.001634 | 1.111238 | 0.027579 | 0.146880 |

这组结果的论文意义是：不同感觉通道在同一个 FlyWire 图上产生不同 readout profile，说明该框架不是只为嗅觉记忆任务定制的动画系统。与此同时，我们在文稿中明确限制：当前公开复现不能声称“连接组单独自动涌现完整果蝇行为”，只能声称“连接组约束的 sensory-to-readout profile 与身体代理行为可组成可检验闭环”。

### 结果 1：四卡传播把结构侧化候选连接到记忆轴

四卡运行耗时 `11.089` 秒，生成 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv`。显著指标如下：

| actual_condition            | metric                  |   actual_value |   effect_z |     fdr_q |
|:----------------------------|:------------------------|---------------:|-----------:|----------:|
| right_serotonin_kc_activate | dan_abs_mass            |       0.186214 |    4.23566 | 0.0381634 |
| right_serotonin_kc_activate | apl_abs_mass            |       0.148781 |   -4.04281 | 0.0381634 |
| right_serotonin_kc_activate | dpm_abs_mass            |       0.126599 |    4.01922 | 0.0381634 |
| right_serotonin_kc_activate | response_laterality_abs |       0.842948 |   -2.70813 | 0.0381634 |
| right_serotonin_kc_activate | max_abs_target_score    |       0.148627 |   -3.82696 | 0.0381634 |
| left_glutamate_kc_activate  | memory_axis_abs_mass    |       1.14883  |    3.08075 | 0.0381634 |
| left_glutamate_kc_activate  | mbon_abs_mass           |       0.349468 |   -5.35489 | 0.0381634 |
| left_glutamate_kc_activate  | dan_abs_mass            |       0.190758 |    7.18757 | 0.0381634 |
| left_glutamate_kc_activate  | mbin_abs_mass           |       0.3043   |    2.92339 | 0.0381634 |
| left_glutamate_kc_activate  | apl_abs_mass            |       0.150568 |   -4.01147 | 0.0381634 |
| left_glutamate_kc_activate  | dpm_abs_mass            |       0.153731 |    7.18411 | 0.0381634 |
| left_glutamate_kc_activate  | response_laterality_abs |      -0.830021 |    6.99079 | 0.0381634 |
| left_glutamate_kc_activate  | max_abs_target_score    |       0.153376 |   -2.65301 | 0.0381634 |

解释：右侧 serotonin 相关 KC 扰动和左侧 glutamate 相关 KC 扰动均能显著影响 DAN/APL/DPM 或 response laterality。这说明论文中的结构不对称候选可以映射到记忆调控轴，而不是仅停留在形态或拓扑描述。

### 结果 2：结构-功能-行为联动支持左侧 glutamate 轴影响 approach margin

联动分析文件为 `/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/functional_behavior_linkage.csv`。

| condition                   | functional_condition                            |   cs_plus_choice_rate |   mean_approach_margin |   memory_axis_abs_mass |   response_laterality_abs |
|:----------------------------|:------------------------------------------------|----------------------:|-----------------------:|-----------------------:|--------------------------:|
| mirror_reversal             | left_glutamate_activate_silence_right_serotonin |                   1   |                4.52957 |                1.14915 |                 -0.830289 |
| amplified_left_axis         | left_glutamate_kc_activate                      |                   0.5 |                2.19707 |                1.14883 |                 -0.830021 |
| left_mb_glutamate_enriched  | left_glutamate_kc_activate                      |                   1   |                5.86938 |                1.14883 |                 -0.830021 |
| bilateral_memory_blunted    | right_serotonin_activate_silence_left_glutamate |                   0.5 |                2.60023 |                1.10769 |                  0.843098 |
| amplified_right_axis        | right_serotonin_kc_activate                     |                   0.5 |                2.58335 |                1.10754 |                  0.842948 |
| right_mb_serotonin_enriched | right_serotonin_kc_activate                     |                   1   |                3.311   |                1.10754 |                  0.842948 |

`left_mb_glutamate_enriched` 条件的 `mean_approach_margin` 较高，提示左侧 glutamate-enriched 结构差异可能更直接影响接近行为。相比之下，`cs_plus_choice_rate` 在多个条件中接近饱和，因此连续轨迹指标更适合论文主图。

### 结果 3：嗅觉冲突任务给出可实验验证的反事实预测

嗅觉扰动总结图位于 `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/figures/Fig_olfactory_perturbation_summary.png`。两个视频位于：

- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_left_long.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_right_long.mp4`

关键条件：

| condition                     |   cs_plus_choice_rate |   mean_approach_margin |   cs_plus_intensity |   cs_minus_intensity | memory_mode             |
|:------------------------------|----------------------:|-----------------------:|--------------------:|---------------------:|:------------------------|
| acute_balanced_memory         |              0.833333 |                3.99337 |                1    |                 1    | acute                   |
| cs_plus_weak_conflict         |              0.833333 |                3.78446 |                0.28 |                 1    | sensory_memory_conflict |
| initial_state_mirror          |              1        |                5.36599 |                1    |                 1    | initial_state_control   |
| left_sensor_deprivation       |              1        |                5.08019 |                1    |                 1    | sensory_asymmetry       |
| long_term_memory_consolidated |              0.833333 |                3.96725 |                1    |                 1    | long_term               |
| long_term_memory_decay        |              1        |                5.29904 |                1    |                 1    | long_term_decay         |
| narrow_plume_high_gradient    |              1        |                4.51364 |                1    |                 1    | plume_geometry          |
| right_sensor_deprivation      |              0.833333 |                4.07821 |                1    |                 1    | sensory_asymmetry       |
| weak_odor_high_memory         |              1        |                5.0327  |                0.35 |                 0.35 | weak_cue_retrieval      |
| wide_plume_low_gradient       |              1        |                8.21895 |                1    |                 1    | plume_geometry          |

`cs_plus_weak_conflict` 是最适合真实实验的条件：CS+ 强度被削弱到 `0.28`，CS- 强度保持 `1.0`。如果真实果蝇仍选择 CS+，说明记忆能覆盖强即时感觉输入；如果转向 CS-，说明感觉强度主导决策。左右蘑菇体操控可进一步揭示这种竞争是否侧化。

### 结果 4：候选实验靶点集中在 APL、DPM、MBON 和 DAN

靶点表位于 `/unify/ydchen/unidit/bio_fly/outputs/target_prioritization/memory_axis_target_family_summary.csv`。

| condition                                       | cell_class   | cell_type   |   n_targets |   mean_priority_score | dominant_side   | dominant_nt   |
|:------------------------------------------------|:-------------|:------------|------------:|----------------------:|:----------------|:--------------|
| left_alpha_prime_beta_prime_glutamate_activate  | MBIN         | DPM         |           1 |             0.239982  | left            | dopamine      |
| left_alpha_prime_beta_prime_glutamate_activate  | MBIN         | APL         |           1 |             0.194197  | left            | gaba          |
| left_alpha_prime_beta_prime_glutamate_activate  | MBON         | MBON03      |           1 |             0.0757877 | right           | glutamate     |
| left_alpha_prime_beta_prime_glutamate_activate  | MBON         | MBON13      |           1 |             0.0345605 | left            | acetylcholine |
| left_alpha_prime_beta_prime_glutamate_activate  | MBON         | MBON09      |           2 |             0.0313808 | right           | gaba          |
| left_alpha_prime_beta_prime_glutamate_activate  | MBON         | MBON04      |           1 |             0.0222756 | right           | glutamate     |
| left_alpha_prime_beta_prime_glutamate_activate  | MBON         | MBON12      |           2 |             0.0211961 | left            | acetylcholine |
| left_alpha_prime_beta_prime_glutamate_activate  | DAN          | PPL103      |           2 |             0.0168901 | left            | dopamine      |
| left_alpha_prime_beta_prime_glutamate_activate  | MBON         | MBON05      |           1 |             0.0162033 | right           | glutamate     |
| left_glutamate_activate_silence_right_serotonin | MBIN         | DPM         |           1 |             0.300353  | left            | dopamine      |
| left_glutamate_activate_silence_right_serotonin | MBIN         | APL         |           1 |             0.293601  | left            | gaba          |
| left_glutamate_activate_silence_right_serotonin | MBON         | MBON03      |           1 |             0.0617738 | right           | glutamate     |
| left_glutamate_activate_silence_right_serotonin | MBON         | MBON06      |           1 |             0.0575754 | right           | glutamate     |
| left_glutamate_activate_silence_right_serotonin | MBON         | MBON22      |           1 |             0.0312591 | left            | acetylcholine |
| left_glutamate_activate_silence_right_serotonin | MBON         | MBON07      |           2 |             0.0307233 | left            | glutamate     |
| left_glutamate_activate_silence_right_serotonin | MBON         | MBON05      |           1 |             0.0293706 | right           | glutamate     |

这些靶点可转化为遗传操控、钙成像或光遗传实验。优先级最高的是左侧 `DPM` 和左侧 `APL`，与 `left_glutamate_kc_activate` 条件相连。

## 图表和视频插入建议

### Figure 1：框架图

建议引用或重画 zip 中的结构示意，并叠加本项目流程：结构统计、signed propagation、FlyGym 行为、真实实验闭环。候选源文件在 `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip::figures/Fig1_mushroom_body_nt_system.png`。

### Figure 2：四卡功能传播结果

使用 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv` 画 volcano 或 forest plot，突出 DAN、APL、DPM、response laterality 的 FDR 显著项。

### Figure 3：结构-功能-行为联动图

使用 `/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/Fig_structure_behavior_linkage.png`。

![Figure 3 structure-function-behavior linkage](/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/Fig_structure_behavior_linkage.png)

### Figure 4：嗅觉记忆扰动图

使用 `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/figures/Fig_olfactory_perturbation_summary.png`。

![Figure 4 olfactory perturbation summary](/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/figures/Fig_olfactory_perturbation_summary.png)

### Supplementary Video 1

使用 `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_left_long.mp4`。

[Supplementary Video 1：侧化行为对比，CS+ 左侧](/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_left_long.mp4)

### Supplementary Video 2

使用 `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_left_long.mp4`。

[Supplementary Video 2：嗅觉扰动，CS+ 左侧](/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_left_long.mp4)

### Supplementary Video 3

使用 `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_right_long.mp4`。

[Supplementary Video 3：嗅觉扰动，CS+ 右侧](/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_right_long.mp4)

## 讨论

本研究的核心贡献是提出可复现的结构-功能-行为桥接框架。传统连接组论文常停留在结构统计，纯 AI 模拟又容易缺乏生物约束。本项目把真实连接矩阵、神经递质侧化、记忆轴细胞类别和 embodied 行为轨迹放入同一套统计框架，提供了可被实验检验的机制假说。

最重要的发现不是某个单一 p 值，而是多个层级相互支持：结构侧化候选经过 signed propagation 后影响记忆轴，行为模型进一步预测左右蘑菇体操控会改变 CS+/CS- 冲突任务中的 approach margin。这个结论适合 Nature 子刊叙事，但目前必须谨慎表述为“仿真预测”和“待实验验证的机制模型”。

## 需要补充的真实实验

1. 行为实验：使用 `3-octanol` 与 `isoamyl acetate` 作为可交换 CS+/CS-，训练后进行左右平衡 T-maze 或虚拟现实测试。
2. 遗传操控：单侧或通路特异操控 APL、DPM、MBON03/09/12/13、PPL103。
3. 成像验证：记录左右蘑菇体、DAN、MBON 在 `cs_plus_weak_conflict` 条件下的活动。
4. 统计设计：每条件至少 `n >= 30`，主指标为 `mean_approach_margin` 和 `side_specific_margin_shift`，FDR 校正全部多重比较。

## 数据和代码可复现性

- 代码：`/unify/ydchen/unidit/bio_fly/src/bio_fly`
- 脚本：`/unify/ydchen/unidit/bio_fly/scripts`
- 测试：`/unify/ydchen/unidit/bio_fly/tests`
- 环境：`/unify/ydchen/unidit/bio_fly/env`
- 输出：`/unify/ydchen/unidit/bio_fly/outputs`
- 文档：`/unify/ydchen/unidit/bio_fly/docs`
- 论文草稿：`/unify/ydchen/unidit/bio_fly/paper`

验证命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python -m pytest -q
```

当前测试结果：`25 passed, 1 warning in 14.93s`。

## 新增结果：FlyWire v783 连接表直接支持侧化反馈模块

本节保存于 `/unify/ydchen/unidit/bio_fly/paper/NATURE_STYLE_DRAFT_CN.md` 的增补结果。新增分析不再只依赖论文 zip 的图文，而是直接读取 `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/proofread_connections_783.feather` 和 `/unify/ydchen/unidit/bio_fly/data/processed/flywire_neuron_annotations.parquet`。

新增连接组发现：

| pre_family | post_family | left | right | right_laterality_index | total_ipsilateral_syn_count |
| --- | --- | --- | --- | --- | --- |
| KC | KC | 2.032e+05 | 1.761e+05 | -0.07155 | 3.793e+05 |
| KC | MBON | 8.932e+04 | 8.921e+04 | -0.0006162 | 1.785e+05 |
| KC | APL | 6.056e+04 | 5.626e+04 | -0.03677 | 1.168e+05 |
| APL | KC | 5.349e+04 | 4.514e+04 | -0.08458 | 9.863e+04 |
| KC | DPM | 4.82e+04 | 3.982e+04 | -0.0952 | 8.803e+04 |
| KC | DAN | 4.094e+04 | 3.607e+04 | -0.0632 | 7.7e+04 |
| DAN | KC | 2.017e+04 | 1.725e+04 | -0.07816 | 3.742e+04 |
| MBON | MBON | 5127 | 4933 | -0.01928 | 1.006e+04 |
| DPM | KC | 5169 | 4109 | -0.1142 | 9278 |
| DAN | MBON | 3721 | 3995 | 0.03551 | 7716 |
| MBON | KC | 4329 | 2625 | -0.245 | 6954 |
| MBON | DAN | 2393 | 2747 | 0.06887 | 5140 |

这一结果为文章提供了更强的生物解释：蘑菇体左右侧化不是一侧整体更强，而是不同记忆子模块的侧化方向不同。`KC→KC`、`APL→KC`、`KC→DPM`、`DPM→KC` 偏左，提示左侧可能更偏向反馈抑制、递归稳定和记忆维持；`DAN→MBON` 与 `MBON→DAN` 轻度右偏，提示右侧可能更偏向调制输出或状态切换。

新增图可作为正文或扩展数据图：

![MB family transition heatmap](/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_mb_family_transition_heatmap.png)

![MB transition laterality](/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_mb_transition_laterality.png)

新增补充视频：

- [MB lateralization mechanism video](/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/videos/mb_lateralization_mechanism.mp4)
- [MB discovery behavior, CS+ left](/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior/videos/mb_discovery_behavior_cs_plus_left.mp4)
- [MB discovery behavior, CS+ right](/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior/videos/mb_discovery_behavior_cs_plus_right.mp4)

谨慎表述：当前新增结果支持“左侧反馈稳定 / 右侧调制输出”的可检验假说，但仍需真实单侧 APL/DPM/DAN/MBON 操控和 CS+/CS- 行为学实验证明因果性。

## 新增结果：Eon/CyberFly 多模态复现基准

为回应“连接组是否能自动涌现果蝇生物现象”的问题，我们把 Eon/CyberFly 公开说明拆解为四层：连接组/LIF 响应、sensory input、descending-neuron readout、NeuroMechFly/FlyGym 身体控制器。这样可以避免把低维控制器输出误写成纯连接组自动涌现。

新增脚本为 `/unify/ydchen/unidit/bio_fly/scripts/run_eon_multimodal_benchmark.py`，输出目录为 `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark`。本轮测试四种输入：

- 气味/食物记忆：ORN 输入，行为为 CS+ 食物气味趋近。
- 视觉：LC/LPLC visual projection 输入，行为为视觉目标跟踪或 looming readout。
- 味觉/feeding：gustatory 输入，当前为 feeding/proboscis-extension 连接组代理。
- 机械感觉/梳理：mechanosensory 输入，当前为前足梳理代理。

关键连接组 readout 文件：

- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_readout_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_connectome_multimodal_readout_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_top_target_classes.png`

视频材料：

- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_visual_object_tracking.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_front_leg_grooming_proxy.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_multimodal_reproduction_summary.mp4`

可写入论文的谨慎结论：本系统已经把结构连接组、感觉通道、descending readout 和 embodied proxy 统一到一个可复现基准中，能够比较气味、视觉、味觉和机械感觉输入是否进入不同下游 readout。它支持“连接组约束的多模态行为假说生成”，但还不是“完整行为自动涌现”的最终证明。

## 新增结果：食物气味记忆仿真

我们进一步把连接组侧化模型放入 embodied 行为仿真。由于当前 FlyGym 环境没有真实可摄取糖滴对象，本实验将食物实现为糖奖励相关气味源 `CS+`，并设置一个中性或竞争性气味源 `CS-`。虚拟果蝇在两个气味源之间运动，模型记录最终选择、食物 approach margin、镜像校正后的终点方向和轨迹长度。

新增脚本和输出：

- `/unify/ydchen/unidit/bio_fly/scripts/run_food_memory_suite.py`
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/food_memory.py`
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/food_memory_behavior_summary.csv`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`

仿真条件包括 balanced naive search、learned sugar memory、left KC-APL-DPM feedback、right DAN-MBON output 和 weak-sugar/strong-decoy conflict。当前小样本中二分类 food choice rate 饱和，因此论文主指标应使用连续轨迹变量。该实验的科学价值在于把“左侧反馈稳定 / 右侧输出调制”转化为真实行为学可检验预测：如果左侧 KC-APL-DPM 反馈模块参与食物记忆稳定，则在弱糖气味和强竞争气味冲突条件下，单侧操控应最明显地改变 food approach margin。

## 新增结果：descending-neuron 行为接口把多模态连接组响应落到身体控制层

为了更严谨地回答“连接组是否足以产生行为相关现象”，我们进一步分析了 sensory seed 传播后的 descending-neuron (`DN`) 读出。DN 是从脑部下行到腹神经索的神经元，是脑内感觉、记忆和决策计算进入走路、转向、逃逸、梳理、取食等身体动作的关键接口。这个分析保存于 `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout`，论文视频副本保存于 `/unify/ydchen/unidit/bio_fly/paper/video/dn_multimodal_mechanism_summary.mp4`。

核心结果如下：

| condition | recruited DN | DN abs mass | DN laterality index | top DN family | top-family fraction | interpretation |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| `olfactory_food_memory` | 58 | 0.011488 | +0.049 | `DNge` | 0.282 | 气味食物记忆较弱进入下行接口，更偏脑内记忆轴 |
| `visual_object_tracking` | 704 | 0.203957 | -0.098 | `DNg` | 0.299 | 视觉输入强烈进入转向/姿态/逃逸候选 DN |
| `gustatory_feeding` | 638 | 0.255412 | -0.103 | `DNge` | 0.514 | 味觉输入强烈进入头部、腿部和进食动作候选接口 |
| `mechanosensory_grooming` | 769 | 0.463450 | -0.033 | `DNg` | 0.510 | 接触/机械感觉最强进入梳理和运动程序候选接口 |

这一结果支持一个更适合 Nature 叙事的分层模型：蘑菇体左右侧化主要解释记忆检索和抗干扰稳定性；视觉、机械感觉和味觉则更直接招募 DN 家族，构成身体动作输出接口。换言之，我们不是声称“连接组单独自动涌现完整行为”，而是证明了 FlyWire 结构约束可以把不同感觉模态映射到不同下游行为接口，并产生可实验验证的 DN 家族预测。

建议写入论文主线的表述：

> Connectome propagation did not merely diffuse through generic central-brain targets. Instead, sensory modality determined the descending-neuron interface: mechanosensory and gustatory inputs strongly recruited DNg/DNge families, visual inputs recruited DNg/DNge/DNp pathways, whereas olfactory food-memory inputs had weak descending mass and a larger memory-axis component. This separation supports a layered model in which mushroom-body lateralization shapes memory-state computation, while modality-specific descending readouts provide the bridge to embodied behaviour.

谨慎边界：当前 DN 结果是基于 FlyWire v783 signed propagation 的功能预测。它可以指导真实实验选择 DN 靶点，但不能替代钙成像、电生理、遗传干预或真实行为学验证。
