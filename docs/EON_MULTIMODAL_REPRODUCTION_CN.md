# Eon/CyberFly 多模态复现实验与严谨边界报告

保存路径：`/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/EON_MULTIMODAL_REPRODUCTION_CN.md`

## 原文复现边界

Eon 的公开说明页为 `https://eon.systems/updates/embodied-brain-emulation`。该系统不是“只给连接组就自动涌现全部果蝇行为”的纯端到端模型，而是整合了四层组件：

1. Shiu 等 FlyWire 全脑 LIF 模型，用连接组传播感觉扰动。
2. 视觉模型和嗅觉/机械/味觉输入接口。
3. descending neuron 或少数运动神经元读出。
4. NeuroMechFly/FlyGym 身体和低维运动控制器；walking 使用已有 imitation-learned controller，其他行为也依赖特定 readout 与控制接口。

因此，本项目现在采用同样分层标准复现：连接组响应、readout 映射、身体代理行为和视频，而不是把低维控制器的行为误称为“连接组自动涌现”。

## 本轮实现的多模态测试

- 气味/食物记忆：`CS+` 为糖奖励相关气味，`CS-` 为中性或诱饵气味。
- 视觉：FlyGym retina + moving object arena + visual taxis controller，测试 moving object tracking。
- 味觉/feeding：gustatory sensory channel 的连接组 readout；当前没有完整 proboscis mechanics，因此作为 feeding proxy。
- 机械感觉/梳理：mechanosensory channel 的连接组 readout + NeuroMechFly 前足 rhythmic grooming proxy。

## 连接组 readout 摘要

              condition                                                                                biological_input                                                                   expected_behavior  n_seed_neurons  active_response_neurons  absolute_mass  positive_mass  negative_mass  descending_abs_mass  descending_signed_mass  memory_axis_abs_mass  memory_axis_signed_mass  visual_projection_abs_mass  visual_projection_signed_mass  gustatory_abs_mass  gustatory_signed_mass  mechanosensory_abs_mass  mechanosensory_signed_mass
  olfactory_food_memory                                ORN olfactory sensory neurons representing food-associated odour                                               approach learned CS+ food/sugar odour             255                     7376       2.664589       2.427158      -0.237430             0.011488                0.010349              0.245349                 0.245190                    1.320785                       0.922793            0.000028               0.000028                 0.000000                    0.000000
 visual_object_tracking            LC/LPLC visual projection neurons representing moving object or looming visual input orient or steer toward visual target; looming-related DN readout is not full escape             255                    11152       1.577666       0.896018      -0.681648             0.203957                0.058669              0.075750                -0.066276                    0.885637                       0.085317            0.005476              -0.001517                 0.005376                   -0.002836
      gustatory_feeding                                      gustatory sensory neurons representing sugar/taste contact     feeding/proboscis-extension proxy; full proboscis mechanics are not implemented             256                     6895       1.645239       0.760617      -0.884621             0.255412                0.003148              0.004189                 0.003766                    0.945583                      -0.257589            0.225318              -0.182848                 0.118458                   -0.112964
mechanosensory_grooming mechanosensory Johnston-organ/bristle-like neurons representing dust/contact on head or antenna                                                            front-leg grooming proxy             256                     7802       1.878642       1.155701      -0.722941             0.463450                0.203777              0.001634                -0.001634                    1.111238                       0.171484            0.027579              -0.025050                 0.146880                   -0.109450

## 输出文件

- 连接组 readout 表：`/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_readout_summary.csv`
- top targets：`/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_top_targets.csv`
- readout 热图：`/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_connectome_multimodal_readout_heatmap.png`
- top class 图：`/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/figures/Fig_eon_top_target_classes.png`
- 食物/气味视频左：`/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`
- 食物/气味视频右：`/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`
- 视觉目标跟踪视频：`/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/videos/eon_visual_object_tracking.mp4`
- 梳理代理视频：`/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/videos/eon_mechanosensory_front_leg_grooming_proxy.mp4`
- 多模态总览视频：`/unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/videos/eon_multimodal_reproduction_summary.mp4`

## 对 Nature 级叙事最重要的结论

当前可以严谨地写：FlyWire 连接组约束的多模态 readout 能把不同感觉输入映射到不同下游类别，并通过 FlyGym/NeuroMechFly 低维控制器生成可解释行为代理。对于我们的论文，最有生物意义的是把蘑菇体左右侧化从静态结构推进到食物气味记忆任务，并用视觉、味觉和机械感觉作为“不是只会跑一个气味任务”的系统性对照。

当前不能写：连接组单独自动涌现了完整觅食、视觉逃逸、进食和梳理行为。这个结论需要完整 DN-to-motor 映射、真实训练权重、行为级定量复现和跨个体验证。

## 下一步严格目标

1. 用原文相同 DN 列表和参数复现 DN response traces。
2. 用同一组 sensory neuron IDs 复现 feeding、grooming、steering 的响应排序。
3. 把 grooming proxy 替换成可验证的前足/头部接触动力学。
4. 对视觉 looming 做 escape DN readout 和真实转向/冻结/逃逸行为，而不是只做 object tracking。
5. 用真实行为数据校准 CS+/CS- 食物记忆模型。

## 追加：DN 行为接口复核

新增脚本 `/unify/ydchen/unidit/bio_fly/scripts/run_dn_behavior_readout_analysis.py` 对多模态传播结果做了 descending-neuron 家族分析。这个分析非常重要，因为 Eon/CyberFly 类系统真正连接脑和身体的接口不是任意全脑响应，而是从脑部下行到腹神经索的 DN。

输出文件：

- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_behavior_readout_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_family_readout_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_side_laterality_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/dn_top_targets_by_condition.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_family_readout_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_laterality_index.png`
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/figures/Fig_dn_side_mass_stacked.png`
- `/unify/ydchen/unidit/bio_fly/outputs/dn_behavior_readout/videos/dn_multimodal_mechanism_summary.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/dn_multimodal_mechanism_summary.mp4`

主要结果：

| condition | recruited DN | DN abs mass | laterality index | top DN family | top-family fraction |
|---|---:|---:|---:|---|---:|
| `olfactory_food_memory` | 58 | 0.011488 | +0.049 | `DNge` | 0.282 |
| `visual_object_tracking` | 704 | 0.203957 | -0.098 | `DNg` | 0.299 |
| `gustatory_feeding` | 638 | 0.255412 | -0.103 | `DNge` | 0.514 |
| `mechanosensory_grooming` | 769 | 0.463450 | -0.033 | `DNg` | 0.510 |

解释：嗅觉食物记忆条件的 DN mass 很低，说明该任务更像是先在蘑菇体/脑内记忆轴完成状态计算，再较弱地进入下行运动接口；视觉、味觉和机械感觉条件则更强地招募 DN，尤其 `DNg`、`DNge` 和 `DNp`，更符合直接转向、梳理、姿态和进食候选动作接口。

严谨边界：DN 家族分析显著加强了“连接组约束行为接口”的证据，但它仍然是功能预测，不是因果证明。Nature 级别最终证据需要把这些 DN 家族作为真实实验靶点，进行单侧或家族级干预、钙成像/电生理读出和 CS+/CS- 行为学验证。
