# DPM 光遗传仿真验证方案：从 5-HT 释放 pattern 到群体行为

本报告回答当前最核心的问题：能否通过仿真脑先模拟光遗传激活 DPM neuron，预测偏侧化果蝇的激活 pattern 和 5-HT 释放 pattern，并把结果转成湿实验方便验证的设计。

## 给不熟悉赛博果蝇的读者：这个仿真实验到底怎么跑

本报告里的“仿真脑”不是一个已经完整复制真实果蝇所有生理过程的数字生命体。它是一个连接组约束的预测器：用真实 FlyWire 接线图告诉我们，假如 DPM 神经元被光遗传激活，影响会优先沿哪些连接传播到蘑菇体、DAN、APL、MBON 和下游 readout；再用一个明确写出的 release/readout 模型，把这种传播转成可被湿实验测量的 5-HT 释放曲线和群体行为预测。

完整流程如下：

1. **选择 seed。** 从 FlyWire/注释表中选择 DPM neuron，分别构造 `left_DPM_opto`、`right_DPM_opto` 和 `bilateral_DPM_opto` 三类输入。
2. **设置虚拟光刺激。** 枚举 `ChR2_blue`、`ReaChR_red`、`CsChrimson_red`，并扫描波长、频率、脉宽、刺激时长和光强。
3. **连接组传播。** 在 GPU0/1 上运行 signed propagation，计算 DPM 激活经过 FlyWire 连接矩阵传播到哪些 neuron 和哪些脑区。
4. **ROI 聚合。** 把传播后的神经元响应聚合到 `KC_all`、`KCa'b'_memory_consolidation`、`MBON_output`、`DAN_teaching`、`APL_feedback` 等下游读出。
5. **释放曲线预测。** 用光刺激能量、opsin 波长匹配度、DPM 左右传播强度和侧化假设，生成 `left_release_au`、`right_release_au`、release AUC 和 release LI。
6. **旋转伪影控制。** 模拟“果蝇水平旋转 180 度”后的图像坐标和脑侧坐标。如果是真实脑侧化，按脑侧注册的 LI 不应变号；如果只是成像角度伪影，图像坐标下的 LI 会跟着翻转。
7. **行为预测。** 把 DPM/5-HT release 预测映射到 OCT/MCH T-maze 代理，输出 `choice_index_delta`、`approach_margin` 和最值得做的实验条件。

一句话解释：我们不是声称“仿真已经看到了真实 5-HT 释放”，而是在用连接组和光遗传参数生成一个可检验预测：**如果 DPM 5-HT 侧化是真实的，那么用红光激活 DPM 时，右侧相关 readout 应更强，并且这个差异应能在 180 度旋转控制和独立群体行为实验中被验证。**

## 每个关键变量是什么意思

| 变量 | 含义 | 怎么解释 |
| --- | --- | --- |
| `opsin` | 光遗传工具名称，例如 `ChR2_blue`、`ReaChR_red`、`CsChrimson_red` | 不同 opsin 对不同波长的光敏感性不同；本项目优先推荐红光工具，因为更适合成人果蝇行为并减少蓝光视觉干扰 |
| `wavelength_nm` | 光波长，单位 nm | 470 nm 是蓝光，617/627 nm 是红光；数值决定是否能有效激活对应 opsin |
| `frequency_hz` | 光脉冲频率，每秒多少次 | 40 Hz 表示每秒 40 个脉冲；频率越高不一定越好，可能引入非生理或热效应 |
| `pulse_width_ms` | 每个光脉冲持续时间，单位 ms | 20 ms 表示每次亮光 20 毫秒；与频率共同决定 duty cycle |
| `train_duration_s` | 一组刺激持续时间，单位秒 | 5 s 是主推荐协议；0.5 s 高光强可作为短刺激对照 |
| `irradiance_mw_mm2` | 光强，单位 mW/mm2 | 湿实验中需要从低强度开始，避免热效应和非特异行为扰动 |
| `protocol_energy` | 协议总能量的相对量 | 由光强、频率、脉宽和时长综合得到，用于比较不同协议 |
| `left_release_au` / `right_release_au` | 左/右半脑预测 5-HT 释放强度 | `au` 是 arbitrary unit，表示相对量，不是真实浓度 |
| `peak_total_release_au` | 预测释放峰值总量 | 用于排序哪个协议更容易产生可检测信号 |
| `release_auc_au_s` | 释放曲线下面积 | 反映一段时间内总释放量，适合与成像 AUC 对接 |
| `brain_registered_release_li` | 按脑侧注册的左右释放指数 | 常用形式为 `(right - left)/(right + left)`；正值表示右侧更强 |
| `image_li_after_180deg_rotation` | 果蝇旋转 180 度后，按相机图像坐标看到的 LI | 用来区分真实脑侧化和成像角度伪影 |
| `choice_index_delta` | 光遗传刺激前后群体选择指数变化 | 正值表示更偏向仿真预测的记忆方向，负值表示相反 |
| `approach_margin` | 接近目标气味相对远离竞争气味的优势 | 越大表示越靠近预期目标 |
| `wetlab_priority_score` | 湿实验优先级 | 综合效应大小、可测性、文献可行性和对照清晰度；不是 p 值 |

## 一键复现命令

推荐只使用 GPU0/1，避免影响其它卡上的任务：

```bash
cd /unify/ydchen/unidit/bio_fly
CUDA_VISIBLE_DEVICES=0,1 /unify/ydchen/unidit/bio_fly/env/bin/python \
  /unify/ydchen/unidit/bio_fly/scripts/run_dpm_optogenetic_validation.py \
  --devices cuda:0 cuda:1
```

主要输出目录：

- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_optogenetic_protocol_library.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_5ht_release_pattern_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_optogenetic_behavior_predictions.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/tables/dpm_wetlab_protocol_recommendations.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/dpm_optogenetic_validation_20260429/videos/dpm_optogenetic_release_prediction.mp4`

如果要同时复现会议反馈分拆实验：

```bash
cd /unify/ydchen/unidit/bio_fly
CUDA_VISIBLE_DEVICES=0,1 /unify/ydchen/unidit/bio_fly/env/bin/python \
  /unify/ydchen/unidit/bio_fly/scripts/run_meeting_feedback_experiments.py \
  --devices cuda:0 cuda:1
```

对应输出目录是 `/unify/ydchen/unidit/bio_fly/outputs/meeting_feedback_20260429`。

## 结论先行

1. **成像证明和行为证明应分开做。** 5-HT 侧化成像会破坏或强扰动果蝇，不能要求同一只果蝇继续做行为；因此本项目把“释放 pattern 成像验证”和“群体行为调节验证”拆成两条链。
2. **DPM 光遗传优先用红光工具。** 文献支持 ReaChR/CsChrimson 在成人果蝇行为中用红光激活；本仿真把 617/627 nm 设为优先协议，470 nm 只作为蓝光 positive/control 或校准，不作为主行为实验。
3. **最关键的可验证 readout 是 brain-registered laterality index。** 如果是真实偏侧化，水平旋转果蝇 180 度后，按脑侧配准的左右符号应保持；如果是成像角度伪影，图像坐标符号会翻转。
4. **行为验证不需要直接测每只果蝇的 NT 侧化。** 使用几百只果蝇群体 T-maze，在训练或测试窗口给 DPM 红光刺激，看 OCT/MCH choice index 是否按仿真方向移动。
5. **结构验证仍是硬红线。** 仿真和功能/行为结果最多形成强佐证；若要把“递质侧化是群体稳定结构规律”写成定论，仍需 GRASP、split-GFP 或等价结构实验。

## 这五个仿真实验分别怎么做，结果是什么

### 1. 选 DPM neuron 作为起点，做 FlyWire 上的连接组传播

这一步是在回答：如果我们把 DPM 当成输入起点，它的影响会沿着真实连接组跑到哪里。

怎么做：

1. 从 FlyWire 注释里挑出 DPM 相关 neuron，拆成 `left_DPM_opto`、`right_DPM_opto` 和 `bilateral_DPM_opto`。
2. 在 GPU0/1 上运行 signed multi-hop propagation。
3. 把传播结果聚合到 `KC_all`、`KCa'b'_memory_consolidation`、`MBON_output`、`DAN_teaching`、`APL_feedback` 和 `DN_motor_exit`。
4. 用随机或对照 seed 做比较，确认不是任意神经元都能产生同样的 readout。

看什么结果：

| condition | n_seed_neurons | n_active_neurons | absolute_mass | left_abs_mass | right_abs_mass | right_laterality_index |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `left_DPM_opto` | 1 | 6280 | 1.283 | 1.176 | 0.1068 | -0.8334 |
| `right_DPM_opto` | 1 | 6386 | 1.403 | 0.1351 | 1.267 | 0.8073 |
| `bilateral_DPM_opto` | 2 | 6378 | 1.264 | 0.8107 | 0.4528 | -0.2832 |

最关键的下游 ROI 结果是：

| condition | roi | abs_mass |
| --- | --- | ---: |
| `left_DPM_opto` | `KC_all` | 1.45 |
| `right_DPM_opto` | `KC_all` | 1.405 |
| `bilateral_DPM_opto` | `KC_all` | 1.396 |
| `right_DPM_opto` | `KCa'b'_memory_consolidation` | 0.4485 |
| `left_DPM_opto` | `KCa'b'_memory_consolidation` | 0.4461 |
| `bilateral_DPM_opto` | `KCa'b'_memory_consolidation` | 0.4527 |
| `left_DPM_opto` | `MBON_output` | 0.3471 |
| `right_DPM_opto` | `MBON_output` | 0.3428 |
| `left_DPM_opto` | `APL_feedback` | 0.1799 |
| `left_DPM_opto` | `DAN_teaching` | 0.1624 |

这说明什么：

- DPM 作为起点，最强的传播首先回到 KC/蘑菇体相关区域。
- `KCa'b'_memory_consolidation` 是最值得优先看的记忆巩固子区之一。
- `MBON`、`APL` 和 `DAN` 也会被带动，说明这不是局部噪声，而是记忆轴上的系统性传播。
- 右侧 DPM seed 的整体右偏最强，`right_laterality_index = 0.8073`，左侧 DPM 则是左偏，`-0.8334`。

### 2. 扫描不同光遗传协议，尤其是 CsChrimson 和 ReaChR

这一步是在回答：什么光遗传工具和刺激参数最适合做后续湿实验。

怎么做：

1. 把 `opsin`、`wavelength_nm`、`frequency_hz`、`pulse_width_ms`、`train_duration_s` 和 `irradiance_mw_mm2` 组成一个协议库。
2. 对每个协议都跑一次 DPM 传播和 release 预测。
3. 给每个协议打一个 `wetlab_priority_score`，综合考虑可测性和对照清晰度。

结果最靠前的协议是：

| protocol_id | opsin | wavelength_nm | frequency_hz | pulse_width_ms | train_duration_s | irradiance_mw_mm2 | peak_total_release_au | release_auc_au_s | peak_brain_registered_li | wetlab_priority_score |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW` | `CsChrimson_red` | 617 | 40 | 20 | 5.0 | 0.1 | 1.7707 | 11.6495 | 0.8022 | 4.2102 |
| `ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW` | `ReaChR_red` | 627 | 40 | 20 | 5.0 | 0.1 | 1.7707 | 11.6495 | 0.8022 | 4.2102 |
| `CsChrimson_red_617nm_40Hz_20ms_0.5s_1.0mW` | `CsChrimson_red` | 617 | 40 | 20 | 0.5 | 1.0 | 1.6606 | 3.5636 | 0.8010 | 4.2075 |
| `ReaChR_red_627nm_40Hz_20ms_0.5s_1.0mW` | `ReaChR_red` | 627 | 40 | 20 | 0.5 | 1.0 | 1.6606 | 3.5636 | 0.8010 | 4.2075 |

这说明什么：

- 这套仿真更支持红光工具，而不是把蓝光当主实验条件。
- `CsChrimson` 和 `ReaChR` 都是高优先级候选，优先级接近。
- 5 秒、0.1 mW/mm2 这一组协议同时兼顾了释放峰值和 AUC，因此最适合作为“先跑通验证”的湿实验起点。

### 3. 预测 DPM 激活后左右半脑的 5-HT 释放 pattern

这一步是在回答：DPM 被光遗传激活后，左右半脑的血清素释放会不会出现稳定偏侧。

怎么做：

1. 把 DPM 激活后的传播结果映射成一个相对的 5-HT 释放曲线。
2. 分别计算左半脑和右半脑的 `release_au`。
3. 用 `brain_registered_release_li` 判断左右偏向。
4. 另外计算 `image_li_after_180deg_rotation`，看旋转后图像坐标是否会误导判断。

结果最稳定的是：

| protocol_id | fly_model | peak_total_release_au | release_auc_au_s | peak_brain_registered_li | mean_rotation_discrepancy |
| --- | --- | ---: | ---: | ---: | ---: |
| `CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW` | `lateralized_fly` | 1.7707 | 11.6495 | 0.8022 | 0.0 |
| `ReaChR_red_627nm_40Hz_20ms_5.0s_0.1mW` | `lateralized_fly` | 1.7707 | 11.6495 | 0.8022 | 0.0 |
| `CsChrimson_red_617nm_40Hz_20ms_0.5s_1.0mW` | `lateralized_fly` | 1.6606 | 3.5636 | 0.8010 | 0.0 |
| `ReaChR_red_627nm_20Hz_20ms_1.0s_1.0mW` | `lateralized_fly` | 1.7639 | 4.6138 | 0.8021 | 0.0 |

同一协议下的 `camera_artifact_control` 会给出负的旋转差异，例如：

- `CsChrimson_red_617nm_40Hz_20ms_5.0s_0.1mW` 的 `mean_rotation_discrepancy = -1.2289`
- `ReaChR_red_627nm_20Hz_20ms_1.0s_1.0mW` 的 `mean_rotation_discrepancy = -0.8862`

这说明什么：

- 如果你按脑侧去看，仿真给出的 release 偏侧是稳定右偏，`peak_brain_registered_li` 大约在 `0.80` 左右。
- 如果你只按图像坐标去看，水平旋转 180 度以后会出现相反的假象，所以必须做脑侧注册。
- 这一步不是说真实果蝇已经被测出来，而是说我们已经把“脑侧真实偏侧化”和“成像角度伪影”区分开了。

### 4. 做 180 度旋转控制，判断这是不是“脑侧真实偏侧化”而不是成像角度伪影

这一步的核心不是再跑一个新生物学现象，而是一个排错实验。

怎么做：

1. 对同一只果蝇，按原始方向记录一次。
2. 再把果蝇水平旋转 180 度，重复记录。
3. 分析时分别计算 image-coordinate 下的 LI 和 brain-registered LI。
4. 看两者在旋转后是否表现一致。

仿真结果的逻辑是：

- `fly_model = lateralized_fly` 时，脑侧注册的 LI 不变，说明是真实偏侧化。
- `fly_model = camera_artifact_control` 时，图像坐标下的 LI 会翻转，说明如果只看画面方向就会误判。

这一步的结论很重要，因为它决定我们后面能不能把“右侧更强”写成真正的脑侧发现，而不是显微镜摆放导致的左右假象。

### 5. 把这个结果映射到 OCT/MCH 群体行为，预测 choice index 会怎么变

这一步是在回答：如果 DPM/5-HT 偏侧化是真的，它有没有可能改变群体气味记忆选择。

怎么做：

1. 把 DPM 的 release 预测映射到 OCT/MCH 行为代理。
2. 设定三个行为条件：`oct_shock_aversive_wt`、`oct_sucrose_appetitive_wt` 和 `weak_oct_strong_mch_conflict`。
3. 计算给 DPM 红光刺激前后的 `choice_index_delta` 和 `approach_margin`。

结果最敏感的是 weak conflict 条件：

| assay_condition | base_expected_choice_rate | predicted_expected_choice_rate_with_DPM_opto | predicted_choice_index_delta | predicted_approach_margin_with_DPM_opto |
| --- | ---: | ---: | ---: | ---: |
| `weak_oct_strong_mch_conflict` | 0.88 | 0.9319 | 0.1038 | 0.2787 |
| `oct_sucrose_appetitive_wt` | 0.86 | 0.8988 | 0.0777 | 0.2757 |
| `oct_shock_aversive_wt` | 0.86 | 0.8276 | -0.0647 | -0.2365 |

这说明什么：

- 普通正性任务里，DPM 红光刺激会把 choice index 往正方向推一点，但效应不如 conflict 条件敏感。
- 普通惩罚任务里，choice index 会往负方向走，表示更偏向回避。
- `weak_oct_strong_mch_conflict` 是最适合做湿实验验证的条件，因为它最容易暴露 DPM/5-HT 调节，不容易天花板化。

### 这一整套仿真最后得出的总结

把上面 5 步合在一起，当前仿真已经给出了一个明确的可检验假说：

1. DPM 的连接组传播可以强烈投射到 KC/蘑菇体记忆相关区域。
2. 红光 DPM 光遗传协议里，`CsChrimson 617 nm` 和 `ReaChR 627 nm` 是最值得先做的两个候选。
3. DPM 激活后，按脑侧注册的 5-HT release pattern 预测是右偏，峰值 `LI` 大约 `0.80`。
4. 180 度旋转控制说明必须区分真实脑侧化和成像角度伪影。
5. 在行为层面，最敏感的验证条件不是普通强刺激，而是 `weak OCT / strong MCH conflict`，预测 `choice_index_delta` 约 `+0.104`。

这里补一句实现细节，避免把它误读成机器学习拟合结果：

- 行为预测不是训练出来的模型，而是把 `DPM` 连接组传播强度和左右偏侧指数，映射到 OCT/MCH 基线行为上的规则模型。
- 代码里先从 `release_auc_au_s` 归一化出 `release_drive`，再从 `peak_brain_registered_li` 归一化出 `li_drive`。
- 冲突条件用 `predicted_delta = 0.10 * release_drive * li_drive`。
- 最后把 `predicted_choice` 与 `base_choice` 的差异乘以 2，得到 `predicted_choice_index_delta`。

因此 `+0.104` 的含义是“模型预测的 choice index 增量”，不是湿实验已经测到的显著性差异。

这就是我们目前“仿真做了什么、发现了什么、下一步怎么用湿实验验证”的完整逻辑。

## 文献依据

- DPM 5-HT 与蘑菇体 ARM/记忆相关：Lee et al., Neuron 2011，PubMed: https://pubmed.ncbi.nlm.nih.gov/21808003/
- 5-HT sensor 可报告 DPM/KC 相关 5-HT dynamics：Wan et al., Nature Neuroscience 2021，PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC8544647/
- ReaChR 成人果蝇红光光遗传行为：Inagaki et al., Nature Methods 2014，PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC4151318/
- DPM appetitive/aversive memory trace 与时间窗：Yu et al. / follow-up memory trace work，PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3396741/

## 湿实验怎么验证最严谨

### 证明 1：结构层面确认侧化不是偶然

目标：验证“右侧 5-HT/DPM 输入更强、左侧 Glu 输入更强，且 alpha'beta' 记忆巩固区最明显”是否是群体稳定规律。

推荐实验：

- 使用 GRASP/split-GFP 或等价突触接触报告，优先看 right DPM/5-HT input -> right `KCa'b'`。
- 同时选择 left Glu input -> left `KCa'b'` 作为相反方向 positive control。
- 分析时必须按脑侧注册，而不是按显微镜图像左右注册。
- 每只果蝇只提供结构或成像证据，不要求继续做行为。

主指标：

- 左右 ROI 的荧光强度、接触点数量或体素体积。
- laterality index：`(right - left) / (right + left)`。
- 180 度旋转或盲法 ROI 注册后的 LI 稳定性。

### 证明 2：功能层面验证 DPM 光遗传 release pattern

目标：验证仿真预测的 DPM 红光激活是否会产生可重复的右偏 5-HT/KC readout。

推荐实验：

- 遗传设计：`DPM-driver > CsChrimson` 或 `DPM-driver > ReaChR`，KC 或 MB compartment 表达 5-HT sensor 或 GCaMP。
- 光刺激：优先从 `617/627 nm, 40 Hz, 20 ms pulses, 5.0 s, 0.1 mW/mm2` 起步。
- 同一只果蝇做两个方向：原始方向和水平旋转 180 度。
- 对照：no-opsin、retinal-minus、red-light-only、盲法 ROI 注册、低频/低强度 dose control。

主指标：

- 左/右 peak dF/F。
- 左/右 AUC。
- 响应上升时间和半衰期。
- brain-registered release LI。
- image-coordinate LI 在 180 度旋转后的变化。

判定逻辑：

- 如果是**真实脑侧化**，按脑侧注册的 LI 应保持同一方向。
- 如果是**成像角度伪影**，按图像坐标看的 LI 更可能随旋转翻转。

### 证明 3：行为层面验证 DPM/5-HT 轴能调节记忆选择

目标：不要求每只果蝇都测 NT 侧化，而是在群体层面验证“DPM 红光刺激会按仿真方向改变 OCT/MCH 记忆选择”。

推荐实验：

- 使用独立果蝇群体，不和成像果蝇混用。
- 任务：OCT/MCH T-maze 或摄像轨迹实验。
- 条件：优先做 `weak OCT / strong MCH conflict` 和 delayed memory window，因为普通强气味任务容易天花板化。
- 在训练、巩固或测试窗口给 DPM 红光刺激，先选一个预注册主窗口，避免事后挑选。
- 做 CS+/CS- side mirror 和 OCT/MCH counterbalance。
- 对照：no-opsin、retinal-minus、red-light-only、无训练 naive、红光但不表达 opsin。

主指标：

- choice index。
- approach margin。
- early turning bias。
- 群体速度和活动量，排除只是红光让果蝇不动或过度兴奋。

判定逻辑：

- 如果 DPM/5-HT 轴影响记忆表达，红光组相对对照组的 choice index 应按仿真方向移动。
- 如果只改变活动量而不改变 choice index，需要谨慎解释为非特异运动效应。

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
