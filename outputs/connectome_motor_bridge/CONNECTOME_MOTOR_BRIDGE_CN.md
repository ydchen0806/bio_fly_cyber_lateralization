# Calibrated connectome motor interface 接入行为仿真报告

保存路径：`/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/CONNECTOME_MOTOR_BRIDGE_CN.md`

## 目的

本轮把 `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv` 中的 calibrated motor targets 接到 OCT/MCH 行为仿真参数。输出表可直接被现有 FlyGym 记忆行为仿真读取，形成：

`OCT/MCH 条件表 -> calibrated motor target -> MemoryCondition -> FlyGym memory choice trial`

## 条件参数

                                     name             cs_plus_odor            cs_minus_odor unconditioned_stimulus                mb_perturbation  attractive_gain  aversive_gain  lateral_memory_bias
                oct_sucrose_appetitive_wt            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward           wild_type_connectome      -728.067594      40.911378             0.062185
mch_sucrose_appetitive_wt_counterbalanced MCH_4-methylcyclohexanol            OCT_3-octanol         sucrose_reward           wild_type_connectome      -728.067594      40.911378             0.062185
                    oct_shock_aversive_wt            OCT_3-octanol MCH_4-methylcyclohexanol         electric_shock           wild_type_connectome       556.354488     218.784829            -0.062185
             oct_sucrose_left_mb_silenced            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward              left_MB_gain_0.25      -728.067594      40.911378            -0.217815
            oct_sucrose_right_mb_silenced            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward             right_MB_gain_0.25      -728.067594      40.911378             0.342185
               oct_sucrose_mb_symmetrized            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward left_right_MB_weights_averaged      -728.067594      40.911378             0.000000
                   oct_sucrose_mb_swapped            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward  left_right_MB_weights_swapped      -728.067594      40.911378            -0.062185
             weak_oct_strong_mch_conflict            OCT_3-octanol MCH_4-methylcyclohexanol         sucrose_reward           wild_type_connectome      -728.067594      40.911378             0.062185

## 解释边界

这里的 `attractive_gain`、`aversive_gain` 和 `lateral_memory_bias` 是公开替代接口推导出的行为参数，不是 Eon 私有 DN-to-motor 权重。它用于把连接组 readout 变成可运行假说，而不是替代真实生物实验证据。

## 输出

- 条件表：`/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv`
