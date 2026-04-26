# OCT/MCH 嗅觉条件化记忆实验计划

保存路径：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/OCT_MCH_CONDITIONING_PLAN_CN.md`

## 目的

这一组配置把“闻到了什么”明确写成经典果蝇嗅觉条件化气味：`OCT_3-octanol` 和 `MCH_4-methylcyclohexanol`。每个条件都有 `CS+`、`CS-`、`US`、左右摆放、蘑菇体扰动和预期行为，后续可以直接接入 FlyGym 行为仿真或真实果蝇行为实验。

## 关键变量

- `CS+`：训练时与 unconditioned stimulus 配对的气味。若 `US=sucrose_reward`，测试时应趋近 CS+；若 `US=electric_shock`，测试时应回避 CS+。
- `CS-`：训练时未与 US 配对的对照气味。
- `US`：unconditioned stimulus，即不需要学习就有生物意义的刺激。这里包括糖奖励 `sucrose_reward` 和电击惩罚 `electric_shock`。
- `OCT_3-octanol`：经典果蝇嗅觉记忆实验常用气味之一。
- `MCH_4-methylcyclohexanol`：经典对照气味之一。
- `mb_perturbation`：蘑菇体左右侧化扰动，包括左侧抑制、右侧抑制、左右平均化和左右互换。

## 条件表

                                     name             cs_plus_odor            cs_minus_odor unconditioned_stimulus cs_plus_side  cs_plus_intensity  cs_minus_intensity  training_epochs                     memory_phase                mb_perturbation                   expected_behavior                                                      biological_question
                oct_sucrose_appetitive_wt            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward         left               1.00                 1.0                3                     acute_memory           wild_type_connectome                    approach_CS_plus                baseline appetitive odor memory with OCT as rewarded odor
mch_sucrose_appetitive_wt_counterbalanced MCH_4-methylcyclohexanol            OCT_3-octanol         sucrose_reward        right               1.00                 1.0                3                     acute_memory           wild_type_connectome                    approach_CS_plus  odor identity counterbalance to separate memory from odor-specific bias
                    oct_shock_aversive_wt            OCT_3-octanol MCH_4-methylcyclohexanol         electric_shock         left               1.00                 1.0                3                     acute_memory           wild_type_connectome                       avoid_CS_plus                  aversive memory should reverse the sign of CS+ approach
             oct_sucrose_left_mb_silenced            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward         left               1.00                 1.0                3                     acute_memory              left_MB_gain_0.25 reduced_or_shifted_CS_plus_approach test whether left MB feedback contributes to appetitive memory stability
            oct_sucrose_right_mb_silenced            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward        right               1.00                 1.0                3                     acute_memory             right_MB_gain_0.25       altered_output_or_choice_bias         test whether right DAN-MBON output axis controls expression bias
               oct_sucrose_mb_symmetrized            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward         left               1.00                 1.0                3                     acute_memory left_right_MB_weights_averaged        reduced_lateralization_index    causal control for structural asymmetry rather than total MB strength
                   oct_sucrose_mb_swapped            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward         left               1.00                 1.0                3                     acute_memory  left_right_MB_weights_swapped  reversed_lateralization_prediction          strongest in-silico causal test for MB lateralization mechanism
             weak_oct_strong_mch_conflict            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward         left               0.35                 1.0                3 retrieval_under_sensory_conflict           wild_type_connectome     memory_dependent_CS_plus_rescue          test whether memory can overcome weaker immediate sensory plume

## 输出

- CSV 条件表：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/oct_mch_condition_table.csv`
- YAML 条件表：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/oct_mch_condition_table.yaml`

## 下一步如何接入仿真

当前 FlyGym 行为层已经能放置两个气味源，并用 `cs_plus_intensity`、`cs_minus_intensity`、`cs_plus_side` 表示条件化气味竞争。下一步需要把 `cs_plus_odor` 和 `cs_minus_odor` 接到更具体的 ORN/PN/KC sensory encoder，而不是只作为视频标签。这样才能从“两个抽象气味源”升级为“OCT/MCH 气味身份特异性输入”。
