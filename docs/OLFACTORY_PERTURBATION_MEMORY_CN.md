# 嗅觉输入扰动与长期记忆仿真实验报告

更新时间：2026-04-26T12:20:31

## 1. 目标

本实验专门处理“外界嗅觉输入”和“初始状态难以设置”的问题：把 CS+/CS- 强度、气味扩散指数、嗅源几何、左右嗅觉通道权重、初始位置和朝向都显式写入 condition table，并测试这些输入扰动如何影响赛博果蝇的短期/长期记忆行为。

## 2. 输入参数表

参数表路径：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/conditions/olfactory_condition_table.csv`

| name | memory_mode | attractive_gain | aversive_gain | lateral_memory_bias | cs_plus_intensity | cs_minus_intensity | diffuse_exponent | odor_y_offset | spawn_y | spawn_heading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| acute_balanced_memory | acute | -500 | 80 | 0 | 1 | 1 | 2 | 3 | 0 | 0 |
| long_term_memory_consolidated | long_term | -680 | 45 | 0.18 | 1 | 1 | 2.2 | 3 | 0 | 0 |
| long_term_memory_decay | long_term_decay | -220 | 25 | 0.05 | 1 | 1 | 1.8 | 3 | 0 | 0 |
| weak_odor_high_memory | weak_cue_retrieval | -720 | 40 | 0.22 | 0.35 | 0.35 | 2.4 | 3 | 0 | 0 |
| cs_plus_weak_conflict | sensory_memory_conflict | -650 | 60 | -0.18 | 0.28 | 1 | 2.1 | 3 | 0 | 0 |
| left_sensor_deprivation | sensory_asymmetry | -500 | 80 | 0.18 | 1 | 1 | 2 | 3 | 0 | 0 |
| right_sensor_deprivation | sensory_asymmetry | -500 | 80 | -0.18 | 1 | 1 | 2 | 3 | 0 | 0 |
| initial_state_mirror | initial_state_control | -500 | 80 | 0 | 1 | 1 | 2 | 3 | -1.5 | 0.25 |
| wide_plume_low_gradient | plume_geometry | -500 | 80 | 0 | 1 | 1 | 1.45 | 4.2 | 0 | 0 |
| narrow_plume_high_gradient | plume_geometry | -500 | 80 | 0 | 1 | 1 | 2.8 | 2.4 | 0 | 0 |

## 3. 核心发现

1. 嗅觉输入强度不是简单线性控制 choice rate：在当前几何下，二分类选择容易饱和或被初始状态影响，连续轨迹读出更稳。
2. `long_term_memory_consolidated` 与 `weak_odor_high_memory` 测试了长期记忆是否能补偿低气味强度，是最接近“长期记忆功能”的仿真条件。
3. `cs_plus_weak_conflict` 把 CS+ 设置为弱气味、CS- 设置为强气味，用于测试记忆能否战胜即时感觉输入；这个条件最适合设计真实行为学冲突实验。
4. `left_sensor_deprivation` 与 `right_sensor_deprivation` 用左右输入权重模拟单侧嗅觉通道受损，能够把嗅觉偏侧化和蘑菇体记忆偏侧化放到同一个因果框架里。
5. `initial_state_mirror` 让初始位置和朝向偏置显式化，用来避免把起点偏差误判为记忆偏侧化。

## 4. 最强行为条件

| condition | memory_mode | cs_plus_choice_rate | mean_approach_margin | mean_distance_to_cs_plus | mean_path_length | cs_plus_intensity | cs_minus_intensity | lateral_memory_bias |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wide_plume_low_gradient | plume_geometry | 1 | 8.219 | 1.205 | 10.6 | 1 | 1 | 0 |
| initial_state_mirror | initial_state_control | 1 | 5.366 | 3.133 | 14.86 | 1 | 1 | 0 |
| long_term_memory_decay | long_term_decay | 1 | 5.299 | 2.824 | 14.87 | 1 | 1 | 0.05 |
| left_sensor_deprivation | sensory_asymmetry | 1 | 5.08 | 2.825 | 14.81 | 1 | 1 | 0.18 |
| weak_odor_high_memory | weak_cue_retrieval | 1 | 5.033 | 2.821 | 14.81 | 0.35 | 0.35 | 0.22 |
| narrow_plume_high_gradient | plume_geometry | 1 | 4.514 | 2.012 | 10.25 | 1 | 1 | 0 |
| right_sensor_deprivation | sensory_asymmetry | 0.8333 | 4.078 | 2.928 | 14.55 | 1 | 1 | -0.18 |
| acute_balanced_memory | acute | 0.8333 | 3.993 | 3.042 | 14.82 | 1 | 1 | 0 |

## 5. 易失败/冲突条件

| condition | memory_mode | cs_plus_choice_rate | mean_approach_margin | cs_minus_count | cs_plus_intensity | cs_minus_intensity | diffuse_exponent | biological_interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cs_plus_weak_conflict | sensory_memory_conflict | 0.8333 | 3.784 | 1 | 0.28 | 1 | 2.1 | weak CS+ cue competes with stronger CS- sensory plume |
| long_term_memory_consolidated | long_term | 0.8333 | 3.967 | 1 | 1 | 1 | 2.2 | stronger consolidated CS+ drive with reduced aversive interference |
| acute_balanced_memory | acute | 0.8333 | 3.993 | 1 | 1 | 1 | 2 | balanced acute odor-memory reference |
| right_sensor_deprivation | sensory_asymmetry | 0.8333 | 4.078 | 1 | 1 | 1 | 2 | right olfactory channel deprivation with intact left channel |
| narrow_plume_high_gradient | plume_geometry | 1 | 4.514 | 0 | 1 | 1 | 2.8 | narrow steep plume emphasizes sensory input precision |
| weak_odor_high_memory | weak_cue_retrieval | 1 | 5.033 | 0 | 0.35 | 0.35 | 2.4 | long-term memory compensates for low odor concentration |
| left_sensor_deprivation | sensory_asymmetry | 1 | 5.08 | 0 | 1 | 1 | 2 | left olfactory channel deprivation with intact right channel |
| long_term_memory_decay | long_term_decay | 1 | 5.299 | 0 | 1 | 1 | 1.8 | forgetting or weak retrieval after memory decay |

## 6. 长视频

长视频路径：

- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_left_long.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/videos/olfactory_perturbation_cs_plus_right_long.mp4`

逐条件渲染摘要：

| condition | memory_mode | cs_plus_side | choice | signed_final_y | distance_to_cs_plus | distance_to_cs_minus | video_duration_s | render_device |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| acute_balanced_memory | acute | left | CS- | -1.843 | 5.130 | 2.049 | 16.500 | 0 |
| acute_balanced_memory | acute | right | CS+ | 7.374 | 5.605 | 10.950 | 16.500 | 1 |
| cs_plus_weak_conflict | sensory_memory_conflict | left | CS- | -2.318 | 5.368 | 1.001 | 16.500 | 0 |
| cs_plus_weak_conflict | sensory_memory_conflict | right | CS+ | 6.937 | 5.259 | 10.531 | 16.500 | 1 |
| initial_state_mirror | initial_state_control | left | CS+ | 6.489 | 5.606 | 10.454 | 16.500 | 2 |
| initial_state_mirror | initial_state_control | right | CS+ | 9.397 | 6.577 | 12.491 | 16.500 | 3 |
| left_sensor_deprivation | sensory_asymmetry | left | CS+ | 4.668 | 5.232 | 9.132 | 16.500 | 2 |
| left_sensor_deprivation | sensory_asymmetry | right | CS+ | 6.152 | 5.461 | 10.181 | 16.500 | 3 |
| long_term_memory_consolidated | long_term | left | CS- | -2.050 | 5.389 | 2.108 | 16.500 | 2 |
| long_term_memory_consolidated | long_term | right | CS+ | 8.200 | 5.857 | 11.520 | 16.500 | 3 |
| long_term_memory_decay | long_term_decay | left | CS+ | 8.323 | 5.655 | 11.483 | 16.500 | 0 |
| long_term_memory_decay | long_term_decay | right | CS+ | 4.633 | 5.256 | 9.123 | 16.500 | 1 |
| right_sensor_deprivation | sensory_asymmetry | left | CS- | -1.914 | 5.086 | 1.701 | 16.500 | 0 |
| right_sensor_deprivation | sensory_asymmetry | right | CS+ | 8.206 | 5.903 | 11.546 | 16.500 | 1 |
| weak_odor_high_memory | weak_cue_retrieval | left | CS+ | 4.615 | 5.204 | 9.081 | 16.500 | 2 |
| weak_odor_high_memory | weak_cue_retrieval | right | CS+ | 6.206 | 5.350 | 10.154 | 16.500 | 3 |

## 7. 生物学假说

1. 长期记忆的可发表读出不应只看是否选择 CS+，而应看低浓度气味下是否仍能保持接近 margin 和更短路径。
2. 如果 `cs_plus_weak_conflict` 在真实行为实验中仍偏向 CS+，说明蘑菇体记忆轴能覆盖外周感觉强度差；如果失败，则说明感觉强度是边界条件。
3. 单侧嗅觉 deprivation 与左右蘑菇体侧化联用，可以测试“感觉输入侧化”和“记忆轴侧化”是否可分离。
4. 初始状态 mirror control 是必要对照：没有它，左右行为差异可能只是初始位姿造成的。

## 8. 输出文件

- screen trial：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/screen_trials/memory_choice_summary.csv`
- rendered trial：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/rendered_trials/memory_choice_summary.csv`
- aggregate summary：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/olfactory_behavior_summary.csv`
- figure：`/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite/figures/Fig_olfactory_perturbation_summary.png`

## 9. 一键复现

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
python /unify/ydchen/unidit/bio_fly/scripts/run_olfactory_perturbation_suite.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite \
  --render-devices 0 1 2 3 \
  --screen-trials 2 \
  --screen-run-time 0.9 \
  --render-run-time 2.0 \
  --camera-play-speed 0.12
```

## 10. 限制

当前实现是具身行为代理模型，不是完整 ORN/PN/LH/MB spiking 闭环。它适合提出嗅觉输入、长期记忆和偏侧化之间的可检验预测；最终发表还需要真实行为学、外周嗅觉控制、长期记忆时间窗和遗传操控验证。
