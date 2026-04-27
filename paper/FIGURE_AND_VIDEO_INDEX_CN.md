# 图表和视频材料索引

保存路径：`/unify/ydchen/unidit/bio_fly/paper/FIGURE_AND_VIDEO_INDEX_CN.md`

## 正文图候选

### Figure 1：结构假说与仿真框架

- 候选来源：`/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip::figures/Fig1_mushroom_body_nt_system.png`
- 作用：给非生物背景读者解释蘑菇体、KC、MBON、DAN、APL、DPM 和左右侧化。
- 需要改进：重新绘制为统一配色，并标注 `CS+`、`CS-`、结构层、功能层、行为层和统计层。

### Figure 2：四卡 functional propagation 显著性

- 数据：`/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv`
- 作用：证明右侧 serotonin KC 与左侧 glutamate KC 不是随机扰动。
- 主变量：`effect_z`、`fdr_q`、`metric`、`actual_condition`。

### Figure 3：结构-功能-行为联动

- 图片：`/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/Fig_structure_behavior_linkage.png`
- 数据：`/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/functional_behavior_linkage.csv`
- 作用：展示结构侧化如何映射到记忆轴传播和行为轨迹。

### Figure 4：嗅觉 CS+/CS- 记忆扰动

- 图片：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/figures/Fig_olfactory_perturbation_summary.png`
- 数据：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/olfactory_behavior_summary.csv`
- 作用：明确展示果蝇闻到什么，以及记忆、感觉强度、单侧剥夺如何改变行为。

### Figure 5：靶点优先级

- 数据：`/unify/ydchen/unidit/bio_fly/outputs/target_prioritization/memory_axis_target_family_summary.csv`
- 作用：把仿真结果转成真实实验可操作对象。
- 重点候选：`DPM`、`APL`、`MBON03`、`MBON09`、`MBON12`、`MBON13`、`PPL103`。

## 补充视频候选

### Supplementary Video 1：侧化行为对比，CS+ 左侧

- 路径：`/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_left_long.mp4`
- 含义：展示不同左右记忆偏置条件下，果蝇面对左侧 CS+ 时的轨迹差异。

### Supplementary Video 2：侧化行为对比，CS+ 右侧

- 路径：`/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_right_long.mp4`
- 含义：镜像验证，排除单纯空间偏置。

### Supplementary Video 3：嗅觉扰动，CS+ 左侧

- 路径：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_left_long.mp4`
- 含义：展示弱气味、高记忆、长期记忆、单侧嗅觉剥夺等条件在 CS+ 左侧时的行为。

### Supplementary Video 4：嗅觉扰动，CS+ 右侧

- 路径：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_right_long.mp4`
- 含义：镜像验证，适合和 Supplementary Video 3 成对出现。

## 表格候选

### Supplementary Table 1：四卡运行参数

- 路径：`/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_run_info.json`

### Supplementary Table 2：经验显著性

- 路径：`/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv`

### Supplementary Table 3：嗅觉条件表

- 路径：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/conditions/olfactory_condition_table.csv`

### Supplementary Table 4：行为统计

- 路径：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/olfactory_behavior_summary.csv`

### Supplementary Table 5：实验靶点

- 路径：`/unify/ydchen/unidit/bio_fly/outputs/target_prioritization/memory_axis_target_family_summary.csv`

## 目前图片和视频还需要提升的地方

- 统一 1080p 或 4K 分辨率。
- 每个视频帧叠加条件名、CS+ 和 CS- 位置、时间戳和比例尺。
- 对所有主图使用同一套左右脑颜色：左侧蓝色、右侧红色、中性灰色。
- 增加误差条、置信区间和显著性标记。
- 把 `choice rate` 与 `approach margin` 同时展示，避免只展示容易饱和的指标。

## 新增 FlyWire v783 连接组图和视频

- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_mb_family_transition_heatmap.png`：MB 家族连接热图。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_mb_transition_laterality.png`：MB 家族连接左右偏侧化图。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_kc_upstream_nt_by_side.png`：KC 上游神经递质左右比较图。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_memory_axis_candidate_targets.png`：记忆轴候选靶点图。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/videos/mb_lateralization_mechanism.mp4`：MB 侧化机制说明视频。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior/videos/mb_discovery_behavior_cs_plus_left.mp4`：结构候选行为仿真，CS+ 左侧。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior/videos/mb_discovery_behavior_cs_plus_right.mp4`：结构候选行为仿真，CS+ 右侧。

## 新增食物气味记忆视频

- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`：糖奖励相关食物气味 CS+ 位于左侧时的五条件行为仿真拼接视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`：糖奖励相关食物气味 CS+ 位于右侧时的镜像仿真拼接视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_left.mp4`：同一视频的显式 assay-scene 文件名，含培养皿、糖滴、气味杯、滤纸片、羽流和比例尺。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_right.mp4`：同一视频的显式 assay-scene 文件名，含培养皿、糖滴、气味杯、滤纸片、羽流和比例尺。
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/FOOD_MEMORY_SIMULATION_CN.md`：食物气味记忆仿真实验解释。
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/food_memory_behavior_summary.csv`：食物气味记忆仿真统计表。

2026-04-27 更新：

- 上面两个 paper 默认视频已经替换为 assay-scene 版本，视频面板内叠加了培养皿/agar 背景、糖滴、气味杯、滤纸片、`CS+`/`CS-` 羽流和比例尺。
- 标注含义：`CS+` 是训练时和糖奖励/食物意义配对的气味，`CS-` 是中性或竞争诱饵气味。
- 复现脚本：`/unify/ydchen/unidit/bio_fly/scripts/make_food_memory_assay_scene_videos.py`。
- 严谨边界：这些实验场景物体是 post-render scene overlay，用于论文/汇报可读性；FlyGym 原始仿真输入是 OdorArena 气味源，不是可摄取糖滴力学对象。

## 新增 OCT/MCH mirror-side 论文视频

- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_key_conditions.mp4`：核心 OCT/MCH 条件视频，包含 `OCT sucrose WT`、`MCH sucrose WT counterbalance`、`OCT shock WT` 和 `Weak OCT / strong MCH conflict`，每个条件左右 mirror-side 成对展示。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_mb_perturbations.mp4`：MB perturbation 视频，包含 WT、left MB gain 0.25、right MB gain 0.25、left/right averaged 和 left/right swapped。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_cs_plus_left.mp4`：8 个条件在 `CS+` 左侧时的代表性轨迹。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_cs_plus_right.mp4`：8 个条件在 `CS+` 右侧时的代表性轨迹。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_full_both_sides.mp4`：8 个条件、左右两种摆放的全量 16-panel 视频。

配套材料：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_assay_scene_video_manifest.json`：视频生成 manifest。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_video_qc.json`：视频帧数、分辨率、首帧非空检查和缩略图路径的论文目录副本。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_oct_mch_mirror_assay_video_frame.png`：带轨迹尾迹的代表性中帧，适合作为视频缩略图或补充图入口。
- `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_ASSAY_VIDEO_RENDERING_CN.md`：完整变量解释和复现命令。

建议论文用法：

- Supplementary Video：优先使用 `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_key_conditions.mp4`，展示奖励趋近、惩罚回避、气味身份 counterbalance 和弱 OCT/强 MCH 冲突。
- Supplementary Video：使用 `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_mb_perturbations.mp4`，透明展示 MB perturbation 相对 WT 未通过 FDR 的负结果。
- Figure thumbnail：可以在图注中引用 `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_oct_mch_mirror_assay_video_frame.png` 作为视频缩略图。

严谨边界：

- 每个视频 panel 是单条代表性渲染 trial；统计 inset 来自 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50` 的正式 `n=100` mirror-side 结果。
- 培养皿、糖滴、电极、气味杯、滤纸和羽流是 post-render scene overlay，用于论文读者理解实验结构。
- 这些视频不用于声称“连接组单独自动涌现完整果蝇行为”；它们用于展示公开替代闭环和正式统计结果对应的代表性轨迹。

## 新增 OCT/MCH assay video v2

- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_key_conditions.mp4`：v2 核心条件视频，不使用 FlyGym raw video 背景，直接由 trajectory CSV 重画实验场景。画面包含培养皿、OCT/MCH 气味杯、滤纸、气味羽流、糖滴、电击栅格、果蝇身体朝向、轨迹尾迹和正式 `n=100` 统计 inset。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_mb_perturbations.mp4`：v2 MB perturbation 视频，展示 WT、left MB gain 0.25、right MB gain 0.25、left/right averaged 和 left/right swapped。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_oct_mch_assay_v2_key_conditions_frame.png`：v2 代表性中帧缩略图。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/OCT_MCH_ASSAY_VIDEO_V2_CN.md`：v2 视频报告。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/oct_mch_assay_v2_qc.json`：v2 QC，key conditions 为 `600` 帧、`20.0 s`、`1920x1080`；MB perturbations 为 `750` 帧、`25.0 s`、`1920x1080`。

建议论文用法：

- Supplementary Video：优先用 `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_key_conditions.mp4` 替代旧版 key conditions 视频。
- Supplementary Video：用 `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_mb_perturbations.mp4` 展示 MB perturbation 负结果。
- Figure thumbnail：用 `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_oct_mch_assay_v2_key_conditions_frame.png`。

严谨边界：v2 是数据驱动的实验场景动画，但仍然是代表性 trajectory visualization；统计证据来自 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50`。

## 新增 MB-DN-motor 直接读出图和视频

- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_family_heatmap.png`：MBON/DAN/APL/DPM 与 OCT/MCH KC context seed 招募 DN family 的热图。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_motor_primitive_heatmap.png`：DN family 映射到 motor primitive 的热图。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_laterality_index.png`：MB-to-DN readout 的左右偏侧指数。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_motor_mechanism.png`：机制示意图。
- `/unify/ydchen/unidit/bio_fly/paper/video/mb_dn_motor_readout_summary.mp4`：机制视频，展示 `MB seed -> FlyWire propagation -> DN family -> motor primitive`。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/mb_dn_condition_summary.csv`：条件级数值表。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/mb_dn_motor_primitives.csv`：motor primitive 数值表。
- `/unify/ydchen/unidit/bio_fly/docs/MB_DN_MOTOR_READOUT_CN.md`：中文解释文档。

建议论文用法：

- 正文或扩展数据图：`Fig_mb_dn_laterality_index.png` 可支持“右侧 MBON/memory-axis 有更明显右偏 DN 读出”的机制假说。
- 方法学图：`Fig_mb_dn_motor_mechanism.png` 用于说明我们没有恢复 Eon 私有 DN-to-body 权重，而是实现公开替代接口。
- Supplementary Video：`mb_dn_motor_readout_summary.mp4` 作为 interface-layer 机制动画。

严谨边界：这个模块支持“公开连接组中 MB 输出到 DN 层存在可检测读出”的假说；不能写成已经证明完整行为涌现。

## 新增 Eon/CyberFly 多模态复现视频

- `/unify/ydchen/unidit/bio_fly/paper/video/eon_visual_object_tracking.mp4`：视觉目标跟踪复现/代理视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_front_leg_grooming_proxy.mp4`：机械感觉触发前足梳理代理视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_multimodal_reproduction_summary.mp4`：食物气味记忆、视觉目标跟踪、机械感觉梳理的四宫格总览视频。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_connectome_multimodal_readout_heatmap.png`：嗅觉、视觉、味觉、机械感觉到 readout family 的连接组传播热图。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_top_target_classes.png`：多模态传播 top target 类别图。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_readout_summary.csv`：多模态连接组 readout 数值表。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/EON_MULTIMODAL_REPRODUCTION_CN.md`：Eon/CyberFly 复现边界和结果报告。

## 新增 DN 行为接口图和视频

- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_family_readout_heatmap.png`：四种感觉条件招募 `DNg`、`DNge`、`DNp`、`DNpe` 等 descending-neuron 家族的热图。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_laterality_index.png`：DN 响应左右偏侧指数，定义为 `(right-left)/(right+left)`。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_side_mass_stacked.png`：每个感觉条件的左右 DN 绝对响应量占比。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig16_dn_family_readout_heatmap.png`：主稿 LaTeX 使用的 DN 家族热图副本。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig17_dn_laterality_index.png`：主稿 LaTeX 使用的 DN 偏侧图副本。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig18_dn_side_mass_stacked.png`：主稿 LaTeX 使用的 DN 左右堆叠图副本。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/videos/dn_multimodal_mechanism_summary.mp4`：1280x720 机制动画，展示 sensory input、FlyWire graph、DN family 和 behaviour proxy 的分层关系。
- `/unify/ydchen/unidit/bio_fly/paper/video/dn_multimodal_mechanism_summary.mp4`：论文补充视频副本。
- `/unify/ydchen/unidit/bio_fly/docs/DN_BEHAVIOR_READOUT_REPORT_CN.md`：中文报告，解释所有 DN 变量和主要生物学含义。
