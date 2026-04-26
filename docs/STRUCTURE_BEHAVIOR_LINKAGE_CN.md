# 结构-功能-行为关联探索报告

更新时间：2026-04-26T11:53:04

## 1. 目标

本报告把 FlyWire KC neurotransmitter 结构侧化、四卡 signed propagation 功能读出、FlyGym/MuJoCo 行为轨迹放在同一张证据链里，寻找比单一结构差异或单一视频更强的可发表假说。

## 2. 新增输出

- 结构 NT 汇总：`/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/nt_structural_summary.csv`
- 行为条件汇总：`/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/behavior_condition_summary.csv`
- 剂量-行为相关性：`/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/dose_response_correlations.csv`
- 功能-行为候选表：`/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/functional_behavior_linkage.csv`
- 关联图：`/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage/Fig_structure_behavior_linkage.png`

## 3. 结构侧化重点

| nt | n_subtype_tests | n_fdr_significant | n_right_biased | n_left_biased | mean_right_laterality_index | max_abs_cohens_d | min_fdr_q | top_subtypes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| glut | 11 | 7 | 4 | 7 | -0.06149 | 1.467 | 1.521e-50 | KCa'b'-ap2;KCa'b'-m;KCab-s;KCab-m;KCa'b'-ap1 |
| ser | 11 | 9 | 11 | 0 | 0.174 | 1.446 | 9.194e-48 | KCa'b'-ap2;KCa'b'-m;KCa'b'-ap1;KCab-p;KCg-d |
| da | 11 | 7 | 6 | 5 | 0.003279 | 1.423 | 1.299e-22 | KCa'b'-ap1;KCa'b'-ap2;KCa'b'-m;KCab-p;KCg-d |
| gaba | 11 | 7 | 5 | 6 | -0.009872 | 1.26 | 1.134e-20 | KCa'b'-ap2;KCa'b'-ap1;KCa'b'-m;KCab-c;KCg-d |

解释：`ser` 和 `glut` 仍是最值得围绕蘑菇体记忆侧化展开的两个 NT 轴；α′β′ 与 KCab-s 的 effect size 最高，适合作为下一轮 spike-level 和湿实验候选。

## 4. 行为读出敏感性

| cs_plus_side | metric | n_points | pearson_r | spearman_r | linear_slope_per_bias_unit | metric_range |
| --- | --- | --- | --- | --- | --- | --- |
| left | mean_path_length | 7 | -0.1106 | -0.2143 | -0.0454 | 0.6586 |
| left | mean_distance_to_cs_plus | 7 | 0.5486 | 0.4643 | 0.2178 | 0.6043 |
| right | mean_path_length | 7 | -0.385 | -0.2143 | -0.1672 | 0.5905 |
| left | mean_signed_final_y | 7 | 0.5328 | 0.4643 | 0.1386 | 0.4384 |
| right | mean_distance_to_cs_plus | 7 | 0.2203 | 0.4286 | 0.06202 | 0.3687 |
| left | mean_approach_margin | 7 | -0.2569 | -0.2857 | -0.06157 | 0.34 |

解释：当前几何下二分类选择率容易饱和，连续轨迹量更敏感。`mean_approach_margin`、`mean_signed_final_y` 和 `mean_path_length` 比单纯 CS+ choice rate 更适合作为仿真-行为桥接指标。

## 5. 强行为条件

| condition | lateral_memory_bias | cs_plus_choice_rate | mean_approach_margin | behavioral_side_asymmetry | mean_path_length |
| --- | --- | --- | --- | --- | --- |
| left_mb_glutamate_enriched | -0.219 | 1 | 5.869 | -0.07737 | 18.77 |
| mirror_reversal | -0.267 | 1 | 4.53 | -2.931 | 18.81 |
| control | 0 | 1 | 3.922 | 3.848 | 18.58 |
| right_mb_serotonin_enriched | 0.315 | 1 | 3.311 | -5.354 | 18.7 |
| symmetric_rescue | 0 | 1 | 2.986 | -5.887 | 18.77 |
| bilateral_memory_blunted | 0 | 0.5 | 2.6 | -5.383 | 18.17 |

解释：强侧化、镜像翻转和双侧钝化条件会改变接近 margin 与左右不对称轨迹，是比原始 control 更有信息量的行为对照。

## 6. 结构-功能-行为候选

| condition | functional_condition | lateral_memory_bias | mean_approach_margin | memory_axis_abs_mass | response_laterality_abs | min_empirical_fdr_q |
| --- | --- | --- | --- | --- | --- | --- |
| left_mb_glutamate_enriched | left_glutamate_kc_activate | -0.219 | 5.869 | 1.149 | -0.83 | 0.03816 |
| mirror_reversal | left_glutamate_activate_silence_right_serotonin | -0.267 | 4.53 | 1.149 | -0.8303 |  |
| right_mb_serotonin_enriched | right_serotonin_kc_activate | 0.315 | 3.311 | 1.108 | 0.8429 | 0.03816 |
| bilateral_memory_blunted | right_serotonin_activate_silence_left_glutamate | 0 | 2.6 | 1.108 | 0.8431 |  |
| amplified_right_axis | right_serotonin_kc_activate | 0.63 | 2.583 | 1.108 | 0.8429 | 0.03816 |
| amplified_left_axis | left_glutamate_kc_activate | -0.438 | 2.197 | 1.149 | -0.83 | 0.03816 |

解释：这个表优先筛选同时满足三点的候选：结构侧化强、传播进入 memory-axis、行为轨迹出现可观测改变。它比只看结构 p 值更接近可投稿的机制链。

## 7. 可发表的新假说

1. 蘑菇体侧化的关键不是整体左右体积差，而是 `serotonin-right` 与 `glutamate-left` 两条 NT-specific memory axes 的不对称耦合。
2. 行为层最敏感的表型不是二分类选择率，而是接近 CS+ 的 margin、最终 signed y 和路径长度；这些连续 readout 更适合连接结构组学和行为学。
3. 镜像翻转和双侧记忆钝化是最有价值的反事实对照：如果真实行为实验中也出现轨迹/接近策略改变，就能支持 causal lateralization surgery 的叙事。
4. 下一步应把 `right_serotonin_kc_activate` 与 `left_glutamate_kc_activate` 的 top MBON/DAN/APL/DPM target 转成遗传驱动线候选，做真实 odor-memory 左右侧操控验证。

## 8. 限制

这组结果仍是仿真预测，不等价于真实果蝇行为。当前强项是把结构侧化、功能传播和具身行为统一成可检验假说；投稿级证据还需要 spike-level validation、synapse-level uncertainty 和真实行为学实验。
