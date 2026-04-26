# OCT/MCH 多 seed 行为套件报告

保存路径：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/OCT_MCH_FORMAL_SUITE_CN.md`

## 目的

本套件把上一轮 0.2 秒单 seed sanity check 升级为多 seed、可统计的 OCT/MCH 行为 screen。它仍然是具身代理仿真，不是最终真实行为学实验；但它已经把 OCT/MCH 条件表、calibrated motor bridge 和 FlyGym memory choice trial 连接成可重复统计流程。

## 运行参数

- 条件表：`/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv`
- trials：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/oct_mch_formal_trials.csv`
- 条件汇总：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/oct_mch_formal_condition_summary.csv`
- 对照比较：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/oct_mch_formal_wt_comparisons.csv`
- 图：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/figures/Fig_oct_mch_formal_suite.png`
- n_trials_per_condition：`4`
- run_time_s：`0.35`
- max_workers：`4`
- render：`False`

## 条件汇总

                                condition  n_trials  cs_plus_choice_rate  expected_choice_rate  mean_approach_margin  expected_choice_fdr_q             cs_plus_odor unconditioned_stimulus                mb_perturbation
mch_sucrose_appetitive_wt_counterbalanced         4                  1.0                   1.0              1.121587                  0.125 MCH_4-methylcyclohexanol         sucrose_reward           wild_type_connectome
            oct_sucrose_right_mb_silenced         4                  1.0                   1.0              1.059814                  0.125            OCT_3-octanol         sucrose_reward             right_MB_gain_0.25
                oct_sucrose_appetitive_wt         4                  1.0                   1.0              0.962411                  0.125            OCT_3-octanol         sucrose_reward           wild_type_connectome
             oct_sucrose_left_mb_silenced         4                  1.0                   1.0              0.861734                  0.125            OCT_3-octanol         sucrose_reward              left_MB_gain_0.25
                   oct_sucrose_mb_swapped         4                  1.0                   1.0              0.851617                  0.125            OCT_3-octanol         sucrose_reward  left_right_MB_weights_swapped
               oct_sucrose_mb_symmetrized         4                  1.0                   1.0              0.711964                  0.125            OCT_3-octanol         sucrose_reward left_right_MB_weights_averaged
             weak_oct_strong_mch_conflict         4                  1.0                   1.0              0.672881                  0.125            OCT_3-octanol         sucrose_reward           wild_type_connectome
                    oct_shock_aversive_wt         4                  0.0                   1.0             -0.673866                  0.125            OCT_3-octanol         electric_shock           wild_type_connectome

## 解释

- `mean_approach_margin = d(CS-) - d(CS+)`，正值表示更接近 CS+，负值表示更接近 CS-。
- `expected_choice_rate` 根据条件预期计算：奖励条件预期选择 CS+，电击条件预期选择 CS-。
- `expected_choice_fdr_q` 是 expected choice 对 0.5 随机选择的二项检验 FDR 校正值。

## 当前边界

当前默认运行可作为 pilot 统计。若要作为论文主图证据，建议使用：

```bash
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite \
  --n-trials 50 \
  --run-time 0.8 \
  --max-workers 4
```

不能把本代理 screen 写成真实果蝇行为学显著性证据；它用于决定真实实验和更大规模仿真的优先条件。
