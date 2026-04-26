# OCT/MCH 多 seed 行为套件报告

保存路径：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/OCT_MCH_FORMAL_SUITE_CN.md`

## 目的

本套件把上一轮 0.2 秒单 seed sanity check 升级为多 seed、可统计的 OCT/MCH 行为 screen。本次运行类型：`正式仿真`。它仍然是具身代理仿真，不是最终真实行为学实验；但它已经把 OCT/MCH 条件表、calibrated motor bridge 和 FlyGym memory choice trial 连接成可重复统计流程。

## 运行参数

- 条件表：`/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv`
- trials：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_trials.csv`
- 条件汇总：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_condition_summary.csv`
- 对照比较：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_wt_comparisons.csv`
- 图：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/figures/Fig_oct_mch_formal_suite.png`
- n_trials_per_condition：`50`
- run_time_s：`0.2`
- max_workers：`4`
- render：`False`
- mirror_sides：`True`
- early_fraction：`0.25`
- commit_y_threshold_mm：`0.75`

## 条件汇总

                                condition  n_trials  cs_plus_choice_rate  expected_choice_rate  mean_approach_margin  expected_choice_fdr_q             cs_plus_odor unconditioned_stimulus                mb_perturbation
            oct_sucrose_right_mb_silenced       100                 0.89                  0.89              0.303976           6.775609e-16            OCT_3-octanol         sucrose_reward             right_MB_gain_0.25
             oct_sucrose_left_mb_silenced       100                 0.89                  0.89              0.297667           6.775609e-16            OCT_3-octanol         sucrose_reward              left_MB_gain_0.25
               oct_sucrose_mb_symmetrized       100                 0.89                  0.89              0.292496           6.775609e-16            OCT_3-octanol         sucrose_reward left_right_MB_weights_averaged
                oct_sucrose_appetitive_wt       100                 0.86                  0.86              0.265371           9.467945e-14            OCT_3-octanol         sucrose_reward           wild_type_connectome
             weak_oct_strong_mch_conflict       100                 0.88                  0.88              0.264908           3.822715e-15            OCT_3-octanol         sucrose_reward           wild_type_connectome
                   oct_sucrose_mb_swapped       100                 0.87                  0.87              0.263343           2.100770e-14            OCT_3-octanol         sucrose_reward  left_right_MB_weights_swapped
mch_sucrose_appetitive_wt_counterbalanced       100                 0.85                  0.85              0.245904           4.825422e-13 MCH_4-methylcyclohexanol         sucrose_reward           wild_type_connectome
                    oct_shock_aversive_wt       100                 0.14                  0.86             -0.244407           9.467945e-14            OCT_3-octanol         electric_shock           wild_type_connectome

## 侧化动力学汇总

                                condition  n_trials  n_nominal_side_trials  n_mirror_side_trials  mean_expected_laterality_index  mean_early_expected_lateral_velocity  mean_expected_curvature_rad_per_mm  mean_physical_laterality_index  mean_time_to_expected_zone_s
            oct_sucrose_right_mb_silenced       100                     50                    50                        0.102954                             -0.553725                           -0.782775                       -0.003768                           NaN
             oct_sucrose_left_mb_silenced       100                     50                    50                        0.099731                             -0.766174                           -1.229535                       -0.004334                           NaN
               oct_sucrose_mb_symmetrized       100                     50                    50                        0.095934                             -0.484511                           -0.262509                        0.004926                           NaN
                oct_sucrose_appetitive_wt       100                     50                    50                        0.089150                             -0.575002                            0.331695                        0.001040                           NaN
             weak_oct_strong_mch_conflict       100                     50                    50                        0.089230                             -0.525155                           -0.755631                       -0.011458                           NaN
                   oct_sucrose_mb_swapped       100                     50                    50                        0.088346                             -0.511283                           -1.209758                       -0.008577                           NaN
mch_sucrose_appetitive_wt_counterbalanced       100                     50                    50                        0.084061                             -0.543153                           -0.722323                        0.001594                           NaN
                    oct_shock_aversive_wt       100                     50                    50                        0.083488                             -0.552929                           -0.822829                        0.007508                           NaN

## WT 对照比较

                                condition                                 reference  delta_mean_approach_margin  welch_fdr_q  delta_mean_early_expected_lateral_velocity  welch_fdr_q_early_expected_lateral_velocity  delta_mean_expected_laterality_index  welch_fdr_q_expected_laterality_index  delta_mean_physical_laterality_index  welch_fdr_q_physical_laterality_index  delta_mean_expected_curvature_rad_per_mm  welch_fdr_q_expected_curvature_rad_per_mm
mch_sucrose_appetitive_wt_counterbalanced mch_sucrose_appetitive_wt_counterbalanced                    0.000000          1.0                                    0.000000                                          1.0                              0.000000                                    1.0                              0.000000                                    1.0                                  0.000000                                   1.000000
                    oct_shock_aversive_wt                     oct_shock_aversive_wt                    0.000000          1.0                                    0.000000                                          1.0                              0.000000                                    1.0                              0.000000                                    1.0                                  0.000000                                   1.000000
                oct_sucrose_appetitive_wt                 oct_sucrose_appetitive_wt                    0.000000          1.0                                    0.000000                                          1.0                              0.000000                                    1.0                              0.000000                                    1.0                                  0.000000                                   1.000000
             oct_sucrose_left_mb_silenced                 oct_sucrose_appetitive_wt                    0.032297          1.0                                   -0.191173                                          1.0                              0.010581                                    1.0                             -0.005374                                    1.0                                 -1.561230                                   0.170533
                   oct_sucrose_mb_swapped                 oct_sucrose_appetitive_wt                   -0.002028          1.0                                    0.063718                                          1.0                             -0.000804                                    1.0                             -0.009617                                    1.0                                 -1.541453                                   0.170533
               oct_sucrose_mb_symmetrized                 oct_sucrose_appetitive_wt                    0.027126          1.0                                    0.090491                                          1.0                              0.006784                                    1.0                              0.003886                                    1.0                                 -0.594204                                   0.693157
            oct_sucrose_right_mb_silenced                 oct_sucrose_appetitive_wt                    0.038605          1.0                                    0.021276                                          1.0                              0.013804                                    1.0                             -0.004808                                    1.0                                 -1.114470                                   0.314646
             weak_oct_strong_mch_conflict                 oct_sucrose_appetitive_wt                   -0.000463          1.0                                    0.049847                                          1.0                              0.000080                                    1.0                             -0.012498                                    1.0                                 -1.087326                                   0.314646

## 解释

- `mean_approach_margin = d(CS-) - d(CS+)`，正值表示更接近 CS+，负值表示更接近 CS-。
- `expected_choice_rate` 根据条件预期计算：奖励条件预期选择 CS+，电击条件预期选择 CS-。
- `expected_choice_fdr_q` 是 expected choice 对 0.5 随机选择的二项检验 FDR 校正值。
- `mirror_sides=True` 时每个条件同时运行 CS+ 左侧与右侧，减少空间摆放对 MB 扰动比较的混杂。
- `mean_expected_laterality_index` 是按预期行为方向校正的横向位移除以路径长度；奖励任务朝 CS+ 为正，电击任务远离 CS+ 为正。
- `mean_early_expected_lateral_velocity` 是早期窗口内朝预期方向的横向速度，用于捕捉终点 choice rate 饱和前的转向差异。
- `mean_physical_laterality_index` 不按 CS+ 方向校正，保留真实左/右漂移，可用于发现 motor-side bias。

## 当前边界

本轮达到每条件 n>=50，可作为代理仿真的正式统计结果；但它仍然不是真实果蝇行为学证据。

如果需要重新运行正式代理仿真，建议使用：

```bash
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite_n50 \
  --n-trials 50 \
  --run-time 0.8 \
  --max-workers 4 \
  --mirror-sides
```

不能把本代理 screen 写成真实果蝇行为学显著性证据；它用于决定真实实验和更大规模仿真的优先条件。MB 扰动相对 WT 的差异需要优先查看 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_wt_comparisons.csv`，不能只看 expected choice 是否显著。
