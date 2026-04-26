# 逆向拟合 DN-to-motor 接口层可行性报告

保存路径：`/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/INVERSE_MOTOR_INTERFACE_CN.md`

## 结论摘要

本轮已经实现一个可运行的“逆向拟合接口层”原型。它用公开连接组传播得到的多模态 readout 特征，拟合到低维行为控制目标：前进、转向、进食、梳理和视觉转向。该层可以作为接近 Eon 闭环系统的替代方案，但必须在论文中称为 `surrogate motor interface`，不能声称是 Eon 私有 DN-to-motor 权重。

当前训练样本数为 `4` 个感觉/行为条件，岭回归正则强度 `alpha = 0.2`。样本量很小，因此它适合做工程闭环和图表演示，不足以单独支撑 Nature 级统计结论。Nature 级证据需要后续加入真实行为轨迹、公开神经元级 DN 标签、更多条件和湿实验验证。

## 输入变量

- `descending_abs_mass`：感觉扰动经连接组传播到 descending neuron 类神经元的总绝对响应量，近似表示脑到身体接口的招募强度。
- `descending_signed_mass`：descending neuron 响应的带符号总和，近似表示净兴奋/抑制方向。
- `memory_axis_abs_mass`：KC、MBON、DAN、APL、DPM 等记忆相关轴的总响应量。
- `memory_axis_signed_mass`：记忆轴带符号响应。
- `visual_projection_abs_mass` / `visual_projection_signed_mass`：视觉投射相关通路响应。
- `gustatory_abs_mass` / `gustatory_signed_mass`：味觉/糖接触相关通路响应。
- `mechanosensory_abs_mass` / `mechanosensory_signed_mass`：机械感觉/接触相关通路响应。

## 输出变量

- `forward_drive`：前进/趋近驱动，数值越高表示越倾向持续行走。
- `turning_drive`：左右转向或轨迹修正驱动，数值越高表示越需要方向控制。
- `feeding_drive`：进食或 proboscis extension proxy 驱动。
- `grooming_drive`：梳理动作驱动。
- `visual_steering_drive`：视觉目标跟踪或视觉诱导转向驱动。

## 误差摘要

               target  training_mae  leave_one_out_mae
        feeding_drive      0.009139           0.644893
        forward_drive      0.003054           0.219888
       grooming_drive      0.006552           0.411317
        turning_drive      0.006402           0.408964
visual_steering_drive      0.009980           0.649956

## 训练条件

              condition                                                                                biological_input                                                                   expected_behavior                        label_source
  olfactory_food_memory                                ORN olfactory sensory neurons representing food-associated odour                                               approach learned CS+ food/sugar odour       CS+ food-odour approach motif
 visual_object_tracking            LC/LPLC visual projection neurons representing moving object or looming visual input orient or steer toward visual target; looming-related DN readout is not full escape    moving-object visual taxis motif
      gustatory_feeding                                      gustatory sensory neurons representing sugar/taste contact     feeding/proboscis-extension proxy; full proboscis mechanics are not implemented   sugar/taste contact feeding motif
mechanosensory_grooming mechanosensory Johnston-organ/bristle-like neurons representing dust/contact on head or antenna                                                            front-leg grooming proxy head/antenna contact grooming motif

## 输出文件

- 训练表：`/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_training_table.csv`
- 接口系数：`/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_interface_coefficients.csv`
- 训练集预测：`/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_interface_predictions.csv`
- 留一法交叉验证：`/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_interface_leave_one_out_cv.csv`
- 图：`/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/figures/Fig_inverse_motor_interface.png`

## 严谨边界

1. 这里拟合的是公开可审计的替代接口，不是 Eon 内部接口。
2. 默认标签来自行为 motif 约束，而不是真实果蝇逐帧标注，因此只用于工程原型和假说生成。
3. 该接口已经能把 olfactory、visual、gustatory、mechanosensory 四类 readout 映射到不同 motor motif，但样本数只有四个，留一法误差只能作为 sanity check。
4. 下一步应把真实行为数据或更大规模 FlyGym/NeuroMechFly rollout 结果加入 `target_table_path`，再重新拟合并报告独立测试集误差。

## 对论文的用法

可以写：我们实现了一个 connectome-readout-constrained surrogate motor interface，用于把公开连接组传播结果接入 embodied 行为仿真，并通过留一法和消融实验评估接口稳定性。

不能写：我们通过逆向拟合恢复了 Eon 的真实 DN-to-motor 权重。
