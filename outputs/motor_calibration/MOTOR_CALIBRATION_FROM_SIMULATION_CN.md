# 从仿真轨迹生成 motor calibration table 的报告

保存路径：`/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/MOTOR_CALIBRATION_FROM_SIMULATION_CN.md`

## 目的

上一版 inverse motor fitting 使用默认行为 motif 标签。本轮把标签来源升级为已有仿真输出：食物气味轨迹、视觉目标跟踪轨迹、梳理代理时间序列，以及 gustatory connectome readout。这样 DN-to-motor 替代接口不再完全依赖手工设定，而是开始由项目内已有行为数据校准。

## 校准表

校准表保存于：`/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv`

              condition  forward_drive  turning_drive  feeding_drive  grooming_drive  visual_steering_drive                                                     label_source            evidence_level                                                calibration_notes
  olfactory_food_memory       0.743884       0.603642       0.944602        0.030000                   0.05                     derived_from_food_memory_flygym_trajectories embodied_trajectory_proxy  mean_margin=5.7841; mean_path_length=8.9266; choice_rate=1.0000
 visual_object_tracking       0.688239       0.012953       0.020000        0.030000                   0.00                    derived_from_visual_tracking_proxy_trajectory   visual_proxy_trajectory distance_start=29.4600; distance_end=105.4670; mean_speed=2.0647
      gustatory_feeding       0.120000       0.080000       0.803024        0.138312                   0.02 derived_from_gustatory_connectome_readout_no_proboscis_mechanics     connectome_proxy_only            gustatory_abs_mass=0.2253; descending_abs_mass=0.2554
mechanosensory_grooming       0.080000       0.180000       0.030000        0.827428                   0.02                          derived_from_grooming_proxy_time_series      embodied_motor_proxy           mean_grooming_drive=0.5069; peak_grooming_drive=1.0000

## 交叉验证误差

               target  leave_one_out_mae
        feeding_drive           0.681158
        forward_drive           0.248337
       grooming_drive           0.358318
        turning_drive           0.248008
visual_steering_drive           0.025188

## 证据等级

- `embodied_trajectory_proxy`：来自 FlyGym/FlyGym-like 轨迹，可用于行为代理校准。
- `visual_proxy_trajectory`：来自视觉目标跟踪代理轨迹，当前若 FlyGym 原生视觉接口失败，则仍是 proxy。
- `embodied_motor_proxy`：来自身体动作代理时间序列，例如前足梳理节律。
- `connectome_proxy_only`：只来自连接组 readout，尚无完整身体动力学。当前 `gustatory_feeding` 属于此类，因为还没有完整 proboscis mechanics。

## 严谨结论

本轮实现说明“逆向拟合接口层”可以被已有仿真行为数据校准，而不是只能依靠默认标签。它仍然不是 Eon 私有 DN-to-motor 权重，也不是最终生物实验证据；但它已经是一个可替换、可审计、可逐步引入真实行为数据的接口层。

## 输出

- 逆向拟合训练表：`/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/inverse_motor_training_table.csv`
- 逆向拟合系数：`/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/inverse_motor_interface_coefficients.csv`
- 逆向拟合预测：`/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/inverse_motor_interface_predictions.csv`
- 留一法交叉验证：`/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/inverse_motor_interface_leave_one_out_cv.csv`
- 拟合图：`/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/figures/Fig_inverse_motor_interface.png`
- 拟合报告：`/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/INVERSE_MOTOR_INTERFACE_CN.md`
