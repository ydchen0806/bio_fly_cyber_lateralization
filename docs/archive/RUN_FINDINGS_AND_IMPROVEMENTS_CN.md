# 本次运行结果、发现和改进说明

路径：`/unify/ydchen/unidit/bio_fly/docs/RUN_FINDINGS_AND_IMPROVEMENTS_CN.md`

## 1. 本次检查的项目状态

项目根目录：`/unify/ydchen/unidit/bio_fly`

已存在的核心交付物：

- `/unify/ydchen/unidit/bio_fly/README.md`
- `/unify/ydchen/unidit/bio_fly/NATURE_LEVEL_EXPERIMENT_REPORT.md`
- `/unify/ydchen/unidit/bio_fly/docs/FULL_PROJECT_GUIDE.md`
- `/unify/ydchen/unidit/bio_fly/docs/NATURE_PAPER_UPGRADE_DRAFT.md`
- `/unify/ydchen/unidit/bio_fly/docs/LATERALIZATION_BEHAVIOR_SIMULATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/STRUCTURE_BEHAVIOR_LINKAGE_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/TARGET_PRIORITIZATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/OLFACTORY_PERTURBATION_MEMORY_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite`
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite`
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite`

## 2. 上一个主要命令运行多久

### 2.1 四卡功能传播套件

记录文件：`/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_run_info.json`

- 总耗时：`11.089` 秒。
- 扰动规格数：`534`。
- 传播步数：`3`。
- 每步保留最大活跃节点数：`5000`。
- GPU：`cuda:0, cuda:1, cuda:2, cuda:3`。
- worker 0：`cuda:0`，`134` 个规格，耗时 `8.537` 秒。
- worker 1：`cuda:1`，`134` 个规格，耗时 `8.657` 秒。
- worker 2：`cuda:2`，`133` 个规格，耗时 `8.218` 秒。
- worker 3：`cuda:3`，`133` 个规格，耗时 `8.704` 秒。

### 2.2 嗅觉记忆扰动套件

记录文件：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/suite_metadata.json`

该脚本未写入显式 elapsed 字段，因此用输出文件时间估算：

- 最早输出：`2026-04-26 12:09:56`。
- 最晚输出：`2026-04-26 12:21:51`。
- 估计耗时：`714.2` 秒，约 `11.9` 分钟。
- 渲染设备：`0, 1, 2, 3`。

## 3. 已得到的结果文件

### 3.1 四卡功能传播

- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_run_info.json`：运行参数、GPU 分配和耗时。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/gpu_worker_assignment.csv`：每个 worker 分配到哪张卡。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/gpu_worker_results.csv`：每张卡的执行结果。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_perturbation_manifest.csv`：所有真实扰动和随机对照扰动。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_signed_propagation_summary.csv`：每个扰动的传播摘要。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_signed_propagation_responses.parquet`：神经元级传播响应。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_response_metrics.csv`：记忆轴、MBON、DAN、APL、DPM 等指标。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv`：与随机对照比较后的经验 p 值和 FDR q 值。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_top_targets.csv`：候选靶点排序。
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/CYBER_FLY_NATURE_UPGRADE_REPORT.md`：自动报告。

### 3.2 侧化行为仿真

- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/conditions/lateralization_condition_table.csv`：侧化条件表。
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/dose_response/dose_response_summary.csv`：侧化剂量反应曲线。
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/figures/Fig_lateralization_dose_response.png`：剂量反应图。
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_left_long.mp4`：CS+ 左侧长视频。
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_right_long.mp4`：CS+ 右侧长视频。
- `/unify/ydchen/unidit/bio_fly/docs/LATERALIZATION_BEHAVIOR_SIMULATION_CN.md`：中文解释报告。

### 3.3 嗅觉记忆扰动

- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/conditions/olfactory_condition_table.csv`：气味和记忆条件表。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/screen_trials/memory_choice_summary.csv`：短程筛选试验结果。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/rendered_trials/memory_choice_summary.csv`：渲染试验结果。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/olfactory_behavior_summary.csv`：合并统计表。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/figures/Fig_olfactory_perturbation_summary.png`：嗅觉扰动总结图。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_left_long.mp4`：CS+ 左侧对比视频。
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_right_long.mp4`：CS+ 右侧对比视频。
- `/unify/ydchen/unidit/bio_fly/docs/OLFACTORY_PERTURBATION_MEMORY_CN.md`：中文报告。

## 4. 主要科学发现

### 4.1 功能传播发现

FDR 显著的指标集中在 DAN、APL、DPM、response laterality 和 max target score，说明候选侧化扰动影响的是记忆调控轴，而不只是全脑随机噪声。

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

变量解释：

- `actual_condition`：真实生物学假设对应的扰动条件。
- `metric`：统计指标。
- `actual_value`：真实扰动的观测值。
- `effect_z`：真实扰动相对随机对照的标准化效应大小。
- `empirical_p_two_sided`：双侧经验 p 值。
- `n_null`：随机对照数量。
- `fdr_q`：多重比较校正后的 q 值。

### 4.2 结构-功能-行为联动发现

`left_mb_glutamate_enriched` 在当前行为读出中有较强的 `mean_approach_margin`，且能连接到 `left_glutamate_kc_activate` 的功能传播指标。

| condition                   | functional_condition                            |   cs_plus_choice_rate |   mean_approach_margin |   mean_signed_final_y |   memory_axis_abs_mass |   response_laterality_abs |   min_empirical_fdr_q |
|:----------------------------|:------------------------------------------------|----------------------:|-----------------------:|----------------------:|-----------------------:|--------------------------:|----------------------:|
| mirror_reversal             | left_glutamate_activate_silence_right_serotonin |                   1   |                4.52957 |               6.01095 |                1.14915 |                 -0.830289 |           nan         |
| amplified_left_axis         | left_glutamate_kc_activate                      |                   0.5 |                2.19707 |               3.14793 |                1.14883 |                 -0.830021 |             0.0381634 |
| left_mb_glutamate_enriched  | left_glutamate_kc_activate                      |                   1   |                5.86938 |               8.2169  |                1.14883 |                 -0.830021 |             0.0381634 |
| bilateral_memory_blunted    | right_serotonin_activate_silence_left_glutamate |                   0.5 |                2.60023 |               3.35794 |                1.10769 |                  0.843098 |           nan         |
| amplified_right_axis        | right_serotonin_kc_activate                     |                   0.5 |                2.58335 |               3.45549 |                1.10754 |                  0.842948 |             0.0381634 |
| right_mb_serotonin_enriched | right_serotonin_kc_activate                     |                   1   |                3.311   |               4.72425 |                1.10754 |                  0.842948 |             0.0381634 |

变量解释：

- `mean_approach_margin`：接近 CS+ 相对 CS- 的优势，是比二分类选择率更连续、更适合统计的行为指标。
- `mean_signed_final_y`：最后位置的左右偏向。
- `memory_axis_abs_mass`：扰动传播到记忆轴的总响应。
- `response_laterality_abs`：功能响应左右不对称强度。
- `min_empirical_fdr_q`：该条件关联的最小 FDR q 值。

### 4.3 嗅觉记忆发现

本轮把“闻到了什么”明确成两个气味源：`CS+` 与 `CS-`。当前仿真可以测试：弱气味、高记忆、长期记忆衰退、强 CS- 冲突、单侧感觉剥夺、初始位置镜像等条件。

| condition                     |   n_trials |   cs_plus_choice_rate |   mean_approach_margin |   left_cs_plus_margin |   right_cs_plus_margin |   cs_plus_intensity |   cs_minus_intensity | memory_mode             | biological_interpretation                                          |
|:------------------------------|-----------:|----------------------:|-----------------------:|----------------------:|-----------------------:|--------------------:|---------------------:|:------------------------|:-------------------------------------------------------------------|
| acute_balanced_memory         |          6 |              0.833333 |                3.99337 |               2.61022 |                5.37651 |                1    |                 1    | acute                   | balanced acute odor-memory reference                               |
| cs_plus_weak_conflict         |          6 |              0.833333 |                3.78446 |               2.1729  |                5.39602 |                0.28 |                 1    | sensory_memory_conflict | weak CS+ cue competes with stronger CS- sensory plume              |
| initial_state_mirror          |          6 |              1        |                5.36599 |               5.41013 |                5.32185 |                1    |                 1    | initial_state_control   | same memory with biased initial position and heading               |
| left_sensor_deprivation       |          6 |              1        |                5.08019 |               4.81495 |                5.34543 |                1    |                 1    | sensory_asymmetry       | left olfactory channel deprivation with intact right channel       |
| long_term_memory_consolidated |          6 |              0.833333 |                3.96725 |               2.48649 |                5.44801 |                1    |                 1    | long_term               | stronger consolidated CS+ drive with reduced aversive interference |
| long_term_memory_decay        |          6 |              1        |                5.29904 |               5.76055 |                4.83753 |                1    |                 1    | long_term_decay         | forgetting or weak retrieval after memory decay                    |
| narrow_plume_high_gradient    |          4 |              1        |                4.51364 |               4.49051 |                4.53677 |                1    |                 1    | plume_geometry          | narrow steep plume emphasizes sensory input precision              |
| right_sensor_deprivation      |          6 |              0.833333 |                4.07821 |               2.41454 |                5.74189 |                1    |                 1    | sensory_asymmetry       | right olfactory channel deprivation with intact left channel       |
| weak_odor_high_memory         |          6 |              1        |                5.0327  |               4.81715 |                5.24825 |                0.35 |                 0.35 | weak_cue_retrieval      | long-term memory compensates for low odor concentration            |
| wide_plume_low_gradient       |          4 |              1        |                8.21895 |               8.33129 |                8.10662 |                1    |                 1    | plume_geometry          | broad shallow odor gradient tests navigational sensitivity         |

关键解释：

- `weak_odor_high_memory`：弱气味但记忆增益高，用于测试记忆是否能补偿低感觉输入。
- `cs_plus_weak_conflict`：CS+ 弱、CS- 强，用于测试即时感觉优势是否能击败记忆。
- `left_sensor_deprivation` / `right_sensor_deprivation`：单侧嗅觉通道剥夺，用于分离感觉侧化与记忆侧化。
- `initial_state_mirror`：改变初始位置和朝向，用于排除起点偏置。

## 5. 对论文 zip 的解释

zip 路径：`/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip`

已检查到 zip 包含：

- `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip::main_connectivity.tex`
- `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip::main_skeleton.tex`
- `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip::main_merged.tex`
- 多个 PDF/PNG 图，例如 `Fig3_hemisphere_asymmetry.pdf`、`Fig7_lobe_memory_schematic.pdf`、`Fig_ext7_volcano_all_NT.png`。

工程判断：该 zip 是文稿和图包，不是 root-id 级仿真数据包。因此当前能做的是把论文中的统计结论变成可检验假说，并用公开/外部连接矩阵进行功能传播与行为读出；如果要逐条复算论文结论，需要补充 root-id 级表格。

## 6. 本次做出的改进

- 更新 `/unify/ydchen/unidit/bio_fly/README.md`，把所有核心路径改为绝对路径。
- 在 `/unify/ydchen/unidit/bio_fly/README.md` 中补充面向非生物背景读者的变量解释。
- 新增 `/unify/ydchen/unidit/bio_fly/docs/RUN_FINDINGS_AND_IMPROVEMENTS_CN.md`，集中记录运行耗时、输出文件、发现和限制。
- 新增 `/unify/ydchen/unidit/bio_fly/paper/NATURE_STYLE_DRAFT_CN.md`，把结果按 Nature 子刊论文逻辑组织。
- 新增 `/unify/ydchen/unidit/bio_fly/paper/FIGURE_AND_VIDEO_INDEX_CN.md`，列出可放入正文和补充材料的图片、视频和表格。
- 保留严谨边界：当前结果是仿真支持的机制假说，不直接宣称已经完成真实生物证明。

## 7. 当前限制与下一步

### 7.1 限制

- `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip` 没有提供可直接仿真的 root-id 数据。
- 当前行为仿真是低维可解释模型，不是完整 spike-level closed-loop cyber fly。
- 选择率 `cs_plus_choice_rate` 在一些条件下饱和，因此应优先使用 `mean_approach_margin` 和 `side_specific_margin_shift`。

### 7.2 下一步

- 补充 root-id 级数据到 `/unify/ydchen/unidit/bio_fly/data/raw`。
- 对 `cs_plus_weak_conflict`、`left_sensor_deprivation`、`right_sensor_deprivation` 做更大重复数仿真。
- 把视频提高到统一 1080p、统一配色、统一标注比例尺和条件说明。
- 设计真实行为实验：CS+ 使用 `3-octanol` 或 `isoamyl acetate`，CS- 使用另一种气味，左右位置和气味身份完全平衡。
- 做 APL、DPM、MBON、DAN 的遗传操控或钙成像验证。
