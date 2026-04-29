# 给没有生物背景读者的验证逻辑说明

保存路径：`/unify/ydchen/unidit/bio_fly/docs/NON_BIOLOGIST_VALIDATION_LOGIC_CN.md`

最后更新：`2026-04-29`

## 1. 我们到底在研究什么

一句话说：我们怀疑果蝇左右脑的记忆电路不是完全对称的，尤其是蘑菇体输入里，右侧更偏血清素，左侧更偏谷氨酸；我们用“赛博果蝇”仿真先预测这种左右差异会怎样影响神经活动和行为，再设计真实生物实验去验证。

这里的核心不是“做一个很像果蝇的视频”，而是建立一条因果链：

`左右脑结构不一样 -> 神经信号传播不一样 -> 记忆相关脑区读出不一样 -> 果蝇在气味选择任务中的行为概率不一样`

如果这条链被仿真和真实实验共同支持，就说明左右脑的递质侧化可能不是一个静态结构现象，而是会影响记忆和行为的功能机制。

## 2. 关键名词解释

### 果蝇

果蝇是一种常用模式动物。它的大脑比小鼠和人类简单很多，但仍然有嗅觉、视觉、学习、记忆和行为决策能力。它适合做神经科学研究，因为连接组数据比较完整，很多遗传工具也成熟。

### 连接组

连接组可以理解为大脑的“接线图”。节点是神经元，边是突触连接。FlyWire 是一个果蝇全脑连接组数据集，告诉我们哪些神经元连到哪些神经元、连接大概有多强。

连接组本身只能告诉我们“线路怎么接”，不能直接告诉我们“行为会怎样”。所以我们需要仿真，把结构差异推演成功能差异和行为预测。

### 蘑菇体

蘑菇体是果蝇学习和记忆的重要脑区，尤其和嗅觉记忆有关。果蝇闻到某种气味时，蘑菇体会参与判断这种气味过去是否和糖奖励、电击惩罚或其它结果关联。

### KC

KC 是 Kenyon cell，中文常译为 Kenyon 细胞，是蘑菇体的主要内在神经元。可以粗略理解为蘑菇体里负责“编码气味和记忆线索”的核心细胞。

### MBON

MBON 是 mushroom body output neuron，蘑菇体输出神经元。它把蘑菇体内部的记忆状态传给下游决策网络。可以理解为“蘑菇体告诉身体该接近还是回避”的出口之一。

### DAN

DAN 是 dopaminergic neuron，多巴胺神经元。它常和奖励、惩罚、学习更新有关。果蝇被糖奖励或电击惩罚时，多巴胺系统会参与修改记忆。

### APL

APL 是 anterior paired lateral neuron，是蘑菇体里的一个广泛反馈调控神经元。可以粗略理解为帮助蘑菇体保持稀疏、稳定编码的调节器。

### DPM

DPM 是 dorsal paired medial neuron，和蘑菇体记忆维持、记忆巩固和血清素调节有关。我们现在特别关注 DPM，是因为老师会议里提出：可以用光遗传激活 DPM，看左右脑血清素释放 pattern 是否有差异。

### 5-HT / serotonin / 血清素

5-HT 就是 serotonin，中文叫血清素，是一种神经递质。神经递质可以理解为神经元之间传递信息的化学信号。我们的结构发现中，右侧蘑菇体相关输入更偏 5-HT。

### Glu / glutamate / 谷氨酸

Glu 是 glutamate，中文叫谷氨酸，也是一种神经递质。我们的结构发现中，左侧蘑菇体相关输入更偏 Glu。

### 递质侧化

侧化就是左右不对称。递质侧化指左右脑在某类神经递质输入或释放上存在系统差异。比如右侧 5-HT 更强、左侧 Glu 更强。

这不是说左脑完全没有 5-HT 或右脑完全没有 Glu，而是说统计上存在偏向。

### 光遗传

光遗传是一种生物实验技术。研究者让某类神经元表达对光敏感的蛋白，然后用特定颜色的光激活或抑制这些神经元。

本项目建议的例子是：让 DPM 神经元表达 CsChrimson 或 ReaChR，然后用 617/627 nm 红光刺激 DPM。

### 5-HT sensor

5-HT sensor 是能报告血清素变化的荧光传感器。血清素释放越强，荧光信号通常越明显。实验上可以用显微镜记录左右脑的荧光变化。

### GCaMP

GCaMP 是一种钙成像传感器。神经元活动增强时，钙信号通常会变化，GCaMP 能把这种变化变成荧光读出。

### OCT 和 MCH

OCT 是 3-octanol，MCH 是 4-methylcyclohexanol。它们是果蝇嗅觉学习实验里常用的两种气味。

实验里可以把 OCT 和糖奖励配对，让 OCT 成为正性气味；也可以把 OCT 和电击配对，让 OCT 成为负性气味。MCH 可以作为另一个对照气味。

### CS+ 和 CS-

CS 是 conditioned stimulus，条件刺激。

CS+ 是训练时和奖励或惩罚配对的气味。例如“闻 OCT 的同时给糖”，OCT 就是糖奖励任务里的 CS+。

CS- 是没有配对奖励/惩罚的对照气味。例如 MCH 只是闻到但没有糖或电击，它就是 CS-。

### T-maze

T-maze 是一个 T 字形选择装置。果蝇从中间出发，左右两边分别放两种气味，看果蝇最后更多跑向哪一边。它能测群体的气味偏好和记忆选择。

### choice index

choice index 是选择指数，用来表示果蝇群体更偏向哪一边或哪种气味。它不是单只果蝇的“想法”，而是群体统计结果。

一个常见形式是：

`choice index = (选择目标气味的数量 - 选择对照气味的数量) / 总数量`

数值越正，说明越偏向目标气味；接近 0，说明没有明显偏好；负值说明更偏向另一边。

### laterality index / LI

LI 是左右偏侧指数，用来量化左边和右边谁更强。常见形式是：

`LI = (右侧信号 - 左侧信号) / (右侧信号 + 左侧信号)`

LI 大于 0 表示右侧更强，LI 小于 0 表示左侧更强。

## 3. 我们仿真了什么

### 仿真 1：结构发现整理

我们先从论文 zip 和 FlyWire 注释中整理结构发现：蘑菇体 KC 输入里，右侧更偏 5-HT，左侧更偏 Glu，而且 alpha'beta' 记忆巩固相关区域最明显。

这一步回答的问题是：我们要验证的左右差异到底是什么。

输出路径：

- `/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/nt_structural_summary.csv`

### 仿真 2：四卡连接组传播

然后我们把右侧 5-HT 相关 KC 或左侧 Glu 相关 KC 当作起点，在 FlyWire 连接图上推演信号会传到哪里。

这一步像是在问：如果这个侧化通路真的被激活，它会不会影响记忆相关下游脑区？

结果显示，这些侧化 seed 的影响可以传播到 memory axis、DAN、APL、DPM、MBON/MBIN 和左右读出。这说明侧化不是只停留在局部结构描述，而是可能影响功能网络。

输出路径：

- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv`

### 仿真 3：OCT/MCH 气味记忆行为代理

我们设计了一个果蝇闻气味的任务：一边是 OCT，一边是 MCH；其中一个气味作为 CS+，另一个作为 CS-。我们让仿真果蝇在培养皿或 T-maze 风格环境里选择方向。

这一步不是最终生物证据，而是把抽象的神经 readout 转成老师和审稿人能看懂的行为任务：果蝇闻到了什么，学到了什么，最后往哪里走。

当前结果说明：代理系统能稳定表达奖励趋近和惩罚回避；但是 MB 侧化扰动相对 WT 的行为差异还不够强，不能单独作为真实行为因果证据。

输出路径：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50`
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_key_conditions.mp4`

### 仿真 4：会议反馈后的 5-HT/Glu 分拆

老师指出：如果 5-HT 和 Glu 都侧化，要尽量分开看它们分别影响什么。于是我们分别减弱或移除 5-HT-right、Glu-left 和 both-blunted 条件。

当前结果更谨慎地支持：

- Glu-left 更像广谱 memory-output 扰动轴。
- 5-HT-right 更适合做 DPM 光遗传、5-HT release pattern 和记忆巩固时间窗验证。

输出路径：

- `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429`

### 仿真 5：DPM 光遗传验证

这是当前最贴近湿实验的一组仿真。

我们模拟用红光激活 DPM neuron。仿真输入包括：

- DPM 神经元 seed。
- 光遗传工具，例如 CsChrimson 或 ReaChR。
- 光刺激参数，例如波长、频率、脉宽、时长、光强。
- FlyWire 连接组。
- 下游 ROI，例如 KC、MBON、DAN、APL。

仿真输出包括：

- DPM 激活后信号传播到哪些脑区。
- 预测左/右 5-HT release pattern。
- 预测按脑侧注册的 release LI。
- 预测 OCT/MCH 群体行为 choice index 会怎么变。
- 推荐给湿实验老师的光遗传协议。

当前推荐协议是优先测试红光工具：

- `CsChrimson 617 nm`
- `ReaChR 627 nm`
- `40 Hz`
- `20 ms pulses`
- `5.0 s`
- `0.1 mW/mm2` 起步

输出路径：

- `/unify/ydchen/unidit/bio_fly/docs/DPM_OPTOGENETIC_VALIDATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429`

## 4. 我们发现了什么

当前最稳的发现分三层。

### 第一层：结构层

蘑菇体 KC 输入存在递质侧化：

- 右侧更偏 5-HT/血清素。
- 左侧更偏 Glu/谷氨酸。
- alpha'beta' 记忆巩固相关区域最强。

这说明左右蘑菇体不是完全等价的。

### 第二层：功能传播层

把这些侧化输入放到 FlyWire 连接图里传播后，它们不是只影响局部，而是能影响：

- memory axis：记忆相关轴。
- DAN：多巴胺教学/奖惩信号。
- APL：蘑菇体反馈抑制。
- DPM：记忆维持和 5-HT 调节。
- MBON/MBIN：蘑菇体输出和输入相关神经元。
- 左右偏向 readout。

这说明侧化结构有可能变成功能差异。

### 第三层：可验证预测层

DPM 光遗传仿真预测：

- 如果 DPM/5-HT 侧化是真实的，用红光激活 DPM 后，右侧 5-HT/KC readout 应该更强。
- 如果把果蝇水平旋转 180 度，按脑侧注册的右偏应该保持。
- 如果只是成像角度伪影，那么按相机图像坐标看的左右差异更可能翻转。
- 在独立群体 T-maze 中，DPM 红光刺激应该能改变 delayed/conflict 条件的 OCT/MCH choice index。

这些是湿实验可以直接验证的预测。

## 5. “两方面证明”到底是什么意思

### 证明 A：功能成像证明

证明 A 的目标是证明：仿真预测的左右 release pattern 在真实神经活动里能看到。

具体做法：

1. 让 DPM 神经元表达红光敏感蛋白，例如 CsChrimson 或 ReaChR。
2. 让蘑菇体 KC 或某个 MB compartment 表达 5-HT sensor 或 GCaMP。
3. 用 617/627 nm 红光激活 DPM。
4. 用显微镜记录左侧和右侧的荧光变化。
5. 计算左右 dF/F、AUC、半衰期和 release LI。
6. 把同一只果蝇水平旋转 180 度后重复一次。
7. 分析时按脑的左/右注册，而不是按相机图像的左/右注册。

如果结果是：

- 右侧 5-HT/KC readout 稳定高于左侧；
- 旋转 180 度后，按脑侧注册仍保持右偏；

那么说明仿真预测的偏侧化 release pattern 有功能对应。

这一步不需要果蝇继续做行为，因为成像可能会损伤或强烈扰动果蝇。

### 证明 B：群体行为证明

证明 B 的目标是证明：DPM/5-HT 轴不只是能产生荧光差异，还能改变可观测行为。

具体做法：

1. 另取一批果蝇，不和成像果蝇混用。
2. 做 OCT/MCH T-maze 嗅觉记忆实验。
3. 设置 delayed memory 或 weak OCT/strong MCH conflict 条件，因为这些条件不容易天花板化，更容易看到 DPM 调节效应。
4. 在训练、巩固或测试窗口给 DPM 红光刺激。
5. 统计果蝇群体选择 OCT 还是 MCH。
6. 计算 choice index、approach margin、early turning bias。
7. 做 side mirror 和 OCT/MCH counterbalance，排除左右摆放和气味身份偏差。

如果结果是：

- DPM 红光刺激按仿真预测方向改变 choice index；
- 这种改变不是由总体活动量、红光本身、视刺激或气味摆放造成；

那么说明 DPM/5-HT 轴能调节可观测行为。

这一步不需要知道每只果蝇的 NT 侧化程度，因为它是群体统计验证。

## 6. 为什么 A 和 B 合起来更有说服力

单独做 A，只能说明神经活动或 5-HT release pattern 有左右差异，但不能证明这个差异会影响行为。

单独做 B，只能说明 DPM 光遗传能改变行为，但别人可能会质疑：这是不是非特异兴奋、运动能力变化、红光干扰，或者和我们发现的 5-HT 侧化无关？

A 和 B 合起来就更强：

1. 连接组和 NT 统计提出假说：右侧 5-HT、左侧 Glu 侧化存在。
2. 仿真预测：DPM 光遗传会产生右偏 5-HT/KC readout，并影响 OCT/MCH choice index。
3. 功能成像验证：真实果蝇里能看到按脑侧注册的 release/readout 偏侧化。
4. 群体行为验证：独立果蝇群体中，DPM 红光刺激能按预测方向改变记忆选择。
5. GRASP/split-GFP 结构验证：证明侧化连接或接触在群体中稳定存在。

这就形成了从结构、功能到行为的证据闭环。

## 7. 还需要注意什么边界

当前不能声称：

- 已经完整复刻 Eon Systems 的私有赛博果蝇系统。
- 连接组单独自动涌现了完整果蝇行为。
- 真实果蝇已经被本项目证明存在 DPM 光遗传右偏 5-HT release。
- 当前视频本身就是最终行为学显著性证据。

当前可以严谨声称：

- 我们建立了公开可审计的连接组约束仿真流程。
- 我们把结构侧化发现转成了可测的功能成像和群体行为预测。
- 当前仿真优先支持 right 5-HT/DPM 作为功能成像验证轴，left Glu 作为广谱 memory-output 扰动轴。
- 下一步湿实验应按“结构验证 + 功能成像 + 群体行为”的三证据路线推进。

## 8. 最短复现命令

DPM 光遗传仿真：

```bash
cd /unify/ydchen/unidit/bio_fly
CUDA_VISIBLE_DEVICES=0,1 /unify/ydchen/unidit/bio_fly/env/bin/python \
  /unify/ydchen/unidit/bio_fly/scripts/run_dpm_optogenetic_validation.py \
  --devices cuda:0 cuda:1
```

会议反馈分拆实验：

```bash
cd /unify/ydchen/unidit/bio_fly
CUDA_VISIBLE_DEVICES=0,1 /unify/ydchen/unidit/bio_fly/env/bin/python \
  /unify/ydchen/unidit/bio_fly/scripts/run_meeting_feedback_experiments.py \
  --devices cuda:0 cuda:1
```

主要阅读入口：

- `/unify/ydchen/unidit/bio_fly/README.md`
- `/unify/ydchen/unidit/bio_fly/docs/DPM_OPTOGENETIC_VALIDATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/TEACHER_BRIEFING_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/NON_BIOLOGIST_VALIDATION_LOGIC_CN.md`
