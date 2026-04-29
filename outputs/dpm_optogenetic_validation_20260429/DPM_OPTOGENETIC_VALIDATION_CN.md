# DPM 光遗传仿真验证方案：从 5-HT 释放 pattern 到群体行为

本报告回答当前最核心的问题：能否通过仿真脑先模拟光遗传激活 DPM neuron，预测偏侧化果蝇的激活 pattern 和 5-HT 释放 pattern，并把结果转成湿实验方便验证的设计。

## 结论先行

1. **成像证明和行为证明应分开做。** 5-HT 侧化成像会破坏或强扰动果蝇，不能要求同一只果蝇继续做行为；因此本项目把“释放 pattern 成像验证”和“群体行为调节验证”拆成两条链。
2. **DPM 光遗传优先用红光工具。** 文献支持 ReaChR/CsChrimson 在成人果蝇行为中用红光激活；本仿真把 617/627 nm 设为优先协议，470 nm 只作为蓝光 positive/control 或校准，不作为主行为实验。
3. **最关键的可验证 readout 是 brain-registered laterality index。** 如果是真实偏侧化，水平旋转果蝇 180 度后，按脑侧配准的左右符号应保持；如果是成像角度伪影，图像坐标符号会翻转。
4. **行为验证不需要直接测每只果蝇的 NT 侧化。** 使用几百只果蝇群体 T-maze，在训练或测试窗口给 DPM 红光刺激，看 OCT/MCH choice index 是否按仿真方向移动。

## 文献依据

- DPM 5-HT 与蘑菇体 ARM/记忆相关：Lee et al., Neuron 2011，PubMed: https://pubmed.ncbi.nlm.nih.gov/21808003/
- 5-HT sensor 可报告 DPM/KC 相关 5-HT dynamics：Wan et al., Nature Neuroscience 2021，PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC8544647/
- ReaChR 成人果蝇红光光遗传行为：Inagaki et al., Nature Methods 2014，PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC4151318/
- DPM appetitive/aversive memory trace 与时间窗：Yu et al. / follow-up memory trace work，PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3396741/

## 1. 仿真生成的数据

- 光遗传协议库：`/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_optogenetic_protocol_library.csv`
- DPM 下游 ROI readout：`/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_downstream_roi_summary.csv`
- 5-HT 释放时间曲线：`/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_5ht_release_timecourses.csv`
- 释放模式摘要：`/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_5ht_release_pattern_summary.csv`
- 行为调节预测：`/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_optogenetic_behavior_predictions.csv`
- 湿实验推荐表：`/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_wetlab_protocol_recommendations.csv`
- 机制视频：`/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/videos/dpm_optogenetic_release_prediction.mp4`

## 2. DPM 传播到哪些下游区域

GPU 传播只使用 `cuda:0` 和 `cuda:1`。DPM seed 的传播摘要：

| condition | device | n_seed_neurons | n_active_neurons | absolute_mass | left_abs_mass | right_abs_mass | right_laterality_index | top_cell_classes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| left_DPM_opto | cuda:0 | 1 | 6280 | 1.283 | 1.176 | 0.1068 | -0.8334 | Kenyon_Cell:0.7370; unannotated:0.1342; MBIN:0.1119; MBON:0.1107; DAN:0.0571 |
| right_DPM_opto | cuda:1 | 1 | 6386 | 1.403 | 0.1351 | 1.267 | 0.8073 | Kenyon_Cell:0.7507; unannotated:0.1798; MBON:0.1480; MBIN:0.0965; DAN:0.0765 |
| bilateral_DPM_opto | cuda:0 | 2 | 6378 | 1.264 | 0.8107 | 0.4528 | -0.2832 | Kenyon_Cell:0.7788; MBON:0.1191; MBIN:0.1031; unannotated:0.0850; DAN:0.0611 |

下游 ROI 总响应最高的条目：

| condition | roi | abs_mass |
| --- | --- | --- |
| left_DPM_opto | KC_all | 1.45 |
| right_DPM_opto | KC_all | 1.405 |
| bilateral_DPM_opto | KC_all | 1.396 |
| bilateral_DPM_opto | KCa'b'_memory_consolidation | 0.4527 |
| right_DPM_opto | KCa'b'_memory_consolidation | 0.4485 |
| left_DPM_opto | KCa'b'_memory_consolidation | 0.4461 |
| right_DPM_opto | other | 0.3784 |
| left_DPM_opto | MBON_output | 0.3471 |
| right_DPM_opto | MBON_output | 0.3428 |
| bilateral_DPM_opto | MBON_output | 0.3373 |
| left_DPM_opto | other | 0.296 |
| bilateral_DPM_opto | other | 0.2187 |
| left_DPM_opto | APL_feedback | 0.1799 |
| bilateral_DPM_opto | APL_feedback | 0.1658 |
| left_DPM_opto | DAN_teaching | 0.1624 |
| right_DPM_opto | DAN_teaching | 0.1587 |

解释：DPM 激活首先应读出到 KC/蘑菇体相关区域，同时保留 MBON/DAN/APL/DPM 和部分 DN/motor-exit 的传播读数。湿实验不需要一次测所有下游，优先测 alpha' beta' KC/MB compartment 的 5-HT sensor 或钙响应。

## 3. 释放 pattern 预测

释放曲线模型不是把仿真当成真实化学动力学，而是把光遗传刺激参数转成可比较的预测变量：

- `left_release_au` / `right_release_au`：左右半脑预测 5-HT 释放强度，单位为 arbitrary unit。
- `brain_registered_release_li`：按脑侧注册后的左右释放偏侧指数，正值表示右偏。
- `image_li_after_180deg_rotation`：模拟水平旋转 180 度后，如果只看图像坐标会看到的偏侧指数。
- `fly_model=lateralized_fly`：真实偏侧化假设。
- `fly_model=symmetric_control`：无偏侧对照。
- `fly_model=camera_artifact_control`：成像角度伪影对照。

释放模式最高优先级协议：

| protocol_id | fly_model | opsin | wavelength_nm | frequency_hz | pulse_width_ms | train_duration_s | irradiance_mw_mm2 | peak_total_release_au | release_auc_au_s | peak_brain_registered_li | mean_rotation_discrepancy | wetlab_priority_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW | lateralized_fly | CsChrimson_red | 617 | 40 | 20 | 5 | 0.1 | 1.771 | 11.65 | 0.8022 | 0 | 4.21 |
| CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW | camera_artifact_control | CsChrimson_red | 617 | 40 | 20 | 5 | 0.1 | 1.771 | 11.65 | 0.8022 | -1.229 | 4.21 |
| ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW | lateralized_fly | ReaChR_red | 627 | 40 | 20 | 5 | 0.1 | 1.771 | 11.65 | 0.8022 | 0 | 4.21 |
| ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW | camera_artifact_control | ReaChR_red | 627 | 40 | 20 | 5 | 0.1 | 1.771 | 11.65 | 0.8022 | -1.229 | 4.21 |
| CsChrimson_red_617nm_40Hz_20ms_0.5s_1.0mW | camera_artifact_control | CsChrimson_red | 617 | 40 | 20 | 0.5 | 1 | 1.661 | 3.564 | 0.801 | -0.8223 | 4.208 |
| ReaChR_red_627nm_40Hz_20ms_0.5s_1.0mW | camera_artifact_control | ReaChR_red | 627 | 40 | 20 | 0.5 | 1 | 1.661 | 3.564 | 0.801 | -0.8223 | 4.208 |
| ReaChR_red_627nm_40Hz_20ms_0.5s_1.0mW | lateralized_fly | ReaChR_red | 627 | 40 | 20 | 0.5 | 1 | 1.661 | 3.564 | 0.801 | 0 | 4.208 |
| CsChrimson_red_617nm_40Hz_20ms_0.5s_1.0mW | lateralized_fly | CsChrimson_red | 617 | 40 | 20 | 0.5 | 1 | 1.661 | 3.564 | 0.801 | 0 | 4.208 |
| ReaChR_red_627nm_20Hz_20ms_1.0s_1.0mW | camera_artifact_control | ReaChR_red | 627 | 20 | 20 | 1 | 1 | 1.764 | 4.614 | 0.8021 | -0.8862 | 4.168 |
| CsChrimson_red_617nm_20Hz_20ms_1.0s_1.0mW | camera_artifact_control | CsChrimson_red | 617 | 20 | 20 | 1 | 1 | 1.764 | 4.614 | 0.8021 | -0.8862 | 4.168 |

## 4. 湿实验可直接采用的成像协议

| priority | experiment | genetic_design | protocol_id | light | primary_readout | critical_control | expected_result | why_feasible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | DPM optogenetic imaging | DPM-driver > red-shifted opsin; KC or MB compartment expresses 5-HT sensor or GCaMP | CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW | 617 nm, 40 Hz, 20 ms pulses, 5.0 s, 0.1 mW/mm2 | left/right 5-HT sensor dF/F or calcium response in alpha' beta' MB compartments | rotate fly 180deg and register by brain side; no-opsin and retinal-minus controls | lateralized flies preserve brain-side LI after rotation; imaging artifact flips in image coordinates | same fly only needs imaging; no post-imaging behaviour required |
| 2 | DPM optogenetic imaging | DPM-driver > red-shifted opsin; KC or MB compartment expresses 5-HT sensor or GCaMP | ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW | 627 nm, 40 Hz, 20 ms pulses, 5.0 s, 0.1 mW/mm2 | left/right 5-HT sensor dF/F or calcium response in alpha' beta' MB compartments | rotate fly 180deg and register by brain side; no-opsin and retinal-minus controls | lateralized flies preserve brain-side LI after rotation; imaging artifact flips in image coordinates | same fly only needs imaging; no post-imaging behaviour required |
| 3 | DPM optogenetic imaging | DPM-driver > red-shifted opsin; KC or MB compartment expresses 5-HT sensor or GCaMP | ReaChR_red_627nm_40Hz_20ms_0.5s_1.0mW | 627 nm, 40 Hz, 20 ms pulses, 0.5 s, 1.0 mW/mm2 | left/right 5-HT sensor dF/F or calcium response in alpha' beta' MB compartments | rotate fly 180deg and register by brain side; no-opsin and retinal-minus controls | lateralized flies preserve brain-side LI after rotation; imaging artifact flips in image coordinates | same fly only needs imaging; no post-imaging behaviour required |
| 4 | DPM optogenetic imaging | DPM-driver > red-shifted opsin; KC or MB compartment expresses 5-HT sensor or GCaMP | CsChrimson_red_617nm_40Hz_20ms_0.5s_1.0mW | 617 nm, 40 Hz, 20 ms pulses, 0.5 s, 1.0 mW/mm2 | left/right 5-HT sensor dF/F or calcium response in alpha' beta' MB compartments | rotate fly 180deg and register by brain side; no-opsin and retinal-minus controls | lateralized flies preserve brain-side LI after rotation; imaging artifact flips in image coordinates | same fly only needs imaging; no post-imaging behaviour required |
| 5 | DPM optogenetic imaging | DPM-driver > red-shifted opsin; KC or MB compartment expresses 5-HT sensor or GCaMP | ReaChR_red_627nm_20Hz_20ms_1.0s_1.0mW | 627 nm, 20 Hz, 20 ms pulses, 1.0 s, 1.0 mW/mm2 | left/right 5-HT sensor dF/F or calcium response in alpha' beta' MB compartments | rotate fly 180deg and register by brain side; no-opsin and retinal-minus controls | lateralized flies preserve brain-side LI after rotation; imaging artifact flips in image coordinates | same fly only needs imaging; no post-imaging behaviour required |

建议实验顺序：

1. 先做 `DPM-driver > CsChrimson/ReaChR`，KC 或 MB compartment 表达 5-HT sensor 或 GCaMP。
2. 使用 617/627 nm 红光，低强度开始，按表中协议做频率、脉宽、时长扫描。
3. 每只果蝇做原始方向和水平旋转 180 度条件，分析时用脑侧而不是相机坐标注册。
4. 对照包括 no-opsin、retinal-minus、red-light-only、左右 ROI 注册盲法。
5. 主指标预注册为 release LI、peak dF/F、AUC、响应半衰期，而不是只看单张图。

## 5. 行为是否能被光遗传调节

行为预测表不是声称已证明真实行为因果，而是给群体实验预估效应方向：

| protocol_id | assay_condition | opsin | wavelength_nm | frequency_hz | pulse_width_ms | train_duration_s | irradiance_mw_mm2 | base_expected_choice_rate | predicted_expected_choice_rate_with_DPM_opto | predicted_choice_index_delta | predicted_approach_margin_with_DPM_opto | behavioral_interpretation | wetlab_observable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW | oct_shock_aversive_wt | CsChrimson_red | 617 | 40 | 20 | 5 | 0.1 | 0.86 | 0.8276 | -0.06472 | -0.2365 | test-phase activation may weaken aversive expression or increase state noise | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW | oct_sucrose_appetitive_wt | CsChrimson_red | 617 | 40 | 20 | 5 | 0.1 | 0.86 | 0.8988 | 0.07766 | 0.2757 | reward-memory expression or delayed consolidation support | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW | weak_oct_strong_mch_conflict | CsChrimson_red | 617 | 40 | 20 | 5 | 0.1 | 0.88 | 0.9319 | 0.1038 | 0.2787 | best behavioural sensitivity: weak CS+ versus strong CS- conflict | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW | oct_shock_aversive_wt | ReaChR_red | 627 | 40 | 20 | 5 | 0.1 | 0.86 | 0.8276 | -0.06472 | -0.2365 | test-phase activation may weaken aversive expression or increase state noise | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW | oct_sucrose_appetitive_wt | ReaChR_red | 627 | 40 | 20 | 5 | 0.1 | 0.86 | 0.8988 | 0.07766 | 0.2757 | reward-memory expression or delayed consolidation support | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW | weak_oct_strong_mch_conflict | ReaChR_red | 627 | 40 | 20 | 5 | 0.1 | 0.88 | 0.9319 | 0.1038 | 0.2787 | best behavioural sensitivity: weak CS+ versus strong CS- conflict | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| ReaChR_red_627nm_40Hz_20ms_0.5s_1.0mW | oct_shock_aversive_wt | ReaChR_red | 627 | 40 | 20 | 0.5 | 1 | 0.86 | 0.8501 | -0.0198 | -0.242 | test-phase activation may weaken aversive expression or increase state noise | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| ReaChR_red_627nm_40Hz_20ms_0.5s_1.0mW | oct_sucrose_appetitive_wt | ReaChR_red | 627 | 40 | 20 | 0.5 | 1 | 0.86 | 0.8719 | 0.02376 | 0.2685 | reward-memory expression or delayed consolidation support | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| ReaChR_red_627nm_40Hz_20ms_0.5s_1.0mW | weak_oct_strong_mch_conflict | ReaChR_red | 627 | 40 | 20 | 0.5 | 1 | 0.88 | 0.8959 | 0.03172 | 0.2691 | best behavioural sensitivity: weak CS+ versus strong CS- conflict | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| CsChrimson_red_617nm_40Hz_20ms_0.5s_1.0mW | oct_shock_aversive_wt | CsChrimson_red | 617 | 40 | 20 | 0.5 | 1 | 0.86 | 0.8501 | -0.0198 | -0.242 | test-phase activation may weaken aversive expression or increase state noise | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| CsChrimson_red_617nm_40Hz_20ms_0.5s_1.0mW | oct_sucrose_appetitive_wt | CsChrimson_red | 617 | 40 | 20 | 0.5 | 1 | 0.86 | 0.8719 | 0.02376 | 0.2685 | reward-memory expression or delayed consolidation support | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |
| CsChrimson_red_617nm_40Hz_20ms_0.5s_1.0mW | weak_oct_strong_mch_conflict | CsChrimson_red | 617 | 40 | 20 | 0.5 | 1 | 0.88 | 0.8959 | 0.03172 | 0.2691 | best behavioural sensitivity: weak CS+ versus strong CS- conflict | T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging |

湿实验最方便的行为设计：

| priority | experiment | genetic_design | protocol_id | light | primary_readout | critical_control | expected_result | why_feasible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | DPM optogenetic group behaviour | DPM-driver > red-shifted opsin; group T-maze or camera-tracked OCT/MCH assay | CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW | 617 nm, 40 Hz, 20 ms pulses, 5.0 s, 0.1 mW/mm2 | weak_oct_strong_mch_conflict choice index; predicted delta 0.104 | CS+/CS- side mirror, OCT/MCH counterbalance, no-opsin, retinal-minus, red-light-only controls | best behavioural sensitivity: weak CS+ versus strong CS- conflict | hundreds of flies can be tested without measuring NT lateralization in each individual |
| 2 | DPM optogenetic group behaviour | DPM-driver > red-shifted opsin; group T-maze or camera-tracked OCT/MCH assay | ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW | 627 nm, 40 Hz, 20 ms pulses, 5.0 s, 0.1 mW/mm2 | weak_oct_strong_mch_conflict choice index; predicted delta 0.104 | CS+/CS- side mirror, OCT/MCH counterbalance, no-opsin, retinal-minus, red-light-only controls | best behavioural sensitivity: weak CS+ versus strong CS- conflict | hundreds of flies can be tested without measuring NT lateralization in each individual |
| 3 | DPM optogenetic group behaviour | DPM-driver > red-shifted opsin; group T-maze or camera-tracked OCT/MCH assay | ReaChR_red_617nm_40Hz_20ms_5.0s_0.1mW | 617 nm, 40 Hz, 20 ms pulses, 5.0 s, 0.1 mW/mm2 | weak_oct_strong_mch_conflict choice index; predicted delta 0.103 | CS+/CS- side mirror, OCT/MCH counterbalance, no-opsin, retinal-minus, red-light-only controls | best behavioural sensitivity: weak CS+ versus strong CS- conflict | hundreds of flies can be tested without measuring NT lateralization in each individual |
| 4 | DPM optogenetic group behaviour | DPM-driver > red-shifted opsin; group T-maze or camera-tracked OCT/MCH assay | CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW | 617 nm, 40 Hz, 20 ms pulses, 5.0 s, 0.1 mW/mm2 | oct_sucrose_appetitive_wt choice index; predicted delta 0.078 | CS+/CS- side mirror, OCT/MCH counterbalance, no-opsin, retinal-minus, red-light-only controls | reward-memory expression or delayed consolidation support | hundreds of flies can be tested without measuring NT lateralization in each individual |
| 5 | DPM optogenetic group behaviour | DPM-driver > red-shifted opsin; group T-maze or camera-tracked OCT/MCH assay | ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW | 627 nm, 40 Hz, 20 ms pulses, 5.0 s, 0.1 mW/mm2 | oct_sucrose_appetitive_wt choice index; predicted delta 0.078 | CS+/CS- side mirror, OCT/MCH counterbalance, no-opsin, retinal-minus, red-light-only controls | reward-memory expression or delayed consolidation support | hundreds of flies can be tested without measuring NT lateralization in each individual |

建议优先测试 `weak_oct_strong_mch_conflict` 和 delayed memory window，因为普通 OCT/MCH choice rate 容易饱和，冲突条件和延迟窗口更容易暴露 DPM/5-HT 调节效应。

## 6. 两方面证明如何支撑我们的方法

**证明 A：功能成像证明。** 如果 DPM 光遗传下，右侧 5-HT/KC readout 在偏侧化果蝇中稳定高于左侧，并且 180 度旋转后按脑侧注册仍保持右偏，则说明仿真预测的偏侧化 release pattern 有功能对应。这个证明不需要果蝇继续做行为。

**证明 B：群体行为证明。** 如果独立群体在 OCT/MCH T-maze 中，DPM 红光刺激按预测方向改变 delayed/conflict 条件的 choice index，则说明 DPM/5-HT 轴不仅能产生释放 pattern，还能调节可观测行为。这个证明不需要知道每只果蝇的 NT 侧化程度。

两者合在一起形成严谨链条：连接组/NT 统计提出侧化假说，DPM 光遗传成像验证功能 readout，群体 T-maze 验证行为调节方向，GRASP/split-GFP 最后提供结构硬证据。

## 7. 图和视频

- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/figures/Fig_dpm_opsin_wavelength_protocol_space.png`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/figures/Fig_dpm_downstream_roi_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/figures/Fig_dpm_5ht_release_timecourses.png`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/figures/Fig_dpm_behavior_modulation_predictions.png`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/figures/Fig_dpm_wetlab_validation_design.png`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/videos/dpm_optogenetic_release_prediction.mp4`

这些图已同步到 `/unify/ydchen/unidit/bio_fly/paper/figures` 和 `/unify/ydchen/unidit/bio_fly/ppt/figures`；视频已同步到 `/unify/ydchen/unidit/bio_fly/paper/video`。
