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
- `/unify/ydchen/unidit/bio_fly/docs/OLFACTORY_PERTURBATION_MEMORY_CN.md`：嗅觉扰动和记忆行为实验。
- `/unify/ydchen/unidit/bio_fly/docs/LATERALIZATION_BEHAVIOR_SIMULATION_CN.md`：侧化行为仿真和剂量/镜像实验。
- `/unify/ydchen/unidit/bio_fly/docs/STRUCTURE_BEHAVIOR_LINKAGE_CN.md`：结构-功能-行为联动统计。
- `/unify/ydchen/unidit/bio_fly/docs/TARGET_PRIORITIZATION_CN.md`：可湿实验验证的 MBON/DAN/APL/DPM 靶点优先级。
- `/unify/ydchen/unidit/bio_fly/docs/MOTOR_AND_ODOR_BRIDGE_CN.md`：本轮新增的 OCT/MCH sensory encoder、calibrated motor interface 和行为桥接总结。

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
- 当前结果支持“蘑菇体左右结构侧化可能影响嗅觉记忆检索和行为偏置”的可检验假说。

不能严谨声称：

- 已完全复刻 Eon 私有闭环系统。
- 已恢复 Eon 内部 DN-to-motor 权重。
- 连接组单独无接口、无训练、无参数校准地自动涌现完整果蝇行为。
- 当前代理视频等同于真实果蝇行为学显著性证据。

