# Descending-neuron 行为接口分析报告

保存路径：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/DN_BEHAVIOR_READOUT_REPORT_CN.md`

## 这一步在验证什么

果蝇大脑里很多感觉和记忆计算发生在脑内，例如嗅觉投射神经元、蘑菇体 Kenyon cell、DAN/MBON、视觉 LC/LPLC 通路等。真正把脑内计算交给身体执行的一类关键神经元是 descending neuron，简称 `DN`。DN 从脑部下行到腹神经索，影响走路、转向、逃逸、梳理、姿态和内部状态相关动作。

因此，如果要严谨复现 Eon/CyberFly 式“连接组约束行为”的结论，不能只看全脑传播热图，还要看不同感觉输入是否能在 FlyWire 连接组上传播到合理的 DN 家族。本报告就是把已有的多模态传播结果进一步压缩为 DN 家族、左右偏侧和候选行为解释。

## 主要结果

| 条件 | 被招募 DN 数 | DN 绝对响应量 | 左右偏侧指数 | 最高 DN 家族 | 最高家族占比 | 行为解释 |
|---|---:|---:|---:|---|---:|---|
| `gustatory_feeding` | 638 | 0.2554 | -0.103 | `DNge` | 0.514 | grooming, head/leg motor programmes and sensory-triggered action interface |
| `mechanosensory_grooming` | 769 | 0.4635 | -0.033 | `DNg` | 0.510 | general locomotor steering and grooming-related descending interface |
| `olfactory_food_memory` | 58 | 0.0115 | +0.049 | `DNge` | 0.282 | grooming, head/leg motor programmes and sensory-triggered action interface |
| `visual_object_tracking` | 704 | 0.2040 | -0.098 | `DNg` | 0.299 | general locomotor steering and grooming-related descending interface |

左右偏侧指数定义为 `(right_dn_abs_mass - left_dn_abs_mass) / (right_dn_abs_mass + left_dn_abs_mass)`。正值表示右侧 DN 响应量更高，负值表示左侧 DN 响应量更高。

## DN 家族前五名

| 条件 | DN 家族 | DN 数 | 绝对响应量 | 条件内占比 | 有符号响应量 |
|---|---|---:|---:|---:|---:|
| `gustatory_feeding` | `DNge` | 230 | 0.1312 | 0.514 | -0.0238 |
| `gustatory_feeding` | `DNg` | 195 | 0.1012 | 0.396 | +0.0288 |
| `gustatory_feeding` | `DNpe` | 46 | 0.0095 | 0.037 | +0.0038 |
| `gustatory_feeding` | `DNp` | 77 | 0.0064 | 0.025 | +0.0003 |
| `gustatory_feeding` | `DNa` | 28 | 0.0027 | 0.011 | -0.0027 |
| `mechanosensory_grooming` | `DNg` | 268 | 0.2362 | 0.510 | +0.1139 |
| `mechanosensory_grooming` | `DNge` | 260 | 0.1562 | 0.337 | +0.0960 |
| `mechanosensory_grooming` | `DNp` | 92 | 0.0229 | 0.049 | -0.0039 |
| `mechanosensory_grooming` | `DNpe` | 56 | 0.0113 | 0.024 | +0.0079 |
| `mechanosensory_grooming` | `DNa` | 25 | 0.0086 | 0.018 | -0.0075 |
| `olfactory_food_memory` | `DNge` | 21 | 0.0032 | 0.282 | +0.0031 |
| `olfactory_food_memory` | `DNb` | 2 | 0.0027 | 0.236 | +0.0027 |
| `olfactory_food_memory` | `DNg` | 13 | 0.0021 | 0.183 | +0.0019 |
| `olfactory_food_memory` | `DNpe` | 4 | 0.0013 | 0.109 | +0.0012 |
| `olfactory_food_memory` | `DNp` | 8 | 0.0011 | 0.098 | +0.0004 |
| `visual_object_tracking` | `DNg` | 196 | 0.0609 | 0.299 | +0.0343 |
| `visual_object_tracking` | `DNge` | 233 | 0.0592 | 0.290 | +0.0229 |
| `visual_object_tracking` | `DNp` | 105 | 0.0382 | 0.187 | -0.0016 |
| `visual_object_tracking` | `DNpe` | 70 | 0.0149 | 0.073 | -0.0029 |
| `visual_object_tracking` | `DNa` | 31 | 0.0103 | 0.050 | +0.0010 |

## 输出文件

- DN 总结表：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_behavior_readout_summary.csv`
- DN 家族表：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_family_readout_summary.csv`
- DN 左右偏侧表：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_side_laterality_summary.csv`
- top DN 明细表：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_top_targets_by_condition.csv`
- DN 家族热图：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_family_readout_heatmap.png`
- DN 偏侧指数图：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_laterality_index.png`
- DN 左右响应量堆叠图：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_side_mass_stacked.png`
- DN 机制动画：`/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/videos/dn_multimodal_mechanism_summary.mp4`
- 论文视频副本：`/unify/ydchen/unidit/bio_fly/paper/video/dn_multimodal_mechanism_summary.mp4`

## 对论文最有用的写法

可以写：不同感觉输入在 FlyWire v783 图上传播后，招募了不同 DN 家族，并且这些 DN 家族对应不同的候选行为接口。视觉、味觉和机械感觉条件比嗅觉条件产生更强的 DN 读出，说明“气味记忆”更多经过蘑菇体/脑内记忆轴，而“视觉目标、接触/梳理、味觉/进食”更直接进入下行运动接口。

需要谨慎写：DN 响应是连接组传播的功能性预测，不等于已经证明完整行为自动涌现。当前视频中的视觉、梳理和进食仍包含代理控制器或代理渲染；真正 Nature 级别的功能证明还需要原始 Eon 参数、真实 DN-to-motor 映射、同一刺激条件下的行为实测校准和跨个体统计。
