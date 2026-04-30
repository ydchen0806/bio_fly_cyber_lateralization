# bio_fly：赛博果蝇连接组-功能-行为仿真项目

本项目目录是 `/unify/ydchen/unidit/bio_fly`。目标是把论文 zip 中的 FlyWire 结构组学发现，转成可复现、可统计、可渲染视频的功能仿真证据链，用于研究果蝇左右脑蘑菇体不对称性与嗅觉记忆行为之间的关系。

## 给第一次接触赛博果蝇的读者：我们到底做了什么仿真

这里的“赛博果蝇”不是指已经完整复制了 Eon Systems 的私有闭环系统，也不是指“只把连接组丢进去就自动长出完整果蝇行为”。本项目当前实现的是一个**公开可审计的替代仿真脑流程**：

`FlyWire 真实连接组/神经递质注释 -> 指定神经元或脑区作为输入 seed -> GPU signed propagation 计算扰动如何沿连接图传播 -> 把传播结果聚合到 KC/MBON/DAN/APL/DPM/DN 等功能脑区 -> 用透明的行为读出模型生成 OCT/MCH 选择率、轨迹和视频 -> 提出湿实验可验证的预测`

这套流程的价值在于：它把“左脑和右脑蘑菇体的结构差异”转成了可以反复运行、可以做随机对照、可以画图、可以给湿实验老师执行的预测。它的边界也很明确：当前行为层是代理读出，不等于真实果蝇完整运动系统；DPM 光遗传结果是预测，不是已经在真实果蝇上测到的实验事实。

### 本项目已经实际完成的仿真实验

| 实验 | 输入是什么 | 我们怎么操作 | 输出文件 | 当前能说明什么 | 当前不能说明什么 | 一键复现 |
| --- | --- | --- | --- | --- | --- | --- |
| 论文 zip 结构发现整理 | `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip` 和 FlyWire 注释 | 解压、整理 figure/table 线索，把“右侧 5-HT、左侧 Glu、alpha'beta' 区最强”转成结构摘要 | `/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/nt_structural_summary.csv` | KC 输入递质侧化是当前最稳的结构主线 | zip 本身不是 root-id 级原始连接组，结构硬证据仍需 GRASP/split-GFP | 见 `/unify/ydchen/unidit/bio_fly/docs/DATA_DOWNLOAD_AND_MB_DISCOVERY_CN.md` |
| 四卡连接组传播 | FlyWire v783/v630 连接表、KC/MB 递质侧化 seed | 在 `cuda:0-3` 上做 signed multi-hop propagation，并用随机 KC seed 做经验显著性对照 | `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv` | 右侧 5-HT KC seed 和左侧 Glu KC seed 的影响能传播到 memory axis、DAN、APL、DPM、MBON/MBIN 和左右读出 | 传播不是生物化学动力学，也不是全脑 spiking 闭环 | `cd /unify/ydchen/unidit/bio_fly && /unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_four_card_experiment_suite.py --devices cuda:0 cuda:1 cuda:2 cuda:3 --steps 3 --max-active 5000 --n-random-per-family 128 --output-dir /unify/ydchen/unidit/bio_fly/outputs/four_card_suite` |
| OCT/MCH 嗅觉记忆代理 | OCT、MCH 两种气味，CS+/CS- 奖励或惩罚条件，mirror-side 左右摆放 | 生成 T-maze/培养皿风格轨迹，平衡 CS+ 左右位置，统计 expected choice rate、approach margin、early lateral velocity | `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_condition_summary.csv` 和 `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_key_conditions.mp4` | 代理系统能稳定表达“奖励趋近、惩罚回避、弱 CS+/强 CS- 冲突”的方向，且不是简单左右摆放偏差 | MB 侧化扰动相对 WT 的行为差异目前未通过 FDR，不能写成已经证明真实行为因果 | `cd /unify/ydchen/unidit/bio_fly && /unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50 --n-trials 50 --run-time 0.2 --max-workers 4 --mirror-sides` |
| 会议反馈分拆验证 | 生物老师提出的 5-HT/Glu 分拆、DPM 光遗传、180 度旋转、群体 T-maze 和 GRASP 验证需求 | 分别移除或减弱 5-HT-right、Glu-left、both-blunted，扫描 DPM 光遗传传播和群体可观测指标 | `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/MEETING_FEEDBACK_EXPERIMENTS_CN.md` | Glu-left 是更强广谱 memory-output 扰动；5-HT-right 更适合做 DPM/5-HT release 和记忆巩固时间窗验证轴 | 不能用计算分拆替代真实遗传或成像验证 | `cd /unify/ydchen/unidit/bio_fly && CUDA_VISIBLE_DEVICES=0,1 /unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_meeting_feedback_experiments.py --devices cuda:0 cuda:1` |
| DPM 光遗传仿真验证 | DPM neuron seed、CsChrimson/ReaChR/ChR2 光遗传参数、FlyWire 下游 ROI、OCT/MCH 行为代理 | 用 `cuda:0,1` 传播 DPM 激活，扫描波长/频率/脉宽/时长/光强，预测 5-HT release pattern、旋转控制和群体行为 delta | `/unify/ydchen/unidit/bio_fly/docs/DPM_OPTOGENETIC_VALIDATION_CN.md` 和 `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429` | 推荐 617/627 nm 红光 DPM 协议；预测偏侧化果蝇按脑侧注册的 release LI 保持右偏；群体 T-maze 最敏感条件是 weak OCT/strong MCH conflict | 不能声称真实 5-HT 已释放或真实行为已改变；必须用湿实验验证 | `cd /unify/ydchen/unidit/bio_fly && CUDA_VISIBLE_DEVICES=0,1 /unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_dpm_optogenetic_validation.py --devices cuda:0 cuda:1` |

### 这些输出怎么读

- `absolute_mass`：扰动沿连接组传播后的总响应量。它像“影响范围/强度”的粗粒度指标，不是钙信号，也不是真实神经递质浓度。
- `laterality_index` 或 `LI`：左右差异指数，常用形式是 `(right - left) / (right + left)`。正值表示右侧更强，负值表示左侧更强。
- `choice_index`：群体行为选择指数。正值通常表示更偏向预期方向，例如更接近奖励 CS+ 或更远离惩罚 CS+。
- `CS+`：训练时与糖奖励、安全或正性结果配对的气味。
- `CS-`：训练时不奖励、竞争或负性结果配对的气味。
- `OCT`：3-octanol，果蝇经典嗅觉条件化气味之一。
- `MCH`：4-methylcyclohexanol，另一种经典嗅觉条件化气味。
- `DPM`：dorsal paired medial neuron，与蘑菇体记忆维持和 5-HT 调节相关。
- `wetlab_priority_score`：按仿真效应强度、文献可行性、光遗传参数可操作性和对照清晰度综合排序的实验优先级，不是生物学显著性 p 值。

### 目前最清楚的结论

1. 结构层面最稳的发现是：KC 输入存在稳定递质侧化，核心是右侧 5-HT/serotonin 偏强、左侧 Glu/glutamate 偏强，并且在 alpha'beta' 记忆巩固相关亚区最突出。
2. 这个发现不是纯描述，因为四卡传播显示这些 seed 的影响能投射到 memory axis、DAN、APL、DPM、MBON/MBIN 和左右读出。
3. 会议反馈后的分拆实验提示：Glu-left 更像广谱 memory-output 扰动轴，5-HT-right 更适合作为 DPM 光遗传、5-HT release pattern 和记忆时间窗的验证轴。
4. OCT/MCH 代理行为和视频已经可以作为“可复现行为框架”和“湿实验设计草图”，但还不是证明真实果蝇行为因果的最终证据。
5. DPM 光遗传仿真给出可直接讨论的湿实验方案：优先用 CsChrimson 617 nm 或 ReaChR 627 nm，做 40 Hz、20 ms、5 s、0.1 mW/mm2 左右的红光协议，主读出为按脑侧注册的 5-HT sensor dF/F、AUC、release LI，以及独立群体 T-maze 的 choice index。

### 为了严谨，必须怎样用湿实验验证

本项目建议把真实验证拆成三条互补链，而不是要求同一只果蝇既做破坏性成像又做行为：

1. **结构硬证据：GRASP/split-GFP 或等价结构验证。** 目标是确认右侧 DPM/5-HT 到右侧 alpha'beta' KC、左侧 Glu 输入到左侧 alpha'beta' KC 的连接或接触差异是否在群体中稳定存在。这个实验回答“结构侧化是不是某只 FlyWire 果蝇的偶然现象”。
2. **功能成像证据：DPM 光遗传 release pattern。** 用 DPM-driver 表达 CsChrimson/ReaChR，用 KC 或 MB compartment 表达 5-HT sensor 或 GCaMP；同一只果蝇做原始方向和水平旋转 180 度，分析时按脑侧而不是相机坐标注册。若真实偏侧化存在，brain-registered LI 应保持；若是成像角度伪影，image-coordinate LI 会随旋转翻转。
3. **行为群体证据：OCT/MCH T-maze 或轨迹记录。** 另取独立群体，不要求测每只果蝇 NT 侧化；在训练、巩固或测试窗口给 DPM 红光刺激，优先测试 weak OCT/strong MCH conflict 和 delayed memory window。主指标是 choice index、approach margin、early turning bias，并做 CS+/CS- side mirror、OCT/MCH counterbalance、no-opsin、retinal-minus、red-light-only 对照。

三条链合在一起才是强论证：结构证据说明侧化真实存在，功能成像说明侧化能被 DPM 光遗传读出，群体行为说明这个轴能调节记忆选择。当前仿真已经完成的是“提出并量化这些预测”，真实湿实验还没有被本项目替代。

## 一句话结论

当前版本已经完成从“结构发现”到“功能传播”再到“行为视频”的闭环原型：

1. 论文 zip `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip` 主要是文稿和图包，不是 root-id 级可直接仿真的原始连接组数据包。
2. 用户原始 paper 的主发现已经明确整理为“KC 输入递质侧化”：右侧血清素 Ser/5-HT 富集，左侧谷氨酸 Glu/GLU 偏置，最强在 $\alpha'\beta'$ 记忆巩固相关亚区。结构汇总见 `/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/nt_structural_summary.csv`。
3. 项目已接入 `/unify/ydchen/unidit/bio_fly/external/Drosophila_brain_model` 与 FlyWire v783/v630 连接矩阵，可运行 signed propagation 与 Brian2 smoke test。
4. 四卡 GPU 功能传播正式套件已在 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite` 生成结果，`534` 个扰动规格、`3` hop、每步最多 `5000` 个活跃节点，总耗时约 `11.089` 秒。
5. 递质侧化 seed 仿真支持功能可传播性：右侧血清素 KC seed 和左侧谷氨酸 KC seed 相比同侧随机 KC 对照，显著改变 memory axis、DAN、APL、DPM、MBON/MBIN 与左右读出，显著性表见 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv`。
6. 最新嗅觉记忆仿真套件在 `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite` 生成，渲染流程总耗时约 `11.9` 分钟，其中包含屏幕筛选、四卡渲染、统计图和两个长视频。
7. OCT/MCH mirror-side 早期动力学正式套件已在 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50` 生成结果：8 个条件、每条件 nominal `50` + mirror `50` 条轨迹、总计 `800` 条短时程试验。
8. OCT/MCH mirror-side 论文视频已在 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos` 和 `/unify/ydchen/unidit/bio_fly/paper/video` 生成，包含培养皿场景、OCT/MCH 气味杯、糖奖励/电击标注、轨迹尾迹和正式 `n=100` 统计 inset。
9. 快速回归测试请在 `/unify/ydchen/unidit/bio_fly` 下运行 `/unify/ydchen/unidit/bio_fly/env/bin/python -m pytest -q`；最近一次完整测试结果见本文末尾。

## 最新交付物入口

面向非生物/AI 背景老师的统一中文汇报文档已整理到：

- `/unify/ydchen/unidit/bio_fly/docs/TEACHER_BRIEFING_CN.md`

已新增并编译出面向老师的递质侧化汇报材料：

- `/unify/ydchen/unidit/bio_fly/ppt/cyber_fly_teacher_report.tex`：中文 Beamer PPT 源码，已把“血清素右偏、谷氨酸左偏”作为主线，并在开头解释所有关键名词。
- `/unify/ydchen/unidit/bio_fly/ppt/cyber_fly_teacher_report.pdf`：编译后的 34 页 PPT。
- `/unify/ydchen/unidit/bio_fly/paper/main_merged.tex`：英文主文，新增 reader guide、递质侧化 seed 的四卡传播结果和方法说明。
- `/unify/ydchen/unidit/bio_fly/paper/main_merged.pdf`：编译后的 42 页英文 paper PDF。
- `/unify/ydchen/unidit/bio_fly/paper/neurotransmitter_lateralization_teacher_cn.tex`：中文 paper 解读稿源码。
- `/unify/ydchen/unidit/bio_fly/paper/neurotransmitter_lateralization_teacher_cn.pdf`：编译后的 6 页中文 paper 解读 PDF，专门解释神经递质、侧化、统计量、仿真加强和严谨边界。

根据生物老师会议反馈新增“分拆验证 + DPM 光遗传 + 群体 T-maze”实验：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/meeting_feedback_experiments.py`：新增会议反馈定向实验模块，包含 5-HT/Glu 绝对效应分拆、DPM 光遗传协议扫描、180 度旋转成像控制、群体 T-maze 可观测指标和 GRASP 靶点优先级。
- `/unify/ydchen/unidit/bio_fly/scripts/run_meeting_feedback_experiments.py`：一键运行脚本。本轮使用 `CUDA_VISIBLE_DEVICES=0,1`，并在脚本参数中指定 `--devices cuda:0 cuda:1`，避免占用其它 GPU。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback/MEETING_FEEDBACK_EXPERIMENTS_CN.md`：完整中文实验报告，解释会议反馈如何转成计算实验和湿实验建议。
- `/unify/ydchen/unidit/bio_fly/docs/MEETING_FEEDBACK_EXPERIMENTS_CN.md`：报告副本，便于在 docs 中统一查阅。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/double_dissociation_metrics.csv`：5-HT 右偏和 Glu 左偏按 `abs(z)` 分拆的 readout 表。当前更严谨结论是：Glu-left 是更强广谱 memory-output 扰动，5-HT-right 更适合进入 DPM 光遗传和记忆巩固时间窗验证。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/dpm_gpu_propagation_summary.csv`：DPM 光遗传 GPU 传播结果。left DPM readout LI 为 `-0.833`，right DPM readout LI 为 `+0.807`。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/group_behavior_predictions.csv`：群体 T-maze 可观测指标预测。WT OCT/MCH choice index 约 `0.72`，移除 5-HT-right 轴预测降至 `0.595`，移除 Glu-left 轴预测降至 `0.566`，双轴减弱预测降至 `0.36`。
- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/grasp_priority_targets.csv`：GRASP 结构验证靶点。优先验证 right DPM/5-HT input -> right `KCa'b'`，并用 left Glu input -> left `KCa'b'` 作为相反方向 positive control。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_meeting_double_dissociation_heatmap.png`、`/unify/ydchen/unidit/bio_fly/paper/figures/Fig_dpm_optogenetic_protocol_predictions.png`、`/unify/ydchen/unidit/bio_fly/paper/figures/Fig_group_behavior_observable_predictions.png`、`/unify/ydchen/unidit/bio_fly/paper/figures/Fig_validation_logic_after_meeting.png`：新增 paper/PPT 共用图。

进一步新增“DPM 光遗传仿真验证”完整套件，专门回答“怎样用仿真指导湿实验验证 5-HT 侧化和行为调节”：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/dpm_optogenetic_validation.py`：DPM 光遗传验证模块，包含 opsin/波长/频率/脉宽/时长/光强协议库、GPU0/1 DPM signed propagation、5-HT release timecourse、下游 ROI readout、群体行为调节预测和湿实验推荐表。
- `/unify/ydchen/unidit/bio_fly/scripts/run_dpm_optogenetic_validation.py`：一键运行脚本。推荐命令：`CUDA_VISIBLE_DEVICES=0,1 /unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_dpm_optogenetic_validation.py --devices cuda:0 cuda:1`。
- `/unify/ydchen/unidit/bio_fly/docs/DPM_OPTOGENETIC_VALIDATION_CN.md`：完整中文报告，明确把验证拆成两条链：成像证明 release pattern，群体 T-maze 证明行为可调节；两者不要求在同一只果蝇上完成。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_optogenetic_protocol_library.csv`：光遗传协议库，覆盖 `ChR2_blue`、`ReaChR_red`、`CsChrimson_red`，波长 `470/530/590/617/627/660 nm`，频率 `1-40 Hz`，脉宽 `5-50 ms`，时长 `0.5-30 s` 和光强 `0.05-1.0 mW/mm2`。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_5ht_release_pattern_summary.csv`：5-HT release pattern 预测。最高优先级协议包括 `CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW` 和 `ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW`，预测 peak brain-registered release LI 约 `0.802`。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_optogenetic_behavior_predictions.csv`：DPM 光遗传群体行为预测。最敏感条件是 `weak_oct_strong_mch_conflict`，预测 DPM 红光刺激使 choice-index delta 约 `+0.104`；普通 reward 条件约 `+0.078`，shock 条件约 `-0.065`。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_wetlab_protocol_recommendations.csv`：可直接给湿实验老师讨论的实验推荐表，包含遗传设计、光刺激参数、主读出、关键对照和预期结果。
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/videos/dpm_optogenetic_release_prediction.mp4` 和 `/unify/ydchen/unidit/bio_fly/paper/video/dpm_optogenetic_release_prediction.mp4`：DPM 光遗传 release pattern 机制视频。
- 关键严谨边界：这套仿真不声称已经测到真实 5-HT 释放；它提供的是基于 FlyWire DPM propagation、opsin action spectrum 先验和 OCT/MCH 行为代理的可检验预测。结构硬证据仍需 GRASP/split-GFP 或等价湿实验验证。

本轮重新生成的 paper 级视频入口：

- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`：新版 assay-scene 视频，CS+ 食物/糖奖励气味在左侧，CS- 诱饵气味在右侧。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`：新版 assay-scene 视频，CS+ 食物/糖奖励气味在右侧，CS- 诱饵气味在左侧。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_left.mp4`：同上，保留显式 assay-scene 文件名。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_right.mp4`：同上，保留显式 assay-scene 文件名。
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_visual_object_tracking.mp4`：视觉目标跟踪复现/代理视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_front_leg_grooming_proxy.mp4`：机械感觉触发前足梳理代理视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_multimodal_reproduction_summary.mp4`：嗅觉食物记忆、视觉、梳理的四宫格总览视频。

新增 OCT/MCH mirror-side 论文视频：

- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_key_conditions.mp4`：OCT 奖励、MCH counterbalance、OCT 电击和弱 OCT/强 MCH 冲突四个核心条件，左右 mirror-side 成对展示。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_mb_perturbations.mp4`：WT、left MB gain 0.25、right MB gain 0.25、left/right averaged 和 left/right swapped 的 MB 扰动对比视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_cs_plus_left.mp4`：8 个条件在 `CS+` 左侧时的代表性轨迹。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_cs_plus_right.mp4`：8 个条件在 `CS+` 右侧时的代表性轨迹。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_full_both_sides.mp4`：8 个条件、左右两种摆放的全量 16-panel 视频。

本轮新增两个更严格实现：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/oct_mch_assay_v2.py`：新的 `assay_video_v2`。它不再把蓝黄 CS+/CS- 标签叠加在旧 FlyGym raw video 上，而是直接从 trajectory CSV 重画 1920x1080 实验场景：培养皿、滤纸、OCT/MCH 气味杯、半透明气味羽流、糖滴、电击栅格、果蝇身体朝向、轨迹尾迹和正式 `n=100` 统计 inset。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_key_conditions.mp4`：v2 核心条件视频，20 秒，600 帧，1920x1080，QC 通过。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_mb_perturbations.mp4`：v2 MB 扰动视频，25 秒，750 帧，1920x1080，QC 通过。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_oct_mch_assay_v2_key_conditions_frame.png`：v2 视频代表性中帧，可直接放入论文或补充材料索引。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/OCT_MCH_ASSAY_VIDEO_V2_CN.md`：v2 视频报告，解释所有变量、生成命令、QC 和严谨边界。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/mb_dn_motor_readout.py`：新的公开 `MBON/DAN/APL/DPM -> DN -> motor primitive` 直接读出。它从 FlyWire 蘑菇体注释表选择 `MBON`、`DAN`、`APL`、`DPM`，按左/右/双侧 seed 通过 FlyWire v783 signed propagation 传播到 `descending neurons`，再用透明 DN-family heuristic 映射到低维 motor primitive。
- `/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/MB_DN_MOTOR_READOUT_CN.md`：直接读出报告，说明变量、四卡运行、主要发现和不能过度声称的边界。
- `/unify/ydchen/unidit/bio_fly/paper/video/mb_dn_motor_readout_summary.mp4`：MB-DN-motor 机制视频，1600x900，1080 帧。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_family_heatmap.png`、`/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_motor_primitive_heatmap.png`、`/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_laterality_index.png`、`/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_motor_mechanism.png`：MB-DN 读出的 paper 图副本。

本轮四卡 MB-DN sweep 实际运行信息：

- 命令：`/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_mb_dn_motor_readout.py --devices cuda:0 cuda:1 cuda:2 cuda:3 --steps 3 --max-active 5000 --output-dir /unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout`
- 本地设备：4 张 `NVIDIA H20Z`，每张约 `139.7 GiB` 显存。
- 条件数：`18`，包括左/右/双侧 `MBON`、`DAN`、`APL_DPM_feedback`、`memory_axis`，以及 OCT/MCH KC odor-context。
- 耗时：`31.81` 秒。
- 主要可写结论：`left_MBON_to_DN` 的 DN 绝对响应最大，`dn_abs_mass=0.064815`，招募 `202` 个 DN，top family 为 `DNa`；`right_MBON_to_DN` 和 `right_memory_axis_to_DN` 的 DN laterality index 明显右偏，分别约 `+0.307` 和 `+0.420`。这支持“MB 输出到下行运动出口存在可检测的侧化读出”的假说。
- 不能写成：已经恢复 Eon 私有 DN-to-body 权重，或已经证明连接组单独自动涌现完整行为。

对应说明文档：

- `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_ASSAY_VIDEO_RENDERING_CN.md`：解释视频每个变量、轨迹尾迹、统计 inset、运行命令、输出路径和严谨边界。
- `/unify/ydchen/unidit/bio_fly/docs/MB_DN_MOTOR_READOUT_CN.md`：解释 MBON/DAN/APL/DPM 到 descending-neuron 再到 motor primitive 的直接读出。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_video_qc.json`：记录每个视频的帧数、分辨率、首帧像素方差和缩略图路径。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_oct_mch_mirror_assay_video_frame.png`：带轨迹尾迹和统计 inset 的代表性中帧，可用作视频缩略图。

这些视频中的单条轨迹来自 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview`，只用于代表性展示；右下角统计 inset 来自 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50` 的 `n=100` 正式 mirror-side 统计。

本轮重要代码改动：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/video.py`：论文视频拼接增加 assay-scene 场景层，包括培养皿/agar 背景、糖滴、气味杯、滤纸、CS+/CS- 羽流和比例尺，解决“觅食视频里看不到食物/气味目标”的问题。
- `/unify/ydchen/unidit/bio_fly/scripts/make_food_memory_assay_scene_videos.py`：从已有 FlyGym rendered trials 重新生成 assay-scene 论文视频，不需要重跑 MuJoCo。
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/video.py`：新增 OCT/MCH 专用 `make_oct_mch_assay_scene_video`，支持 `OCT`/`MCH` 气味身份、`US=sucrose/shock`、mirror-side 标签、trajectory tail 和正式统计 inset。
- `/unify/ydchen/unidit/bio_fly/scripts/make_oct_mch_assay_scene_videos.py`：从 OCT/MCH render preview 与 `n=100` 正式统计表生成 5 个 paper 视频并复制到 `/unify/ydchen/unidit/bio_fly/paper/video`。
- `/unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py`：CLI 增加 `--camera-fps`、`--camera-play-speed`、`--camera-width` 和 `--camera-height`，便于控制渲染视频规格。

本轮重新运行命令和耗时：

- Eon/CyberFly 多模态复现：约 `1 分 34 秒`，输出到 `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark`。
- 食物气味记忆套件：约 `5 分 15 秒`，输出到 `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite` 并覆盖 paper 视频。

严谨边界：

- 本项目已经下载并使用 FlyWire v783 公开连接组、突触表、连接表、neuropil 计数和注释，总量约 `10.6 GB`。
- 公开数据可以支持真实连接组传播和结构-功能统计。
- Eon 内部完整 DN-to-motor 权重、训练权重和所有闭环参数没有公开，因此不能把当前视频写成“连接组单独自动涌现完整果蝇行为”。
- 当前视频中培养皿、糖滴、气味杯、滤纸和 `CS+`/`CS-` 羽流是论文可读性的 post-render scene overlay；真实仿真输入仍是 FlyGym OdorArena 的两个气味源，不是可摄取糖滴力学对象。

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

- 渲染流程总耗时约 `11.9` 分钟。
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

- `/unify/ydchen/unidit/bio_fly`：`20G`
- `/unify/ydchen/unidit/bio_fly/outputs`：`359M`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite`：`110M`
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite`：`60M`
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite`：`83M`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50`：`1.1M`
- `/unify/ydchen/unidit/bio_fly/env`：`9.0G`
- `/unify/ydchen/unidit/bio_fly/external`：`421M`
- `/unify/ydchen/unidit/bio_fly/data`：`9.9G`

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
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_mb_dn_motor_readout.py --devices cuda:0 cuda:1 cuda:2 cuda:3 --steps 3 --max-active 5000 --output-dir /unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/make_oct_mch_assay_v2_videos.py --fps 30 --seconds-per-condition 5 --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2 --paper-video-dir /unify/ydchen/unidit/bio_fly/paper/video
```

最近一次完整测试结果：

```text
40 passed, 43 warnings in 7.05s
```

warnings 主要来自小样本 t 检验、seaborn/pandas 未来行为提示和数值精度提示，不影响本轮新增 v2 视频和 MB-DN-motor 测试通过。

## 论文与报告入口

- `/unify/ydchen/unidit/bio_fly/paper/NATURE_STYLE_DRAFT_CN.md`：面向 Nature 子刊的中文论文草稿。
- `/unify/ydchen/unidit/bio_fly/paper/FIGURE_AND_VIDEO_INDEX_CN.md`：图和视频材料索引。
- `/unify/ydchen/unidit/bio_fly/docs/PROJECT_IMPLEMENTATION_STATUS_CN.md`：本次整理的完整发现、改进和下一步计划。
- `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_MIRROR_KINEMATICS_CN.md`：OCT/MCH mirror-side 早期动力学正式报告。
- `/unify/ydchen/unidit/bio_fly/docs/MB_DN_MOTOR_READOUT_CN.md`：MBON/DAN/APL/DPM 到 DN 再到 motor primitive 的直接读出报告。
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

## Git、论文编译与 CS+/CS- 解释

本地 git 作者信息已配置：

```bash
cd /unify/ydchen/unidit/bio_fly
git config user.name
git config user.email
git remote -v
```

当前值：

- `user.name`：`ydchen0806`
- `user.email`：`yindachen@mail.ustc.edu.cn`
- `origin`：`https://github.com/ydchen0806/bio_fly_cyber_lateralization.git`

安全边界：不要把 GitHub token 写入 `/unify/ydchen/unidit/bio_fly/.git/config`、README、脚本或 shell 历史。推送时建议使用 GitHub CLI、临时环境变量或交互式 credential helper。

CS+/CS- 在本项目中的含义：

- `CS+`：conditioned stimulus positive，即训练时和糖/食物奖励绑定的气味。在仿真视频里，橙色标记代表“学会了会预测食物的气味线索”，不是一个可吃掉的实体食物模型。
- `CS-`：conditioned stimulus negative，即中性或竞争气味。在仿真视频里，蓝色标记代表不预测糖奖励的对照气味或诱饵气味。
- 视频是记忆测试阶段，而不是训练阶段。真实训练阶段可以有糖、电击或其他强化物；测试阶段通常只呈现气味，看果蝇是否靠近预测奖励的气味。因此当前渲染没有实体食物是合理的，但新版视频已在画面上方明确标注 `CS+ learned food/sugar cue` 和 `CS- neutral/decoy odour`。

论文编译器已在本地配置。编译命令：

```bash
cd /unify/ydchen/unidit/bio_fly/paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main_merged.tex
```

主要论文文件：

- `/unify/ydchen/unidit/bio_fly/paper/main_merged.tex`：英文 Nature 风格主稿。
- `/unify/ydchen/unidit/bio_fly/paper/main_merged.pdf`：已编译 PDF。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`：带食物线索标注的 CS+ 左侧补充视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`：带食物线索标注的 CS+ 右侧补充视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_left.mp4`：培养皿/糖滴/气味杯场景版 CS+ 左侧补充视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_assay_scene_cs_plus_right.mp4`：培养皿/糖滴/气味杯场景版 CS+ 右侧补充视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_key_conditions.mp4`：OCT/MCH v2 核心条件补充视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_mb_perturbations.mp4`：OCT/MCH v2 MB perturbation 补充视频。
- `/unify/ydchen/unidit/bio_fly/paper/video/mb_dn_motor_readout_summary.mp4`：MB-DN-motor 机制补充视频。

## Eon/CyberFly 多模态复现基准

Eon/CyberFly 原文和公开说明不能被简化成“只输入连接组，完整果蝇行为自动涌现”。更严谨的分解是：

1. FlyWire/Shiu 全脑 LIF 或 signed propagation 产生感觉扰动后的神经响应。
2. 视觉、嗅觉、机械感觉、味觉输入通过特定 sensory neuron seed 进入连接组。
3. descending neuron 或少数运动相关神经元作为身体接口 readout。
4. NeuroMechFly/FlyGym 的身体和低维控制器把 readout 转成 walking、steering、feeding 或 grooming 的代理行为。

本项目新增 `/unify/ydchen/unidit/bio_fly/scripts/run_eon_multimodal_benchmark.py`，按这个分层框架复现，而不是把低维控制器生成的视频夸大成完整自动涌现。

复现命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_eon_multimodal_benchmark.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark \
  --render-device 0 \
  --propagation-device cuda:0
```

新增输出：

- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_readout_summary.csv`：气味、视觉、味觉、机械感觉到下游 readout 的连接组传播摘要。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_connectome_multimodal_readout_heatmap.png`：多模态 readout 热图。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_top_target_classes.png`：每种 sensory input 的 top target 类别。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/food_memory/food_memory_behavior_summary.csv`：食物/气味记忆行为摘要。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/videos/eon_visual_object_tracking.mp4`：视觉目标跟踪代理视频。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/videos/eon_mechanosensory_front_leg_grooming_proxy.mp4`：机械感觉诱发前足梳理代理视频。
- `/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/videos/eon_multimodal_reproduction_summary.mp4`：四行为总览视频。
- `/unify/ydchen/unidit/bio_fly/docs/EON_MULTIMODAL_REPRODUCTION_CN.md`：中文严谨报告，说明复现层级、结果和限制。

当前多模态 readout 结果：

- `olfactory_food_memory`：主要传播到 visual_projection 与 memory_axis，memory-axis absolute mass 为 `0.245349`，descending absolute mass 为 `0.011488`。
- `visual_object_tracking`：descending absolute mass 为 `0.203957`，说明视觉输入比气味更强地进入 descending readout；视频层因当前 FlyGym `VisualTaxis` camera binding 问题采用可解释 proxy fallback。
- `gustatory_feeding`：gustatory absolute mass 为 `0.225318`，descending absolute mass 为 `0.255412`，适合作为 feeding/proboscis-extension 的连接组 readout 候选，但尚未实现完整口器动力学。
- `mechanosensory_grooming`：descending absolute mass 为 `0.463450`，mechanosensory absolute mass 为 `0.146880`，并生成前足梳理代理视频。

严谨边界：

- 已复现：公开连接组层、sensory seed 到 readout 的多模态传播、FlyGym 食物/气味行为、视觉和梳理代理视频、定量指标和报告。
- 未完全复现：Eon 内部完整 DN-to-motor 参数、所有行为的真实 motor program、视觉 looming 到 escape 的闭环身体反应、feeding 的 proboscis mechanics。
- 论文中应写“connectome-constrained multimodal behavioural proxies”，不要写“连接组单独自动涌现完整果蝇行为”。

## 食物气味记忆功能仿真与文章修改

本轮已把 `/unify/ydchen/unidit/bio_fly/Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip` 解压到 `/unify/ydchen/unidit/bio_fly/paper`，并修改主文 `/unify/ydchen/unidit/bio_fly/paper/main_merged.tex`。新增内容把原文“KC 输入 NT 侧化”扩展为“左侧 KC-APL-DPM 反馈稳定 / 右侧 DAN-MBON 输出调制”的功能环路模型。

新增食物气味记忆仿真：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/food_memory.py`
- `/unify/ydchen/unidit/bio_fly/scripts/run_food_memory_suite.py`
- `/unify/ydchen/unidit/bio_fly/scripts/make_food_memory_assay_scene_videos.py`
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/FOOD_MEMORY_SIMULATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/food_memory_behavior_summary.csv`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`

这里的“食物”被实现为糖奖励相关气味源 `CS+`，竞争气味为 `CS-`。FlyGym 当前环境没有真实可摄取糖滴对象，因此该实验是食物气味记忆仿真，不应在论文中写成真实进食行为。主指标建议使用 `mean_food_approach_margin`、`mean_signed_final_y` 和 `mean_path_length`，因为 `food_choice_rate` 在当前小样本中容易饱和。

视频表现层更新：新版 paper 视频使用 assay-scene 后处理，把 FlyGym 原始小球 marker 画成培养皿中的糖滴、气味杯、滤纸片、羽流和比例尺。该层只用于让老师/审稿人看懂“食物气味在哪里”，不改变仿真控制输入。

复现命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_food_memory_suite.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/food_memory_suite \
  --paper-video-dir /unify/ydchen/unidit/bio_fly/paper/video \
  --n-trials 1 --run-time 0.9 --render-device 0

/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/make_food_memory_assay_scene_videos.py \
  --summary /unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/rendered_trials/memory_choice_summary.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/videos \
  --paper-video-dir /unify/ydchen/unidit/bio_fly/paper/video \
  --replace-paper-defaults
```

详细说明见 `/unify/ydchen/unidit/bio_fly/docs/ARTICLE_REVISION_AND_FUNCTIONAL_SIMULATION_CN.md`。

## Descending-neuron 行为接口分析

为了更接近 Eon/CyberFly 中“连接组响应如何进入身体控制”的核心问题，本项目新增 DN 行为接口分析：

- 脚本：`/unify/ydchen/unidit/bio_fly/scripts/run_dn_behavior_readout_analysis.py`
- 模块：`/unify/ydchen/unidit/bio_fly/src/bio_fly/dn_readout_analysis.py`
- 输出目录：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout`
- 中文报告：`/unify/ydchen/unidit/bio_fly/docs/DN_BEHAVIOR_READOUT_REPORT_CN.md`

复现命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_dn_behavior_readout_analysis.py \
  --multimodal-dir /unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout \
  --top-n 80
```

这里的 `DN` 是 descending neuron，即从脑部下行到腹神经索、把脑内感觉/记忆计算传给身体运动系统的神经元。这个层级非常关键：如果只看到脑内神经元响应，不能说明行为会发生；如果能看到合理的 DN 家族被招募，就能形成“连接组约束的行为接口”证据。

新增 DN 输出：

- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_behavior_readout_summary.csv`：每个感觉条件的 DN 总响应、左右偏侧指数和最高 DN 家族。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_family_readout_summary.csv`：`DNg`、`DNge`、`DNp`、`DNpe` 等 DN 家族的响应量。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_side_laterality_summary.csv`：左右 DN 响应量。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_top_targets_by_condition.csv`：每个条件 top DN 明细。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_family_readout_heatmap.png`：DN 家族热图。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_laterality_index.png`：DN 左右偏侧指数。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_side_mass_stacked.png`：DN 左右响应量堆叠图。
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/videos/dn_multimodal_mechanism_summary.mp4`：高清机制动画。
- `/unify/ydchen/unidit/bio_fly/paper/video/dn_multimodal_mechanism_summary.mp4`：论文视频副本。

本轮 DN 结果：

- `olfactory_food_memory`：招募 `58` 个 DN，DN absolute mass 为 `0.011488`，远低于视觉、味觉和机械感觉；最高家族为 `DNge`，占 DN 绝对响应量 `0.282`。这支持“气味食物记忆主要先经过蘑菇体/脑内记忆轴，再较弱地进入下行接口”的解释。
- `visual_object_tracking`：招募 `704` 个 DN，DN absolute mass 为 `0.203957`；最高家族为 `DNg`，占比 `0.299`，其次 `DNge` 与 `DNp`。这符合视觉目标/looming 输入更直接影响转向、姿态或逃逸候选 DN 的预期。
- `gustatory_feeding`：招募 `638` 个 DN，DN absolute mass 为 `0.255412`；最高家族为 `DNge`，占比 `0.514`，提示味觉/进食相关输入强烈进入头部、腿部和动作触发接口，但当前尚未实现完整口器动力学。
- `mechanosensory_grooming`：招募 `769` 个 DN，DN absolute mass 为 `0.463450`；最高家族为 `DNg`，占比 `0.510`，是四个条件中最强的下行读出，符合接触/灰尘触发梳理或运动程序的连接组预期。

变量解释：

- `dn_abs_mass`：所有 DN 响应分数绝对值之和，表示该感觉输入进入下行运动接口的总强度。
- `dn_signed_mass`：DN 响应分数带符号求和，正负号来自 excitatory/inhibitory 加权传播；它表示净激活方向，但不能直接等同于真实膜电位。
- `laterality_index_right_minus_left`：`(right_dn_abs_mass - left_dn_abs_mass) / (right_dn_abs_mass + left_dn_abs_mass)`。正值表示右侧 DN 响应更强，负值表示左侧 DN 响应更强。
- `top_dn_family_abs_fraction`：最高 DN 家族占该条件全部 DN 绝对响应量的比例。
- `DNg`、`DNge`、`DNp`、`DNpe`：DN 命名家族，不是单个神经元。它们是候选行为接口集合，需要后续用单细胞干预或真实行为数据校准。

严谨结论：当前已经复现了“感觉输入经 FlyWire 连接组传播并汇聚到不同 DN 行为接口”的关键中间层；这比只生成行为视频更接近可发表机制。但它仍然不是完整证明“连接组单独自动涌现所有果蝇行为”。论文中应将其表述为 `connectome-constrained descending-neuron readout and embodied behavioural proxies`。

## 逆向拟合 DN-to-motor 替代接口层

为了进一步接近 Eon/CyberFly 的闭环问题，本项目新增了一个可运行的“逆向拟合接口层”。它的目标是回答：在拿不到 Eon 私有 DN-to-motor 权重的情况下，能否用公开连接组 readout 特征拟合一个透明、可审计、可替换的 motor interface。

新增文件：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/inverse_motor_fit.py`：逆向拟合核心模块。
- `/unify/ydchen/unidit/bio_fly/scripts/run_inverse_motor_fit.py`：命令行入口。
- `/unify/ydchen/unidit/bio_fly/tests/test_inverse_motor_fit.py`：回归测试。
- `/unify/ydchen/unidit/bio_fly/docs/PROJECT_IMPLEMENTATION_STATUS_CN.md`：九项任务整理和本轮实现状态。

复现命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_inverse_motor_fit.py \
  --connectome-summary /unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_readout_summary.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit
```

新增输出：

- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_training_table.csv`：训练表，把 connectome readout 特征和行为 motif 标签合并。
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_interface_coefficients.csv`：岭回归得到的 readout-to-motor 系数。
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_interface_predictions.csv`：训练集预测与残差。
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_interface_leave_one_out_cv.csv`：留一法交叉验证误差。
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/figures/Fig_inverse_motor_interface.png`：预测散点图和主要系数图。
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/INVERSE_MOTOR_INTERFACE_CN.md`：中文可行性报告。
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/suite_metadata.json`：本轮运行元数据。

输入变量解释：

- `descending_abs_mass`：感觉扰动经连接组传播到 descending neuron 的总绝对响应量，表示脑到身体接口被招募的强度。
- `descending_signed_mass`：descending neuron 响应的带符号总和，表示净兴奋/抑制方向。
- `memory_axis_abs_mass`：KC、MBON、DAN、APL、DPM 等蘑菇体记忆轴的总响应量。
- `memory_axis_signed_mass`：记忆轴带符号响应。
- `visual_projection_abs_mass` / `visual_projection_signed_mass`：视觉投射通路响应。
- `gustatory_abs_mass` / `gustatory_signed_mass`：味觉/糖接触通路响应。
- `mechanosensory_abs_mass` / `mechanosensory_signed_mass`：机械感觉/接触通路响应。

输出变量解释：

- `forward_drive`：前进或趋近驱动，越高表示越倾向持续行走。
- `turning_drive`：转向驱动，越高表示越需要方向修正或侧向选择。
- `feeding_drive`：进食或口器伸展代理驱动。
- `grooming_drive`：梳理动作驱动。
- `visual_steering_drive`：视觉目标跟踪或视觉诱导转向驱动。

本轮逆向拟合结果：

- 训练条件数为 `4`：`olfactory_food_memory`、`visual_object_tracking`、`gustatory_feeding`、`mechanosensory_grooming`。
- 训练集平均绝对误差较小：`forward_drive` 约 `0.0031`，`turning_drive` 约 `0.0064`，`feeding_drive` 约 `0.0091`，`grooming_drive` 约 `0.0066`，`visual_steering_drive` 约 `0.0100`。
- 留一法误差明显更大：`forward_drive` 约 `0.2199`，`turning_drive` 约 `0.4090`，`feeding_drive` 约 `0.6449`，`grooming_drive` 约 `0.4113`，`visual_steering_drive` 约 `0.6500`。

这个结果的解释是：逆向拟合接口层技术上可以实现，训练集能把四种 sensory readout 映射到不同 motor motif；但当前样本数只有四个，默认标签来自可解释行为 motif，而不是真实果蝇逐帧行为标注，所以它还不能作为最终功能显著性证据。Nature 级写法应是：`connectome-readout-constrained surrogate motor interface`。不能写成“恢复了 Eon 真实 DN-to-motor 权重”。

完整整理文档见：

- `/unify/ydchen/unidit/bio_fly/docs/PROJECT_IMPLEMENTATION_STATUS_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/INVERSE_MOTOR_INTERFACE_CN.md`

## 从仿真轨迹校准 motor interface

为避免逆向拟合接口层只依赖手工 motif 标签，本项目新增从已有仿真输出生成 motor calibration table 的流程。它读取食物气味轨迹、视觉目标跟踪轨迹、梳理代理时间序列和 gustatory connectome readout，生成可被 `run_inverse_motor_fit.py` 使用的目标表。

新增文件：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/motor_calibration.py`
- `/unify/ydchen/unidit/bio_fly/scripts/build_motor_calibration.py`
- `/unify/ydchen/unidit/bio_fly/tests/test_motor_calibration.py`

复现命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/build_motor_calibration.py \
  --eon-output-dir /unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/motor_calibration
```

新增输出：

- `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv`：从仿真和代理指标生成的 motor target 表。
- `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/MOTOR_CALIBRATION_FROM_SIMULATION_CN.md`：中文报告。
- `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/inverse_motor_interface_coefficients.csv`：校准标签版本的接口系数。
- `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/inverse_motor_interface_leave_one_out_cv.csv`：校准标签版本的留一法误差。
- `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/figures/Fig_inverse_motor_interface.png`：校准标签版本拟合图。

当前 motor calibration 结果：

| condition | forward_drive | turning_drive | feeding_drive | grooming_drive | visual_steering_drive | evidence_level |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `olfactory_food_memory` | 0.743884 | 0.603642 | 0.944602 | 0.030000 | 0.050000 | `embodied_trajectory_proxy` |
| `visual_object_tracking` | 0.688239 | 0.012953 | 0.020000 | 0.030000 | 0.000000 | `visual_proxy_trajectory` |
| `gustatory_feeding` | 0.120000 | 0.080000 | 0.803024 | 0.138312 | 0.020000 | `connectome_proxy_only` |
| `mechanosensory_grooming` | 0.080000 | 0.180000 | 0.030000 | 0.827428 | 0.020000 | `embodied_motor_proxy` |

解释：

- `olfactory_food_memory` 的标签来自 FlyGym 食物气味轨迹，已经比纯手工标签更接近行为数据。
- `visual_object_tracking` 当前目标距离在代理轨迹中变大，因此 `visual_steering_drive` 被量化为 `0.0`。这是失败模式，不应在论文中隐藏；后续需要修复 FlyGym 原生视觉接口或替换为更可靠的 visual taxis rollout。
- `gustatory_feeding` 仍是 `connectome_proxy_only`，因为当前没有完整 proboscis mechanics。
- `mechanosensory_grooming` 来自前足梳理代理时间序列。

## OCT/MCH 经典嗅觉条件化计划

为了让“闻到了什么”更符合果蝇记忆实验标准，本项目新增 OCT/MCH 条件化实验表。这里 `OCT` 表示 `3-octanol`，`MCH` 表示 `4-methylcyclohexanol`，二者是经典果蝇嗅觉条件化实验中常用的气味对。

新增文件：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/oct_mch_conditioning.py`
- `/unify/ydchen/unidit/bio_fly/scripts/write_oct_mch_conditioning_plan.py`
- `/unify/ydchen/unidit/bio_fly/tests/test_oct_mch_conditioning.py`

复现命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/write_oct_mch_conditioning_plan.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning
```

输出：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/oct_mch_condition_table.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/oct_mch_condition_table.yaml`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/OCT_MCH_CONDITIONING_PLAN_CN.md`

该条件表已经包含：

- `OCT` 奖励条件：`OCT_3-octanol` 作为 `CS+`，`MCH_4-methylcyclohexanol` 作为 `CS-`，`US=sucrose_reward`。
- `MCH` 反平衡条件：交换 `CS+` 和 `CS-`，排除气味身份本身造成的偏差。
- 电击惩罚条件：`US=electric_shock`，预期行为从趋近 `CS+` 变成回避 `CS+`。
- 左侧 MB 抑制、右侧 MB 抑制、左右 MB 平均化、左右 MB 互换。
- 弱 OCT / 强 MCH 感觉冲突条件，用于测试记忆能否覆盖即时气味强度。

下一步需要把 `cs_plus_odor` 和 `cs_minus_odor` 从标签升级成具体 ORN/PN/KC sensory encoder 输入。当前行为层可以放置两个气味源，但还没有区分 OCT 与 MCH 的受体通道差异。

## OCT/MCH sensory encoder 与 connectome-motor 行为桥接

本轮已经把上一节的“下一步”落成代码和输出。新增两个闭环：

1. `OCT/MCH sensory encoder`：把 `OCT_3-octanol` 与 `MCH_4-methylcyclohexanol` 映射到候选 antennal-lobe glomeruli，再从 FlyWire 注释表自动选择 ORN/ALPN root ids，并用 FlyWire signed propagation 得到 KC readout。
2. `connectome-motor bridge`：把 `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv` 中的 calibrated motor targets 转成现有 FlyGym 记忆行为仿真的 `MemoryCondition` 参数，并运行轻量 OCT/MCH screen。

新增文件：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/odor_sensory_encoder.py`
- `/unify/ydchen/unidit/bio_fly/scripts/build_oct_mch_sensory_encoder.py`
- `/unify/ydchen/unidit/bio_fly/tests/test_odor_sensory_encoder.py`
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/connectome_motor_bridge.py`
- `/unify/ydchen/unidit/bio_fly/scripts/build_connectome_motor_bridge.py`
- `/unify/ydchen/unidit/bio_fly/tests/test_connectome_motor_bridge.py`
- `/unify/ydchen/unidit/bio_fly/docs/MOTOR_AND_ODOR_BRIDGE_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/INDEX_CN.md`

复现 OCT/MCH sensory encoder：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/build_oct_mch_sensory_encoder.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder \
  --device cuda:0 \
  --steps 2 \
  --max-active 5000
```

核心输出：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_glomerulus_map.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_seed_neurons.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_kc_readout.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_encoder_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/OCT_MCH_SENSORY_ENCODER_CN.md`

当前 encoder 摘要：

| odor_identity | n_configured_glomeruli | n_orn_seeds | n_pn_seeds | n_kc_readout | kc_abs_mass | kc_laterality_index |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `MCH_4-methylcyclohexanol` | 3 | 158 | 10 | 2203 | 0.526523 | -0.115850 |
| `OCT_3-octanol` | 9 | 426 | 44 | 2757 | 0.461211 | -0.062238 |

复现 connectome-motor bridge 和轻量 screen：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/build_connectome_motor_bridge.py \
  --motor-target-table /unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge \
  --run-screen \
  --n-trials 1 \
  --run-time 0.2 \
  --render-device 0
```

核心输出：

- `/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/CONNECTOME_MOTOR_BRIDGE_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/screen_trials/oct_mch_calibrated_screen_summary.csv`

轻量 screen 结论：

- `oct_sucrose_appetitive_wt` 选择 `CS+`，approach margin 为 `0.539841`。
- `oct_shock_aversive_wt` 选择 `CS-`，approach margin 为 `-0.677602`，符合惩罚记忆方向。
- `weak_oct_strong_mch_conflict` 选择 `CS+`，approach margin 为 `0.607921`，符合“记忆可部分覆盖弱 CS+ 感觉强度”的代理预测。
- `mch_sucrose_appetitive_wt_counterbalanced` 和 `oct_sucrose_right_mb_silenced` 在当前 0.2 s screen 中选择 `CS-`，不能直接作为负结论，需要更长仿真和更多 seeds。

严谨边界：

- OCT/MCH encoder 是 `literature_constrained_glomerular_encoder`，不是实测气味响应矩阵。
- connectome-motor bridge 的 `attractive_gain`、`aversive_gain` 和 `lateral_memory_bias` 是公开替代接口推导出的行为参数，不是 Eon 私有 DN-to-motor 权重。
- 当前 screen 每条件只有 1 次、0.2 秒，只是 sanity check；正式统计至少需要每条件 50 个 seeds，最好四卡并行。

## OCT/MCH 多 seed 行为套件

本轮进一步新增 OCT/MCH 多 seed 行为套件，把单 seed sanity check 升级为可统计的 pilot 流程。该套件默认不渲染视频，删除逐步轨迹，只保留 trial 汇总、条件汇总、WT 对照比较、图和报告，便于扩展到每条件 50-300 seeds。

新增文件：

- `/unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py`
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/connectome_motor_bridge.py` 中的 `run_oct_mch_formal_suite`

本轮 pilot 命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite \
  --n-trials 4 \
  --run-time 0.35 \
  --max-workers 4
```

输出：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/oct_mch_formal_trials.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/oct_mch_formal_condition_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/oct_mch_formal_wt_comparisons.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/figures/Fig_oct_mch_formal_suite.png`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/OCT_MCH_FORMAL_SUITE_CN.md`

pilot 结果，每条件 `n=4`：

| condition | expected_choice_rate | mean_approach_margin | interpretation |
| --- | ---: | ---: | --- |
| `mch_sucrose_appetitive_wt_counterbalanced` | 1.0 | 1.121587 | MCH 作为 CS+ 时趋近 CS+ |
| `oct_sucrose_appetitive_wt` | 1.0 | 0.962411 | OCT 作为 CS+ 时趋近 CS+ |
| `oct_shock_aversive_wt` | 1.0 | -0.673866 | 电击条件回避 CS+，方向正确 |
| `weak_oct_strong_mch_conflict` | 1.0 | 0.672881 | 弱 OCT / 强 MCH 冲突中仍趋近 CS+，提示记忆项可覆盖部分感觉强度差 |

正式论文主图建议命令：

```bash
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite_n50 \
  --n-trials 50 \
  --run-time 0.8 \
  --max-workers 4
```

当前 `n=4` pilot 的二项检验 FDR 仍为 `0.125`，不能写成显著性行为学证据。可以写成：多 seed pilot 复现了奖励趋近、惩罚回避和弱 CS+ 冲突下的记忆驱动方向，支持继续扩大到 `n>=50` 的正式仿真和真实果蝇行为实验。

### n=50 正式代理仿真结果

本轮已经实际运行两套每条件 `n=50` 的 OCT/MCH 代理行为仿真：

1. late/terminal assay：`run_time = 0.8 s`，输出目录 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite_n50`。
2. early-decision assay：`run_time = 0.2 s`，输出目录 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_early_suite_n50`。

late assay 结果：

| condition | expected_choice_rate | mean_approach_margin | expected_choice_fdr_q |
| --- | ---: | ---: | ---: |
| `oct_sucrose_appetitive_wt` | 1.0 | 5.747301 | 1.776e-15 |
| `mch_sucrose_appetitive_wt_counterbalanced` | 1.0 | 5.732041 | 1.776e-15 |
| `oct_shock_aversive_wt` | 1.0 | -5.351253 | 1.776e-15 |
| `weak_oct_strong_mch_conflict` | 1.0 | 5.770910 | 1.776e-15 |

early-decision assay 结果：

| condition | expected_choice_rate | mean_approach_margin | expected_choice_fdr_q |
| --- | ---: | ---: | ---: |
| `oct_sucrose_appetitive_wt` | 0.80 | 0.252239 | 2.386e-05 |
| `mch_sucrose_appetitive_wt_counterbalanced` | 0.86 | 0.265210 | 2.798e-07 |
| `oct_shock_aversive_wt` | 0.92 | -0.226482 | 1.785e-09 |
| `weak_oct_strong_mch_conflict` | 0.86 | 0.244648 | 2.798e-07 |

严谨解释：

- 两个时间窗都稳定支持奖励趋近、惩罚回避和弱 CS+ / 强 CS- 冲突下的记忆方向。
- 但 MB perturbation 相对 WT 的 approach margin 差异没有通过 FDR 校正：late assay 中 `welch_fdr_q >= 0.984`，early assay 中 `welch_fdr_q = 1.0`。
- 因此当前可以把 calibrated motor bridge 写成“可靠表达 valence 和 CS+/CS- 方向的代理行为系统”，但不能写成“已经证明 MB 侧化扰动产生显著行为差异”。
- 侧化行为差异需要下一步引入更真实的 OCT/MCH sensory response 权重，或更直接的 MBON/DAN-to-DN motor readout 映射。

### n=50 mirror-side 早期动力学结果

为消除 `CS+` 左右摆放混杂，本轮新增 mirror-side 套件：每个条件都运行 `CS+` 左侧和右侧，输出目录为 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50`。详细中文解释见 `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_MIRROR_KINEMATICS_CN.md`。

运行命令：

```bash
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50 \
  --n-trials 50 \
  --run-time 0.2 \
  --max-workers 4 \
  --mirror-sides
```

新增变量：

- `n_nominal_side_trials`：原始条件表摆放的 trial 数。
- `n_mirror_side_trials`：左右互换摆放的 trial 数。
- `mean_expected_laterality_index`：按预期行为方向校正后的横向位移除以路径长度。
- `mean_early_expected_lateral_velocity`：前 `25%` 时间窗内朝预期方向的横向速度。
- `mean_expected_curvature_rad_per_mm`：按预期方向校正后的轨迹曲率。
- `mean_physical_laterality_index`：不按 `CS+` 方向校正的真实左/右漂移。

关键结果：

| condition | n_trials | expected_choice_rate | mean_approach_margin | expected_choice_fdr_q | mean_expected_laterality_index |
| --- | ---: | ---: | ---: | ---: | ---: |
| `oct_sucrose_appetitive_wt` | 100 | 0.86 | 0.265371 | 9.468e-14 | 0.089150 |
| `mch_sucrose_appetitive_wt_counterbalanced` | 100 | 0.85 | 0.245904 | 4.825e-13 | 0.084061 |
| `oct_shock_aversive_wt` | 100 | 0.86 | -0.244407 | 9.468e-14 | 0.083488 |
| `weak_oct_strong_mch_conflict` | 100 | 0.88 | 0.264908 | 3.823e-15 | 0.089230 |

MB 扰动相对 WT 的结果：

| comparison | q_approach | q_early_velocity | q_expected_laterality | q_physical_laterality | q_expected_curvature |
| --- | ---: | ---: | ---: | ---: | ---: |
| `oct_sucrose_left_mb_silenced` vs `oct_sucrose_appetitive_wt` | 1.0 | 1.0 | 1.0 | 1.0 | 0.170533 |
| `oct_sucrose_right_mb_silenced` vs `oct_sucrose_appetitive_wt` | 1.0 | 1.0 | 1.0 | 1.0 | 0.314646 |
| `oct_sucrose_mb_symmetrized` vs `oct_sucrose_appetitive_wt` | 1.0 | 1.0 | 1.0 | 1.0 | 0.693157 |
| `oct_sucrose_mb_swapped` vs `oct_sucrose_appetitive_wt` | 1.0 | 1.0 | 1.0 | 1.0 | 0.170533 |

严谨结论：

- mirror-side 后，valence memory 仍显著：奖励趋近、惩罚回避、弱 `CS+` 冲突下记忆驱动方向都稳定存在。
- `mean_physical_laterality_index` 接近 0，说明镜像摆放基本抵消了单纯空间偏置。
- 但 MB 侧化扰动在当前 calibrated low-dimensional motor bridge 中仍没有显著行为效应。曲率有趋势但最小 FDR q 仍为 `0.170533`，不能写成显著发现。
- 这不是“结构假说被否定”，而是说明当前 `MemoryCondition` 接口把 MBON/DAN/APL/DPM 信息压得太低维；下一步应实现 `OCT/MCH KC readout -> MBON/DAN/APL/DPM -> DN/motor` 的更直接映射。

## docs 目录整理

文档入口已整理到：

- `/unify/ydchen/unidit/bio_fly/docs/INDEX_CN.md`

早期计划、旧运行报告和临时说明已经归档到：

- `/unify/ydchen/unidit/bio_fly/docs/archive`
