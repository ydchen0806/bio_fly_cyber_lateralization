# 记忆轴遗传操控候选靶点报告

更新时间：2026-04-26T12:02:19

## 1. 目标

本报告把四卡 propagation 的 top target、结构-功能-行为联动结果和蘑菇体记忆轴类别合并，筛出下一轮真实行为学或 spike-level validation 最值得优先操控的 MBON/DAN/APL/DPM/MBIN/OAN 候选。

## 2. 输出

- 候选 target 表：`/unify/ydchen/unidit/bio_fly/outputs/target_prioritization/memory_axis_candidate_targets.csv`
- target family 汇总：`/unify/ydchen/unidit/bio_fly/outputs/target_prioritization/memory_axis_target_family_summary.csv`
- priority 图：`/unify/ydchen/unidit/bio_fly/outputs/target_prioritization/Fig_memory_axis_target_priorities.png`

## 3. 最高优先级单神经元/类别候选

| condition | behavior_condition | root_id | priority_score | cell_class | cell_type | side | top_nt | target_direction | mean_approach_margin | min_empirical_fdr_q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| left_glutamate_kc_activate | left_mb_glutamate_enriched | 720575940620975696 | 0.3989 | MBIN | DPM | left | dopamine | activated | 5.869 | 0.03816 |
| left_glutamate_kc_activate | left_mb_glutamate_enriched | 720575940624547622 | 0.3899 | MBIN | APL | left | gaba | activated | 5.869 | 0.03816 |
| right_serotonin_kc_activate | right_mb_serotonin_enriched | 720575940613583001 | 0.3152 | MBIN | APL | right | gaba | activated | 3.311 | 0.03816 |
| left_glutamate_activate_silence_right_serotonin | mirror_reversal | 720575940620975696 | 0.3004 | MBIN | DPM | left | dopamine | activated | 4.53 |  |
| left_glutamate_activate_silence_right_serotonin | mirror_reversal | 720575940624547622 | 0.2936 | MBIN | APL | left | gaba | activated | 4.53 |  |
| right_serotonin_kc_activate | right_mb_serotonin_enriched | 720575940625934094 | 0.2678 | MBIN | DPM | right | dopamine | activated | 3.311 | 0.03816 |
| subtype_left_glutamate_enriched_kc_KCab-c_KCab |  | 720575940624547622 | 0.2545 | MBIN | APL | left | gaba | activated |  |  |
| subtype_right_serotonin_enriched_kc_KCab-c_KCab |  | 720575940613583001 | 0.2488 | MBIN | APL | right | gaba | activated |  |  |
| subtype_left_glutamate_enriched_kc_KCa_b_-ap1_KCapbp-ap1 |  | 720575940620975696 | 0.2487 | MBIN | DPM | left | dopamine | activated |  |  |
| right_serotonin_activate_silence_left_glutamate | bilateral_memory_blunted | 720575940613583001 | 0.2462 | MBIN | APL | right | gaba | activated | 2.6 |  |
| left_alpha_prime_beta_prime_glutamate_activate |  | 720575940620975696 | 0.24 | MBIN | DPM | left | dopamine | activated |  |  |
| subtype_left_glutamate_enriched_kc_KCa_b_-ap2_KCapbp-ap2 |  | 720575940620975696 | 0.237 | MBIN | DPM | left | dopamine | activated |  |  |
| subtype_right_serotonin_enriched_kc_KCa_b_-m_KCapbp-m |  | 720575940625934094 | 0.2351 | MBIN | DPM | right | dopamine | activated |  |  |
| subtype_left_glutamate_enriched_kc_KCa_b_-m_KCapbp-m |  | 720575940620975696 | 0.2343 | MBIN | DPM | left | dopamine | activated |  |  |
| subtype_right_serotonin_enriched_kc_KCg-m_KCg-m |  | 720575940613583001 | 0.2299 | MBIN | APL | right | gaba | activated |  |  |
| subtype_right_serotonin_enriched_kc_KCa_b_-ap2_KCapbp-ap2 |  | 720575940625934094 | 0.2188 | MBIN | DPM | right | dopamine | activated |  |  |

## 4. 候选 family

| condition | cell_class | cell_type | n_targets | mean_priority_score | max_abs_score | dominant_side | dominant_nt |
| --- | --- | --- | --- | --- | --- | --- | --- |
| left_glutamate_kc_activate | MBIN | DPM | 1 | 0.3989 | 0.1534 | left | dopamine |
| left_glutamate_kc_activate | MBIN | APL | 1 | 0.3899 | 0.1499 | left | gaba |
| right_serotonin_kc_activate | MBIN | APL | 1 | 0.3152 | 0.1486 | right | gaba |
| left_glutamate_activate_silence_right_serotonin | MBIN | DPM | 1 | 0.3004 | 0.1534 | left | dopamine |
| left_glutamate_activate_silence_right_serotonin | MBIN | APL | 1 | 0.2936 | 0.15 | left | gaba |
| right_serotonin_kc_activate | MBIN | DPM | 1 | 0.2678 | 0.1263 | right | dopamine |
| subtype_left_glutamate_enriched_kc_KCab-c_KCab | MBIN | APL | 1 | 0.2545 | 0.2036 | left | gaba |
| subtype_right_serotonin_enriched_kc_KCab-c_KCab | MBIN | APL | 1 | 0.2488 | 0.1991 | right | gaba |
| subtype_left_glutamate_enriched_kc_KCa_b_-ap1_KCapbp-ap1 | MBIN | DPM | 1 | 0.2487 | 0.199 | left | dopamine |
| right_serotonin_activate_silence_left_glutamate | MBIN | APL | 1 | 0.2462 | 0.1486 | right | gaba |
| left_alpha_prime_beta_prime_glutamate_activate | MBIN | DPM | 1 | 0.24 | 0.192 | left | dopamine |
| subtype_left_glutamate_enriched_kc_KCa_b_-ap2_KCapbp-ap2 | MBIN | DPM | 1 | 0.237 | 0.1896 | left | dopamine |
| subtype_right_serotonin_enriched_kc_KCa_b_-m_KCapbp-m | MBIN | DPM | 1 | 0.2351 | 0.1881 | right | dopamine |
| subtype_left_glutamate_enriched_kc_KCa_b_-m_KCapbp-m | MBIN | DPM | 1 | 0.2343 | 0.1875 | left | dopamine |
| subtype_right_serotonin_enriched_kc_KCg-m_KCg-m | MBIN | APL | 1 | 0.2299 | 0.1839 | right | gaba |
| subtype_right_serotonin_enriched_kc_KCa_b_-ap2_KCapbp-ap2 | MBIN | DPM | 1 | 0.2188 | 0.1751 | right | dopamine |

## 5. 生物学解释

1. `left_glutamate_kc_activate` 与 `left_mb_glutamate_enriched` 组合给出当前最强结构-功能-行为链条，优先观察 MBON、DPM/APL 和 MBIN readout 的左右行为影响。
2. `right_serotonin_kc_activate` 仍是核心对照轴，尤其适合与左 glutamate 轴做双向 rescue、mirror reversal 和单侧增强实验。
3. APL/DPM 类 target 虽然不一定是经典输出 MBON，但它们更像记忆状态调制和网络增益节点，适合做 spike-level validation 与药理/遗传扰动。
4. 真实实验建议先做行为轨迹连续指标：接近 CS+ 的 margin、路径长度、最终 signed y，再报告二分类 choice rate，避免饱和读数掩盖侧化效应。

## 6. 限制

这个表是仿真优先级，不是最终因果证明。候选 root_id 需要再映射到可用 split-GAL4、LexA、驱动线或 connectome annotation；真实论文中应配合湿实验、synapse-level uncertainty 和 spike-level 模型验证。
