# 2026-04-29 会议反馈定向实验报告

本轮目标是把生物老师会议反馈转化为可运行的计算实验和可落地的湿实验建议。核心变化是：不再只展示 OCT/MCH 视频，而是把结论拆成 `5-HT 右偏`、`Glu 左偏`、`DPM 光遗传功能读出`、`GRASP 结构验证` 和 `群体 T-maze 行为指标` 五条可验证线。

## 文献和实验依据

| topic | source | url | use_in_project |
| --- | --- | --- | --- |
| DPM/5-HT memory trace | Yu et al., Cell 2006 | https://doi.org/10.1016/j.cell.2005.09.037 | 支持 DPM 神经元和嗅觉记忆时间窗、branch-specific memory trace 相关；因此新增 DPM 光遗传协议扫描。 |
| DPM serotonin and ARM | Lee et al., Neuron 2011 | https://pubmed.ncbi.nlm.nih.gov/21808003/ | 支持 DPM 释放 5-HT 到蘑菇体并影响 anesthesia-resistant memory；因此把 5-HT 右偏解释为记忆巩固/调节轴候选。 |
| GRASP synaptic validation | Feinberg et al., Neuron 2008; Drosophila transsynaptic tools review | https://pmc.ncbi.nlm.nih.gov/articles/PMC8524129/ | 支持用 split-GFP/GRASP 作为结构连接验证；因此新增 GRASP 靶点优先级表。 |
| OCT/MCH T-maze assay | Drosophila adult olfactory shock learning protocol | https://pmc.ncbi.nlm.nih.gov/articles/PMC4672959/ | 支持 3-octanol 和 4-methylcyclohexanol 作为标准嗅觉学习气味；因此行为预测转成 T-maze 群体 choice index。 |
| MB lateralized memory | Pascual and Preat, Science 2004 | https://doi.org/10.1126/science.1100621 | 支持果蝇记忆与左右不对称结构相关；因此保留偏侧化研究主线，但明确单脑 FlyWire 的边界。 |

## 1. 5-HT 与 Glu 的分拆验证

输出表：`/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/double_dissociation_metrics.csv`

核心结果如下。`right_serotonin_abs_z` 和 `left_glutamate_abs_z` 比较的是相对随机对照的效应强度；`abs_z_difference_5ht_minus_glu` 为正表示 5-HT 右侧 seed 的绝对效应更大，为负表示 Glu 左侧 seed 的绝对效应更大。

| metric | left_glutamate_kc_activate | right_serotonin_kc_activate | axis_group | serotonin_minus_glutamate_z | right_serotonin_abs_z | left_glutamate_abs_z | abs_z_difference_5ht_minus_glu | dominant_prediction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| response_laterality_abs | 6.991 | -2.708 | lateral_readout | -9.699 | 2.708 | 6.991 | -4.283 | left_Glu_larger_abs_effect |
| mbin_abs_mass | 2.923 | 0.3092 | memory_output_axis | -2.614 | 0.3092 | 2.923 | -2.614 | left_Glu_larger_abs_effect |
| mbon_abs_mass | -5.355 | -1.793 | memory_output_axis | 3.562 | 1.793 | 5.355 | -3.562 | left_Glu_larger_abs_effect |
| memory_axis_abs_mass | 3.081 | 0.7598 | memory_output_axis | -2.321 | 0.7598 | 3.081 | -2.321 | left_Glu_larger_abs_effect |
| apl_abs_mass | -4.011 | -4.043 | modulatory_feedback_axis | -0.03134 | 4.043 | 4.011 | 0.03134 | similar_abs_effect |
| dan_abs_mass | 7.188 | 4.236 | modulatory_feedback_axis | -2.952 | 4.236 | 7.188 | -2.952 | left_Glu_larger_abs_effect |
| dpm_abs_mass | 7.184 | 4.019 | modulatory_feedback_axis | -3.165 | 4.019 | 7.184 | -3.165 | left_Glu_larger_abs_effect |
| max_abs_target_score | -2.653 | -3.827 | target_peak | -1.174 | 3.827 | 2.653 | 1.174 | right_5HT_larger_abs_effect |

解释：右侧 5-HT seed 在 DAN/DPM/APL 等调节/反馈读出上达到显著，但本轮 `abs(z)` 比较显示左侧 Glu seed 对 memory axis、MBON/MBIN、DAN/DPM 和左右响应的总体扰动更强。因此当前更严谨的表述不是“两个轴已经完全双重分离”，而是“Glu-left 是更强的广谱 memory-output 扰动，5-HT-right 是 DPM/5-HT 光遗传和记忆巩固时间窗优先验证轴”。这仍然保留会议中提出的分拆验证逻辑，但避免把仿真结果过度写成已完成的双重分离。

## 2. DPM 光遗传协议扫描

GPU 约束：本轮 DPM 传播只使用 `cuda:0` 和 `cuda:1`。输出表：`/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/dpm_gpu_propagation_summary.csv`。

| condition | device | n_seed_neurons | n_active_neurons | absolute_mass | left_abs_mass | right_abs_mass | right_laterality_index | top_cell_classes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| left_DPM_opto | cuda:0 | 1 | 6280 | 1.283 | 1.176 | 0.1068 | -0.8334 | Kenyon_Cell:0.7370; unannotated:0.1342; MBIN:0.1119; MBON:0.1107; DAN:0.0571 |
| right_DPM_opto | cuda:1 | 1 | 6386 | 1.403 | 0.1351 | 1.267 | 0.8073 | Kenyon_Cell:0.7507; unannotated:0.1798; MBON:0.1480; MBIN:0.0965; DAN:0.0765 |
| bilateral_DPM_opto | cuda:0 | 2 | 6378 | 1.264 | 0.8107 | 0.4528 | -0.2832 | Kenyon_Cell:0.7788; MBON:0.1191; MBIN:0.1031; unannotated:0.0850; DAN:0.0611 |

协议预测表：`/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/dpm_optogenetic_protocol_predictions.csv`。

最大预测 brain-registered 5-HT release LI 约为 `0.997`。如果是真实脑侧偏侧化，水平旋转 180 度后，经过脑侧坐标配准，右偏信号应保持右偏；如果是成像角度伪影，图像坐标中的左右符号会翻转。这直接对应会议提出的旋转果蝇控制实验。

## 3. 群体行为可观测指标

输出表：`/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/group_behavior_predictions.csv`。

| assay | condition | predicted_choice_rate | predicted_choice_index | predicted_approach_margin | dominant_readout | experimental_observable |
| --- | --- | --- | --- | --- | --- | --- |
| OCT/MCH T-maze group choice | wild_type_lateralization | 0.86 | 0.72 | 0.2654 | normal valence memory | 群体 T-maze OCT/MCH choice index |
| OCT/MCH T-maze group choice | serotonin_right_bias_removed | 0.7976 | 0.5952 | 0.2309 | delayed consolidation / DPM-DAN modulation | 训练后 30-60 min 的 delayed memory choice index、DPM/MB calcium readout |
| OCT/MCH T-maze group choice | glutamate_left_bias_removed | 0.7832 | 0.5663 | 0.2208 | memory-axis / MBON output gain | acquisition/retrieval choice index、CS+ approach margin、群体分布变宽 |
| OCT/MCH T-maze group choice | both_biases_blunted | 0.68 | 0.36 | 0.1645 | reduced learning confidence | 几百只果蝇群体选择率下降；不要求单只果蝇成像后继续行为 |

建议行为学读出优先级：

1. 群体 T-maze OCT/MCH choice index：最贴近现有实验条件，几百只果蝇即可统计。
2. delayed memory window：优先测试训练后 30-60 min，因为 DPM/5-HT 文献支持 delayed/intermediate memory trace。
3. acquisition/retrieval 方向：用于区分 Glu-left memory-axis/MBON 输出假说。
4. 不强求同一只果蝇先成像再行为，因为会议已明确脑成像后果蝇不可继续行为。

## 4. GRASP 结构验证靶点

输出表：`/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/tables/grasp_priority_targets.csv`。

| priority | grasp_pair | side | target_subtype | reason | n_seed_neurons | expected_signal |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | DPM/5-HT input -> right KCa'b' | right | KCa'b'-ap1 | 5-HT right enrichment strongest in alpha' beta' memory-consolidation subtypes | 27 | right GRASP signal > left after brain-side registration |
| 1 | DPM/5-HT input -> right KCa'b' | right | KCa'b'-ap2 | 5-HT right enrichment strongest in alpha' beta' memory-consolidation subtypes | 30 | right GRASP signal > left after brain-side registration |
| 1 | DPM/5-HT input -> right KCa'b' | right | KCa'b'-m | 5-HT right enrichment strongest in alpha' beta' memory-consolidation subtypes | 30 | right GRASP signal > left after brain-side registration |
| 2 | putative glutamatergic input -> left KCa'b' | left | KCa'b'-ap1 | Glu left bias provides opposite-direction positive control | 30 | left GRASP signal > right |
| 2 | putative glutamatergic input -> left KCa'b' | left | KCa'b'-ap2 | Glu left bias provides opposite-direction positive control | 28 | left GRASP signal > right |
| 2 | putative glutamatergic input -> left KCa'b' | left | KCa'b'-m | Glu left bias provides opposite-direction positive control | 30 | left GRASP signal > right |

GRASP 是这条线的硬结构验证：如果右侧 DPM/5-HT 到 alpha' beta' KC 的结构信号、左侧 Glu 输入到 alpha' beta' KC 的相反方向信号能被直接验证，后续功能和行为结果才有资格作为强佐证，而不是替代结构证据。

## 5. 新增图表

- 双重分离热图：`/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/figures/Fig_meeting_double_dissociation_heatmap.png`
- DPM 光遗传协议预测：`/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/figures/Fig_dpm_optogenetic_protocol_predictions.png`
- 群体行为预测：`/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/figures/Fig_group_behavior_observable_predictions.png`
- 验证逻辑图：`/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429/figures/Fig_validation_logic_after_meeting.png`

这些图已复制到 `/unify/ydchen/unidit/bio_fly/paper/figures` 和 `/unify/ydchen/unidit/bio_fly/ppt/figures`，可直接进入 paper 和 PPT。

## 6. 当前结论更新

可以更明确地说：

1. 5-HT 右偏和 Glu 左偏应作为两条候选机制轴，而不是合成一个笼统的“偏侧化强弱”；但当前仿真显示 Glu-left 的广谱扰动更强，5-HT-right 更适合进入 DPM 光遗传功能验证。
2. DPM 光遗传实验可先验证功能 readout 稳定性，并用 180 度旋转控制排除成像角度伪影。
3. GRASP 是结构验证硬红线；行为和功能结果只能作为佐证，不能替代结构证据。
4. 群体 T-maze 可验证预测方向，但不能证明单只果蝇的偏侧化程度和行为一一对应。
5. 下一轮最值得做的是：右侧 DPM/5-HT 光遗传协议扫描 + 左侧 Glu 结构/功能 positive control + delayed OCT/MCH 群体 choice index。
