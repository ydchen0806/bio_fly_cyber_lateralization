# 文章修改与功能性仿真增强报告

保存路径：`/unify/ydchen/unidit/bio_fly/docs/ARTICLE_REVISION_AND_FUNCTIONAL_SIMULATION_CN.md`

## 1. 新增结果是否支持原文章结论

支持，但支持的是更深一层的“功能环路机制”，不是简单重复原文统计。

原文核心结论是：果蝇蘑菇体 Kenyon Cells 的输入神经递质存在左右侧化，特别是 serotonin 右侧富集、glutamate 左侧偏置，并且这种侧化在与记忆巩固相关的 alpha-prime/beta-prime lobe 中最强。

本轮新增结果直接读取 FlyWire v783 聚合连接表和官方 annotation 表，得到如下增强证据：

- `KC->KC`、`KC->APL`、`APL->KC`、`KC->DPM`、`DPM->KC` 等反馈和记忆稳定环路整体左偏。
- `DAN->MBON` 和 `MBON->DAN` 输出/调制环路轻度右偏。
- `KC->MBON` 总体近似平衡，说明不是某一侧整体输出缺失。

因此，新结果把原文的“NT 输入侧化”推进成一个更可检验的模型：左侧蘑菇体更偏反馈稳定和记忆维持，右侧蘑菇体更偏调制输出和状态切换。

## 2. 已修改的文章文件

- `/unify/ydchen/unidit/bio_fly/paper/main_merged.tex`
- `/unify/ydchen/unidit/bio_fly/paper/NATURE_STYLE_DRAFT_CN.md`
- `/unify/ydchen/unidit/bio_fly/paper/FIGURE_AND_VIDEO_INDEX_CN.md`

`/unify/ydchen/unidit/bio_fly/paper/main_merged.tex` 已新增：

- 摘要中的功能环路仿真结论。
- 结果小节 `Connectome-constrained simulations link lateralized circuits to food-odour memory`。
- 新主图 `Fig. mb_circuit_sim`，引用新增结构图。
- 讨论中对“左侧反馈稳定 / 右侧输出调制”模型的解释。
- 方法中新增 `Circuit mining and embodied food-odour simulation`。
- 局限性中明确说明当前 FlyGym 食物实验是 sugar-associated odour target，不是真实可摄取糖滴。

## 3. 新增功能性仿真实验

实验脚本：

- `/unify/ydchen/unidit/bio_fly/scripts/run_food_memory_suite.py`
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/food_memory.py`

实验含义：

当前 FlyGym 环境没有真正可摄取的糖滴对象，因此把“食物”实现为糖奖励相关气味源，即 CS+。另一个气味源为 CS-，代表中性或竞争性气味。虚拟果蝇根据嗅觉输入、记忆增益和左右蘑菇体侧化权重调整转向，模拟“闻到食物气味并根据记忆寻找食物”的过程。

实验条件：

- `food_naive_balanced_search`：无侧化、较弱食物记忆。
- `food_learned_sugar_memory`：糖奖励记忆增强。
- `food_left_kc_apl_dpm_feedback`：模拟左侧 KC-APL-DPM 反馈环增强。
- `food_right_dan_mbon_output`：模拟右侧 DAN-MBON 输出/调制轴增强。
- `food_weak_sugar_strong_decoy`：弱食物气味与强竞争气味冲突。

## 4. 新视频

论文视频目录：

- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`

分析输出目录：

- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite`
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/FOOD_MEMORY_SIMULATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite/food_memory_behavior_summary.csv`

## 5. 行为结果解释

当前所有条件都到达 CS+，说明二分类 `food_choice_rate` 饱和；这与之前嗅觉实验一致。因此文章中不应只报告选择率，而应使用连续轨迹变量：

- `mean_food_approach_margin`：到 CS- 的距离减去到 CS+ 的距离，越大表示越接近食物气味。
- `mean_signed_final_y`：镜像校正后的终点方向，用于看左右偏置。
- `mean_path_length`：轨迹长度，用于排除运动不足或路径异常。

仿真结果显示 learned sugar memory 的 approach margin 高于 naive balanced search，说明食物记忆增益确实增强了对 CS+ 的接近。左侧 KC-APL-DPM feedback 和右侧 DAN-MBON output 条件在终点方向和路径长度上呈现不同模式，适合写成真实实验预测。

## 6. 对 Nature 级文章叙事的增强

建议主文逻辑从三层提升到四层：

1. 表征学习：HGNNA/topology 解决大规模神经元表示。
2. 结构发现：KC 输入 NT 侧化，serotonin 右富集、glutamate 左偏。
3. 环路机制：左侧 KC-APL-DPM 反馈稳定、右侧 DAN-MBON 输出调制。
4. 行为预测：食物/糖气味记忆仿真给出可实验验证的 approach-margin 预测。

最严谨的表述是：新增仿真支持原文结论的功能可解释性，并提出可检验预测；它还不是最终生物因果证明。下一步需要真实果蝇行为、单侧 APL/DPM/DAN/MBON 操控和钙成像验证。
