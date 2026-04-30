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
- 文件大小：约 `2.6 MB`
- 格式检查：LaTeX 日志中未发现 `Overfull`、`LaTeX Error`、`Package Error`、`Undefined control sequence` 或 `Fatal error`。
- 日志中仍有窄列表格里的英文短语断行提示，以及 beamer/ctex 导航元信息造成的 `Missing character ... nullfont` 提示；它们未造成可见文字缺失，不影响 PDF 使用。
- 渲染检查：使用 Ghostscript 将 PDF 渲染为 PNG，确认新增术语页、递质侧化主发现页、结构热图页、四卡传播仿真页、中文路径表和英文 paper reader guide 均能正常显示。
- 人工抽查：名词说明页、血清素/谷氨酸侧化页、四卡传播仿真页、OCT/MCH 统计页、MB 扰动负结果页、隐患页、补充实验页和 take-home message 页可以正常显示。

日志中仍有 `fontspec` 的 WenQuanYi 字体 `Script CJK` 提示，以及 beamer/ctex 生成导航元信息时的 `Missing character ... nullfont` 提示。它们未导致编译失败，也未在抽查页面中造成可见文字缺失；当前 PDF 可用于汇报。

## 二次改稿说明

用户反馈上一版“AI 味太重，发现和结论没有说清楚”，后续又要求压缩成组会汇报版本。本版已改成面向真实组会汇报的精简叙事结构：

- 标题改为明确科学问题：`赛博果蝇能否把左右脑递质侧化变成可验证的记忆假说？`
- 第二页直接给出当前最稳的发现和风险，不再只做泛泛摘要。
- 开场名词说明被压缩为一页，解释 MB、KC、5-HT、Glu、DAN、MBON、APL、DPM、CS+/CS-、OCT/MCH 和 laterality index。
- 主体现在以用户原始 paper 的主发现为核心：右侧血清素富集、左侧谷氨酸偏置，并强调最强位置是 $\alpha'\beta'$ 记忆巩固相关亚区。
- 主体按组会逻辑展开：研究设计、数据和实验条件、递质侧化结构结果、赛博果蝇传播结果、DPM 光遗传预测、OCT/MCH 行为结果、视频可视化、负结果、湿实验验证、风险和下一步。
- 每个关键实验都说明“怎么做、看什么指标、发现什么、不能过度解释什么”。
- 四卡传播仿真页保留核心结论：右侧血清素 KC seed 和左侧谷氨酸 KC seed 相对同侧随机 KC 对照，显著改变 memory axis、DAN、APL、DPM、MBON/MBIN 和左右读出，FDR q=0.038。
- 明确加入最重要的负结果：MB left/right silencing、symmetrization、swap 与 WT 相比当前均未显著改变行为，主要 FDR q=1.0。
- 保留“当前风险”和“下一步计划”两页，区分计算实验补强和湿实验验证。
- 视频页明确说明视频用于展示和检查，统计证据来自 n=100 mirror-side trial，而不是视频本身。
- 新增独立文档 `IMAGE_PROMPTS_FOR_GROUP_MEETING.md`，用于生成更像论文示意图的机制图、DPM 光遗传设计图、OCT/MCH 行为实验图和证据链图。

## PPT 内容结构

这份汇报面向不熟悉生物学或 AI 仿真的老师，按下面逻辑组织：

1. 先给结论和必要名词，让非生物背景老师能快速进入问题。
2. 讲研究设计和实验条件，明确什么是结构统计、什么是赛博果蝇传播、什么是行为代理。
3. 展示结构结果：KC 输入中血清素系统性右偏，谷氨酸多数左偏，最强在 $\alpha'\beta'$。
4. 展示仿真结果：右侧血清素 KC 和左侧谷氨酸 KC 能传播到 memory axis、DAN、APL、DPM、MBON/MBIN。
5. 展示 DPM 光遗传预测：617/627 nm 红光协议、release pattern 和 180 度旋转控制。
6. 展示 OCT/MCH 行为结果：奖励、惩罚、conflict 条件方向稳定。
7. 主动展示 MB 扰动负结果，说明当前行为代理还不能证明真实行为因果。
8. 最后给出湿实验验证路径、风险和下一步计划。

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
