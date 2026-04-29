# bio_fly 文档索引

保存路径：`/unify/ydchen/unidit/bio_fly/docs/INDEX_CN.md`

## 当前主线文档

- `/unify/ydchen/unidit/bio_fly/README.md`：项目总入口，适合第一次阅读。
- `/unify/ydchen/unidit/bio_fly/docs/TEACHER_BRIEFING_CN.md`：给非生物背景、AI 背景老师看的解释性总览。
- `/unify/ydchen/unidit/bio_fly/docs/PROJECT_IMPLEMENTATION_STATUS_CN.md`：当前工程完成度、模块状态、结果边界和下一步。
- `/unify/ydchen/unidit/bio_fly/docs/FULL_PROJECT_GUIDE.md`：项目目录、依赖、命令和二次开发指南。
- `/unify/ydchen/unidit/bio_fly/docs/DATA_DOWNLOAD_AND_MB_DISCOVERY_CN.md`：数据下载、FlyWire 接入和蘑菇体结构发现。
- `/unify/ydchen/unidit/bio_fly/docs/EON_MULTIMODAL_REPRODUCTION_CN.md`：Eon/CyberFly 多模态复现边界和公开替代方案。
- `/unify/ydchen/unidit/bio_fly/docs/DN_BEHAVIOR_READOUT_REPORT_CN.md`：descending-neuron 行为接口分析。
- `/unify/ydchen/unidit/bio_fly/docs/MB_DN_MOTOR_READOUT_CN.md`：本轮新增的 `MBON/DAN/APL/DPM -> DN -> motor primitive` 直接读出，解释四卡传播、DN family、motor primitive 和 Eon 边界。
- `/unify/ydchen/unidit/bio_fly/docs/OLFACTORY_PERTURBATION_MEMORY_CN.md`：嗅觉扰动和记忆行为实验。
- `/unify/ydchen/unidit/bio_fly/docs/LATERALIZATION_BEHAVIOR_SIMULATION_CN.md`：侧化行为仿真和剂量/镜像实验。
- `/unify/ydchen/unidit/bio_fly/docs/STRUCTURE_BEHAVIOR_LINKAGE_CN.md`：结构-功能-行为联动统计。
- `/unify/ydchen/unidit/bio_fly/docs/TARGET_PRIORITIZATION_CN.md`：可湿实验验证的 MBON/DAN/APL/DPM 靶点优先级。
- `/unify/ydchen/unidit/bio_fly/docs/MOTOR_AND_ODOR_BRIDGE_CN.md`：本轮新增的 OCT/MCH sensory encoder、calibrated motor interface 和行为桥接总结。
- `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_MIRROR_KINEMATICS_CN.md`：OCT/MCH 镜像摆放、早期转向动力学和 MB 扰动负结果正式报告。
- `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_ASSAY_VIDEO_RENDERING_CN.md`：OCT/MCH mirror-side 论文视频渲染说明，解释视频变量、轨迹尾迹、统计 inset、运行命令和严谨边界。
- `/unify/ydchen/unidit/bio_fly/docs/MEETING_FEEDBACK_EXPERIMENTS_CN.md`：2026-04-29 生物老师会议反馈后的定向实验报告，包含 5-HT/Glu 分拆、DPM 光遗传协议扫描、180 度旋转控制、GRASP 靶点和群体 T-maze 行为指标。
- `/unify/ydchen/unidit/bio_fly/docs/DPM_OPTOGENETIC_VALIDATION_CN.md`：DPM 光遗传仿真验证报告，包含 opsin/波长/频率/时长协议库、5-HT release pattern 预测、旋转控制、群体 T-maze 行为调节预测和湿实验推荐表。

## 如果只想看“我们到底做了什么仿真”

建议按这个顺序读：

1. `/unify/ydchen/unidit/bio_fly/README.md` 的“给第一次接触赛博果蝇的读者：我们到底做了什么仿真”。这里用表格解释每个仿真实验的输入、操作、输出、结论、局限和一键复现命令。
2. `/unify/ydchen/unidit/bio_fly/docs/DPM_OPTOGENETIC_VALIDATION_CN.md` 的“这个仿真实验到底怎么跑”和“湿实验怎么验证最严谨”。这里专门解释 DPM 光遗传、5-HT release pattern、180 度旋转控制和群体 T-maze 验证。
3. `/unify/ydchen/unidit/bio_fly/docs/TEACHER_BRIEFING_CN.md`。这里适合给非生物背景或 AI 背景老师快速理解项目主线。

最短复现路径：

```bash
cd /unify/ydchen/unidit/bio_fly
CUDA_VISIBLE_DEVICES=0,1 /unify/ydchen/unidit/bio_fly/env/bin/python \
  /unify/ydchen/unidit/bio_fly/scripts/run_dpm_optogenetic_validation.py \
  --devices cuda:0 cuda:1

CUDA_VISIBLE_DEVICES=0,1 /unify/ydchen/unidit/bio_fly/env/bin/python \
  /unify/ydchen/unidit/bio_fly/scripts/run_meeting_feedback_experiments.py \
  --devices cuda:0 cuda:1
```

这两条命令分别生成 `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429` 和 `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429`。它们回答的核心问题是：DPM 光遗传能否预测偏侧化 5-HT release pattern，以及 5-HT-right/Glu-left 两条侧化轴分别会怎样影响可观测 readout。

## 当前关键输出

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/OCT_MCH_SENSORY_ENCODER_CN.md`：OCT/MCH glomerulus-level sensory encoder 输出报告。
- `/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/CONNECTOME_MOTOR_BRIDGE_CN.md`：calibrated connectome motor bridge 报告。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/OCT_MCH_FORMAL_SUITE_CN.md`：OCT/MCH 多 seed pilot 行为套件报告。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/figures/Fig_oct_mch_formal_suite.png`：OCT/MCH pilot 行为图。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite_n50/OCT_MCH_FORMAL_SUITE_CN.md`：OCT/MCH `n=50` late/terminal 正式代理仿真报告。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_early_suite_n50/OCT_MCH_FORMAL_SUITE_CN.md`：OCT/MCH `n=50` early-decision 正式代理仿真报告。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/OCT_MCH_FORMAL_SUITE_CN.md`：OCT/MCH `n=50` mirror-side early-kinematics 正式代理仿真报告。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/figures/Fig_oct_mch_formal_suite.png`：镜像摆放后的 valence、早期转向和 physical laterality 汇总图。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_key_conditions.mp4`：OCT/MCH 核心条件左右 mirror-side 代表性轨迹视频。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_mb_perturbations.mp4`：MB 扰动条件左右 mirror-side 代表性轨迹视频。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_video_qc.json`：OCT/MCH 视频帧数、分辨率和非空检查结果。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/oct_mch_assay_v2_key_conditions.mp4`：本轮新增 v2 核心条件视频，不使用 FlyGym raw video 背景，直接由轨迹 CSV 重画培养皿、气味杯、糖/电击、轨迹尾迹和统计 inset。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/oct_mch_assay_v2_mb_perturbations.mp4`：本轮新增 v2 MB perturbation 视频。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/OCT_MCH_ASSAY_VIDEO_V2_CN.md`：v2 视频变量和 QC 报告。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/MB_DN_MOTOR_READOUT_CN.md`：MB-DN-motor 直接读出完整输出报告。
- `/unify/ydchen/unidit/bio_fly/paper/video/mb_dn_motor_readout_summary.mp4`：MB-DN-motor 机制视频论文副本。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/MEETING_FEEDBACK_EXPERIMENTS_CN.md`：会议反馈实验输出报告。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/double_dissociation_metrics.csv`：5-HT 右偏和 Glu 左偏按绝对效应量分拆后的 readout 表。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/dpm_gpu_propagation_summary.csv`：GPU0/1 DPM 光遗传传播结果。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/group_behavior_predictions.csv`：群体 T-maze choice index 预测。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/grasp_priority_targets.csv`：GRASP 结构验证靶点优先级。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/figures`：会议反馈新增四张图。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/DPM_OPTOGENETIC_VALIDATION_CN.md`：DPM 光遗传完整输出报告。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_optogenetic_protocol_library.csv`：光遗传协议库。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_5ht_release_pattern_summary.csv`：5-HT release pattern 摘要。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_optogenetic_behavior_predictions.csv`：DPM 光遗传行为调节预测。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_wetlab_protocol_recommendations.csv`：湿实验推荐协议。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/videos/dpm_optogenetic_release_prediction.mp4`：DPM release pattern 机制视频。

## 论文目录

- `/unify/ydchen/unidit/bio_fly/paper/NATURE_STYLE_DRAFT_CN.md`：中文 Nature 风格结果叙事草稿。
- `/unify/ydchen/unidit/bio_fly/paper/main_merged.tex`：LaTeX 主文稿。
- `/unify/ydchen/unidit/bio_fly/paper/figures`：论文图。
- `/unify/ydchen/unidit/bio_fly/paper/video`：论文补充视频。

## 归档文档

以下早期计划、旧运行报告或临时说明已移动到 `/unify/ydchen/unidit/bio_fly/docs/archive`，保留用于追溯，不再作为当前主线入口：

- `/unify/ydchen/unidit/bio_fly/docs/archive/ARTICLE_REVISION_AND_FUNCTIONAL_SIMULATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/archive/GIT_PAPER_BUILD_AND_CS_EXPLANATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/archive/NATURE_PAPER_UPGRADE_DRAFT.md`
- `/unify/ydchen/unidit/bio_fly/docs/archive/POST_RUN_REPORT_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/archive/RUN_FINDINGS_AND_IMPROVEMENTS_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/archive/behavior_experiment.md`
- `/unify/ydchen/unidit/bio_fly/docs/archive/reproduction_notes.md`
- `/unify/ydchen/unidit/bio_fly/docs/archive/research_plan.md`
- `/unify/ydchen/unidit/bio_fly/docs/archive/resource_estimate.md`

## 当前结论边界

可以严谨声称：

- 项目已接入 FlyWire 公开连接组、注释和 FlyGym/NeuroMechFly 风格行为代理。
- 项目已实现四卡连接组传播、蘑菇体侧化扰动、嗅觉记忆代理行为、多模态 DN readout、逆向拟合 motor interface、OCT/MCH 条件化实验表、OCT/MCH glomerulus-level sensory encoder 和 calibrated motor-to-behavior bridge。
- 本轮已新增四卡 `MBON/DAN/APL/DPM -> DN -> motor primitive` 直接读出，明确把缺失的 Eon DN-to-body 接口变成公开可审计的替代层。
- 本轮已新增 OCT/MCH `assay_video_v2`，解决旧视频过于像“果蝇 + 蓝黄标签”的问题。
- 本轮已新增会议反馈定向实验：Glu-left 当前是更强的广谱 memory-output 扰动，5-HT-right 更适合作为 DPM 光遗传和记忆巩固时间窗验证轴；GRASP 仍是结构证据硬红线。
- 本轮已新增 DPM 光遗传仿真验证：推荐优先测试 `CsChrimson 617 nm` 或 `ReaChR 627 nm` 红光协议；成像证明和行为证明分开做，避免“成像破坏果蝇导致无法继续行为”的实验瓶颈。
- 当前结果支持“蘑菇体左右结构侧化可能影响嗅觉记忆检索和行为偏置”的可检验假说。
- OCT/MCH mirror-side `n=50` 早期动力学套件稳定复现奖励趋近和惩罚回避，但 MB 侧化扰动相对 WT 的行为差异仍未通过 FDR；这是需要写入论文边界的正式负结果。

不能严谨声称：

- 已完全复刻 Eon 私有闭环系统。
- 已恢复 Eon 内部 DN-to-motor 权重。
- 连接组单独无接口、无训练、无参数校准地自动涌现完整果蝇行为。
- 当前代理视频等同于真实果蝇行为学显著性证据。
