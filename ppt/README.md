# 赛博果蝇项目教师汇报 PPT

保存路径：`/unify/ydchen/unidit/bio_fly/ppt/README.md`

## 文件说明

- `/unify/ydchen/unidit/bio_fly/ppt/cyber_fly_teacher_report.tex`：中文 Beamer PPT 源码。
- `/unify/ydchen/unidit/bio_fly/ppt/cyber_fly_teacher_report.pdf`：编译后的汇报 PDF。
- `/unify/ydchen/unidit/bio_fly/ppt/figures`：PPT 使用的论文级图表素材。
- `/unify/ydchen/unidit/bio_fly/ppt/IMAGE_PROMPTS_FOR_GROUP_MEETING.md`：可交给 GPT Image 生成组会示意图的详细 prompt。

## 编译命令

```bash
cd /unify/ydchen/unidit/bio_fly/ppt
latexmk -xelatex -interaction=nonstopmode -halt-on-error cyber_fly_teacher_report.tex
```

清理 LaTeX 中间文件：

```bash
cd /unify/ydchen/unidit/bio_fly/ppt
latexmk -c cyber_fly_teacher_report.tex
```

## 编译检查结果

已在本机完成 XeLaTeX 编译：

- 输出 PDF：`/unify/ydchen/unidit/bio_fly/ppt/cyber_fly_teacher_report.pdf`
- 页数：`19`
- 文件大小：约 `2.7 MB`
- 格式检查：LaTeX 日志中未发现 `LaTeX Error`、`Package Error`、`Undefined control sequence` 或 `Fatal error`；仅有 1 处 `0.5567pt` 的轻微 `Overfull vbox`，未造成可见重叠。
- 日志中仍有 beamer/ctex 导航元信息造成的 `Missing character ... nullfont` 提示；它们未造成可见文字缺失，不影响 PDF 使用。
- 渲染检查：使用 Ghostscript 将 PDF 渲染为 PNG，确认标题页、实验设计页、递质侧化主发现页、连接组传播页、DPM 光遗传页、OCT/MCH 行为页、视频渲染页、MB 扰动负结果页和验证路径页均能正常显示。
- 人工抽查：结构热图、传播热图、连接组指标解释页、DN laterality 图、DPM 协议图、OCT/MCH 统计图、赛博果蝇视频关键帧页和视频渲染页没有发现明显文字/图表重叠。

日志中仍有 `fontspec` 的 WenQuanYi 字体 `Script CJK` 提示，以及 beamer/ctex 生成导航元信息时的 `Missing character ... nullfont` 提示。它们未导致编译失败，也未在抽查页面中造成可见文字缺失；当前 PDF 可用于汇报。

## 二次改稿说明

用户反馈上一版“不像博士生组会汇报，像对话稿”，并明确要求每一个结果前面先加一页实验设计，说明做了什么、怎么拿到结论、指标是什么，同时不要单独放名词解释页。本版已改成面向真实组会汇报的“实验设计 -> 结果结论”结构：

- 标题改为明确科学问题：`从果蝇蘑菇体递质侧化到可验证的记忆行为假说`。
- 第二页直接给出汇报结构、当前最稳发现和证据边界。
- 删除独立名词解释页；所有名词在对应实验页内就地解释，例如 5-HT/Glu、KC、DPM、OCT/MCH、CS+/CS-、DN 和 laterality index。
- 每个核心结果前均加入实验页：数据来源、对象、方法、控制、统计指标和结论获得方式。
- 参考文献不再每页都放，只保留在标题、FlyWire 数据、蘑菇体结构、连接组传播、DPM 光遗传、OCT/MCH 行为、湿实验验证和核心参考页。
- PPT 作者改为 `陈胤达`，日期改为 `2026年4月30日`。
- 主体现在以用户原始 paper 的主发现为核心：右侧血清素富集、左侧谷氨酸偏置，并强调最强位置是 $\alpha'\beta'$ 记忆巩固相关亚区。
- 主体按组会逻辑展开：研究设计、数据和实验条件、递质侧化结构结果、赛博果蝇传播结果、DPM 光遗传预测、OCT/MCH 行为结果、视频可视化、负结果、湿实验验证、风险和下一步。
- 每个关键实验都说明“怎么做、看什么指标、发现什么、不能过度解释什么”。
- 新增“实验 2 指标解读”页，面向 0 生物基础的计算机研究者解释 `memory axis mass`、`abs mass`、`response laterality`、`empirical p` 和 `FDR q` 的计算含义与用途。
- 四卡传播仿真页保留核心结论：右侧血清素 KC seed 和左侧谷氨酸 KC seed 相对同侧随机 KC 对照，显著改变 memory axis、DAN、APL、DPM、MBON/MBIN 和左右读出，FDR q=0.038。
- 明确加入最重要的负结果：MB left/right silencing、symmetrization、swap 与 WT 相比当前均未显著改变行为，主要 FDR q=1.0。
- 保留“当前风险”和“下一步计划”两页，区分计算实验补强和湿实验验证。
- 新增“赛博果蝇可视化结果”页，嵌入 DPM 光遗传预测、OCT/MCH 行为代理和多模态代理演示的关键帧，并在页内标出可点击/可打开的视频绝对路径。
- 视频页明确说明视频用于展示和检查，统计证据来自 n=100 mirror-side trial、连接组传播和显著性检验，而不是视频本身。
- 新增独立文档 `IMAGE_PROMPTS_FOR_GROUP_MEETING.md`，用于生成更像论文示意图的机制图、DPM 光遗传设计图、OCT/MCH 行为实验图和证据链图。

## PPT 内容结构

这份汇报面向不熟悉生物学或 AI 仿真的老师，按下面逻辑组织：

1. 标题页提出科学问题：左右蘑菇体是否存在可传播到记忆环路的递质侧化。
2. 汇报结构页给出四个问题和当前结论层级。
3. 实验 1 说明 FlyWire 结构统计怎么做，结果 1 展示 KC 输入 5-HT 右偏、Glu 左偏。
4. 实验 2 说明连接组传播和随机对照，并单独解释传播指标；结果 2 展示侧化 seed 可到达 memory axis、DAN、APL、DPM、MBON/MBIN。
5. 实验 3 说明为什么检查 DN/motor bridge，结果 3 展示 MBON/memory axis 到 DN 出口的强度和侧向偏置。
6. 实验 4 说明 DPM 光遗传仿真设置，结果 4 展示推荐红光协议和 release pattern。
7. 实验 5 说明 OCT/MCH 行为代理和 mirror-side 设计，结果 5 展示奖励、惩罚、conflict 条件方向稳定。
8. 赛博果蝇可视化页展示 DPM、OCT/MCH 和多模态代理视频关键帧及绝对路径。
9. 实验 6 说明视频渲染的用途和边界。
10. 负结果页主动展示 MB 扰动尚未产生显著行为差异。
11. 最后给出湿实验验证路径、风险、下一步和核心结论。

## 严谨表述边界

PPT 中刻意避免以下过度声称：

- 不说“已经完整复刻 Eon 私有闭环系统”。
- 不说“已经恢复 Eon DN-to-body 权重”。
- 不说“连接组单独自动涌现完整果蝇行为”。
- 不把当前 MB 扰动行为结果说成显著正结果。

当前最稳妥的论文定位是：

> 公开连接组约束的蘑菇体神经递质侧化发现与仿真验证：右侧血清素富集、左侧谷氨酸偏置可传播到记忆相关读出，并生成可由真实 OCT/MCH 行为学、单侧神经操控和钙成像进一步验证的因果假说。

## PPT 使用的主要图表

- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_oct_mch_formal_suite.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_oct_mch_assay_v2_key_conditions_frame.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_ext1_cohens_d_heatmap_all_NT.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig2_functional_metric_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig3_empirical_null_significance.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_mb_transition_laterality.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_kc_upstream_nt_by_side.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_mb_dn_motor_mechanism.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_mb_dn_laterality_index.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_mb_dn_motor_primitive_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_structure_behavior_linkage.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_dpm_release_video_frame.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_oct_mch_video_midframe.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_cyberfly_multimodal_video_frame.png`
- `/unify/ydchen/unidit/bio_fly/ppt/figures/Fig_cyberfly_grooming_video_frame.png`

## PPT 内嵌/链接的视频

- `/unify/ydchen/unidit/bio_fly/paper/video/dpm_optogenetic_release_prediction.mp4`：DPM 光遗传激活后 5-HT/KC readout release pattern 的动态展示。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_key_conditions.mp4`：OCT/MCH 关键行为条件的视频展示，包含气味杯、气味羽流、糖奖励/电击、轨迹和统计 inset。
- `/unify/ydchen/unidit/bio_fly/paper/video/eon_multimodal_reproduction_summary.mp4`：视觉、食物和梳理等多模态代理演示，用于说明当前代理层覆盖的环境交互类型。
