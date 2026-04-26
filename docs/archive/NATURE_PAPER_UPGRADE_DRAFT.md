# 论文升级稿：A FlyWire-constrained cyber-fly simulation reveals neurotransmitter-specific mushroom-body lateralization

> 工作标题建议：**A connectome-constrained cyber-fly reveals a neurotransmitter-specific lateralized memory-control axis in the adult Drosophila mushroom body**

## Abstract 草稿

Brain lateralization is ubiquitous, yet its synapse-level and circuit-computational basis remains difficult to dissect experimentally because perturbing one hemisphere while preserving whole-brain context is technically challenging. Here we construct a FlyWire-constrained cyber-fly framework that links adult Drosophila connectomics, neurotransmitter-resolved mushroom-body inputs, GPU-accelerated whole-brain perturbation propagation, and embodied FlyGym behavioral rendering. Applying this framework to Kenyon cells, we identify a robust neurotransmitter-specific asymmetry: serotonin-like inputs are right-enriched across major KC subtypes, whereas glutamate-like inputs are left-biased, with the strongest effects in α′β′ memory-related subtypes. Four-GPU simulations across 534 perturbation and matched random-control experiments predict that lateralized KC ensembles differentially recruit MBON/DAN/MBIN/APL/DPM memory-axis targets. These results suggest a testable computational division of labor in which right α′β′ serotonin-enriched and left glutamate-biased ensembles act as asymmetric control points for memory-guided behavioral decisions.

## Significance Statement

传统果蝇行为学能证明“某基因/某神经元影响记忆”，但很难系统遍历全脑连接背景下的左右脑扰动。纯 AI 模拟可以大规模搜索，却缺乏生物结构约束。本工作把 FlyWire connectome、NT annotation、KC subtype、MBON/DAN/APL/DPM readout 和 FlyGym embodied behavior 放进同一个可复现仿真框架，提供了一个介于湿实验和黑箱 AI 之间的“结构约束赛博实验”范式。

## Results 1：结构组学发现 α′β′ KC 存在强 NT 偏侧化

主要 KC subtype 中 serotonin 输入方向一致右侧富集，glutamate 输入多数左侧偏置。最大效应集中在 α′β′ 与 KCab-s：

| hemibrain_type | cell_type | nt | left_n | right_n | right_laterality_index | cohens_d | fdr_q |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KCa'b'-ap2 | KCapbp-ap2 | glut | 138 | 160 | -0.2503 | -1.467 | 7.582e-26 |
| KCa'b'-m | KCapbp-m | glut | 164 | 174 | -0.2383 | -1.467 | 3.097e-28 |
| KCab-s | KCab | glut | 311 | 310 | -0.2743 | -1.457 | 1.521e-50 |
| KCa'b'-ap2 | KCapbp-ap2 | ser | 138 | 160 | 0.323 | 1.446 | 1.089e-25 |
| KCa'b'-ap1 | KCapbp-ap1 | da | 148 | 132 | 0.1426 | 1.423 | 1.299e-22 |
| KCa'b'-m | KCapbp-m | ser | 164 | 174 | 0.2737 | 1.348 | 5.765e-28 |
| KCa'b'-ap1 | KCapbp-ap1 | ser | 148 | 132 | 0.3484 | 1.338 | 2.125e-27 |
| KCa'b'-ap2 | KCapbp-ap2 | da | 138 | 160 | 0.1216 | 1.262 | 1.908e-20 |
| KCa'b'-ap2 | KCapbp-ap2 | gaba | 138 | 160 | -0.1232 | -1.26 | 1.134e-20 |
| KCa'b'-ap1 | KCapbp-ap1 | gaba | 148 | 132 | -0.109 | -1.108 | 3.106e-17 |

建议主文表述：

> The strongest asymmetries were not explained by a generic left-right cell-count imbalance, but by neurotransmitter-resolved input composition. α′β′ KCs showed a coordinated serotonin/right and glutamate-left organization, suggesting a lateralized modulatory substrate for memory gating.

## Results 2：四卡赛博果蝇仿真把结构侧化转化为功能预测

四卡运行信息：

- GPU：`cuda:0, cuda:1, cuda:2, cuda:3`。
- 扰动总数：`534`。
- wall time：`11.089 s`。
- 每组随机对照：`128` side/subtype-matched null controls。
- 输出：`/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_response_metrics.csv` 与 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv`。

核心功能读出：

| condition | memory_axis_abs_mass | mbon_abs_mass | dan_abs_mass | mbin_abs_mass | apl_abs_mass | dpm_abs_mass | response_laterality_abs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| subtype_left_glutamate_enriched_kc_KCa_b_-ap1_KCapbp-ap1 | 1.319 | 0.3835 | 0.234 | 0.3507 | 0.1512 | 0.1995 | -0.7704 |
| subtype_right_serotonin_enriched_kc_KCa_b_-ap1_KCapbp-ap1 | 1.276 | 0.4465 | 0.2383 | 0.2955 | 0.1338 | 0.1616 | 0.7373 |
| left_alpha_prime_beta_prime_glutamate_activate | 1.271 | 0.3677 | 0.2051 | 0.349 | 0.1566 | 0.1924 | -0.7908 |
| subtype_left_glutamate_enriched_kc_KCa_b_-ap2_KCapbp-ap2 | 1.251 | 0.3913 | 0.1876 | 0.336 | 0.146 | 0.19 | -0.787 |
| subtype_left_glutamate_enriched_kc_KCa_b_-m_KCapbp-m | 1.248 | 0.3356 | 0.1952 | 0.3587 | 0.1708 | 0.1879 | -0.8082 |
| right_alpha_prime_beta_prime_serotonin_activate | 1.234 | 0.4011 | 0.2015 | 0.3158 | 0.1399 | 0.1758 | 0.7746 |
| subtype_right_serotonin_enriched_kc_KCa_b_-ap2_KCapbp-ap2 | 1.223 | 0.4128 | 0.2009 | 0.3045 | 0.1285 | 0.1759 | 0.7699 |
| subtype_right_serotonin_enriched_kc_KCa_b_-m_KCapbp-m | 1.208 | 0.348 | 0.1676 | 0.346 | 0.1572 | 0.1888 | 0.806 |
| subtype_right_serotonin_enriched_kc_KCg-m_KCg-m | 1.16 | 0.4071 | 0.1544 | 0.2991 | 0.1859 | 0.1132 | 0.8232 |
| left_glutamate_activate_silence_right_serotonin | 1.149 | 0.3496 | 0.1908 | 0.3044 | 0.1506 | 0.1538 | -0.8303 |
| left_glutamate_kc_activate | 1.149 | 0.3495 | 0.1908 | 0.3043 | 0.1506 | 0.1537 | -0.83 |
| right_serotonin_activate_silence_left_glutamate | 1.108 | 0.3706 | 0.1862 | 0.2754 | 0.1488 | 0.1266 | 0.8431 |

## Results 3：matched-random 消融支持侧化 ensemble 的非随机功能偏置

显著性结果：

| actual_condition | null_family | metric | actual_value | null_mean | effect_z | empirical_p_two_sided | fdr_q |
| --- | --- | --- | --- | --- | --- | --- | --- |
| right_serotonin_kc_activate | null_right_kc_random | dan_abs_mass | 0.1862 | 0.1767 | 4.236 | 0.0155 | 0.03816 |
| right_serotonin_kc_activate | null_right_kc_random | response_laterality_abs | 0.8429 | 0.8509 | -2.708 | 0.0155 | 0.03816 |
| right_serotonin_kc_activate | null_right_kc_random | dpm_abs_mass | 0.1266 | 0.116 | 4.019 | 0.0155 | 0.03816 |
| right_serotonin_kc_activate | null_right_kc_random | apl_abs_mass | 0.1488 | 0.1584 | -4.043 | 0.0155 | 0.03816 |
| right_serotonin_kc_activate | null_right_kc_random | max_abs_target_score | 0.1486 | 0.1576 | -3.827 | 0.0155 | 0.03816 |
| left_glutamate_kc_activate | null_left_kc_random | dan_abs_mass | 0.1908 | 0.1718 | 7.188 | 0.0155 | 0.03816 |
| left_glutamate_kc_activate | null_left_kc_random | mbon_abs_mass | 0.3495 | 0.3656 | -5.355 | 0.0155 | 0.03816 |
| left_glutamate_kc_activate | null_left_kc_random | memory_axis_abs_mass | 1.149 | 1.128 | 3.081 | 0.0155 | 0.03816 |
| left_glutamate_kc_activate | null_left_kc_random | apl_abs_mass | 0.1506 | 0.1596 | -4.011 | 0.0155 | 0.03816 |
| left_glutamate_kc_activate | null_left_kc_random | dpm_abs_mass | 0.1537 | 0.1355 | 7.184 | 0.0155 | 0.03816 |
| left_glutamate_kc_activate | null_left_kc_random | response_laterality_abs | -0.83 | -0.8465 | 6.991 | 0.0155 | 0.03816 |
| left_glutamate_kc_activate | null_left_kc_random | mbin_abs_mass | 0.3043 | 0.2951 | 2.923 | 0.0155 | 0.03816 |
| left_glutamate_kc_activate | null_left_kc_random | max_abs_target_score | 0.1534 | 0.1593 | -2.653 | 0.0155 | 0.03816 |
| left_alpha_prime_beta_prime_glutamate_activate | null_left_alpha_random | max_abs_target_score | 0.192 | 0.1881 | 1.684 | 0.06202 | 0.1417 |
| left_alpha_prime_beta_prime_glutamate_activate | null_left_alpha_random | dpm_abs_mass | 0.1924 | 0.1886 | 1.662 | 0.07752 | 0.1654 |
| right_alpha_prime_beta_prime_serotonin_activate | null_right_alpha_random | mbon_abs_mass | 0.4011 | 0.3935 | 1.537 | 0.09302 | 0.186 |

建议主文表述：

> Relative to side-matched random KC ensembles, the left glutamate-biased ensemble produced stronger memory-axis recruitment and shifted lateralized response mass toward the left hemisphere, whereas the right serotonin-enriched ensemble selectively enhanced DAN/DPM-related readouts while reducing APL-like components. These effects survived empirical FDR correction across readout metrics in the four-GPU simulation suite.

## Results 4：机制模型

机制示意图建议：

1. `FlyWire v783` 提供全脑有向连接结构。
2. KC 输入 NT fraction 揭示 serotonin/right 与 glutamate/left 的结构偏侧化。
3. GPU sparse propagation 将 KC ensemble activation 转化为 whole-brain response field。
4. MBON/DAN/MBIN/APL/DPM readout 量化 memory-axis recruitment。
5. FlyGym 把 readout 映射到 odor-choice trajectory，生成可解释行为预测。

对应图件：

- `outputs/four_card_suite/figures/Fig1_cyber_fly_pipeline_mechanism.png`
- `outputs/four_card_suite/figures/Fig2_functional_metric_heatmap.png`
- `outputs/four_card_suite/figures/Fig3_empirical_null_significance.png`
- `outputs/four_card_suite/figures/Fig4_memory_axis_null_distributions.png`
- `outputs/four_card_suite/figures/Fig5_stepwise_side_class_response.png`
- `outputs/four_card_suite/videos/cyber_fly_lateralized_memory_axis.mp4`

## Methods：赛博果蝇仿真体系科学合理性

### Connectome-constrained perturbation

模型不从随机神经网络开始，而是固定 FlyWire/Shiu v783 全脑连接矩阵。扰动 seed 来自真实 KC root_id，且按照 hemisphere、KC subtype 和 NT fraction 选择。这样保留了真实连接组约束、细胞类型标签和左右脑结构边界。

### Neurotransmitter-informed lateralization

每条输入边的 `gaba_avg/ach_avg/glut_avg/oct_avg/ser_avg/da_avg` 与 synapse count 相乘，得到每个 KC 的 NT-specific input fraction。统计上使用 Mann–Whitney、Welch、bootstrap CI、Cohen's d、Cliff's delta、FDR 和 direction binomial test。

### Four-GPU whole-brain propagation

四个进程分别在 `cuda:0..3` 加载 sparse adjacency matrix，把 534 个 perturbation specs 分片运行。每个 perturbation 保留每步 absolute response 最大的 top active nodes，输出 whole-brain response field、side/class/NT readout 和 top targets。

### Biological controls

随机对照不是任意随机节点，而是 side/subtype matched KC null controls。这样能控制左右脑、KC 类别和 seed 数量造成的偏差，更接近可发表的消融实验设计。

## Figure Legends 草稿

**Figure 1 | Connectome-constrained cyber-fly framework.** FlyWire v783 connectome and neurotransmitter-resolved KC inputs are integrated with four-GPU sparse whole-brain propagation and FlyGym embodied rendering to test lateralized memory-control hypotheses.

**Figure 2 | Neurotransmitter-specific KC input lateralization.** Heatmap/forest/volcano plots show right-enriched serotonin-like inputs and left-biased glutamate-like inputs, strongest in α′β′ KCs.

**Figure 3 | Functional signatures of lateralized KC ensembles.** Whole-brain propagation from lateralized KC seeds reveals distinct MBON/DAN/MBIN/APL/DPM memory-axis recruitment patterns.

**Figure 4 | Matched-random ablation controls.** Side/subtype-matched random KC ensembles provide empirical null distributions for memory-axis and lateralized response metrics.

**Figure 5 | Dynamic recruitment of the memory axis.** Propagation videos visualize stepwise recruitment of left/right MBON/DAN/MBIN/Kenyon-cell populations from right α′β′ serotonin and left α′β′ glutamate seeds.

## Limitations and Required Wet-Lab Validation

当前结果应被严格表述为 **connectome-constrained simulation-derived prediction**，不是最终因果证明。下一步必须补：

1. `flywire_synapses_783.feather` 的 synapse-level NT/spatial uncertainty validation。
2. Brian2/LIF spike-level 动力学对核心 α′β′ 条件复核。
3. 真果蝇 odor-memory 行为：左右 odor geometry、短期/长期记忆、遗传/药理扰动和 rescue。
4. 将 simulation prediction 与真实行为效应量做 causal mediation / Bayesian model comparison。

## 可投稿叙事定位

保守定位：Nature Communications / Nature Computational Science 风格的 computational neurobiology resource + biological prediction。  
更强定位：若补齐 synapse-level validation、spiking dynamics 和真实行为实验，可向 Nature Neuroscience / Nature Methods / Nature Machine Intelligence 方向组织。
