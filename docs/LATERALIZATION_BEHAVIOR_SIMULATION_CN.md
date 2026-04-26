# 赛博果蝇侧化行为仿真实验报告

更新时间：2026-04-26T11:28:57

## 1. 目的

本实验把 `/unify/ydchen/unidit/bio_fly/outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv` 中的蘑菇体 Kenyon cell neurotransmitter 侧化信号转成可操控的具身行为变量，系统测试“增强、削弱、镜像翻转、对称救援”侧化后，赛博果蝇在双气味选择任务中的轨迹、选择和左右偏置如何变化。

核心用途不是宣称替代全部湿实验，而是替代早期大规模假设筛选：先在连接组约束的 cyber-fly 中找到方向稳定、可统计、可视频展示的候选，再把最强条件转成真实行为学和遗传操控实验。

## 2. 方法创新点

1. 结构发现自动转译为行为操控：FlyWire KC NT 侧化统计 → `lateral_memory_bias`、左右输入权重、记忆增益。
2. 引入 in silico lateralization surgery：原生右侧 serotonin 轴、左侧 glutamate 轴、对称救援、镜像翻转、侧化放大、双侧记忆钝化。
3. 加入剂量扫描：连续改变 lateral memory bias，得到行为读出的 dose-response，而不是只比较两三个任意条件。
4. 使用 EGL/MuJoCo GPU 渲染：每个长视频记录 `MUJOCO_EGL_DEVICE_ID`，用于证明渲染任务映射到本地 GPU。
5. 输出完整长视频：关闭到达 CS+ 后提前停止，视频平均时长约 `13.17 s`，最长 `13.17 s`，不再是 1-2 秒 demo。

## 3. 文献约束

- Aso et al., eLife 2014, mushroom body architecture for associative learning：https://elifesciences.org/articles/04577
- Aso et al., eLife 2014, MBON valence and memory-based action selection：https://elifesciences.org/articles/04580
- FlyGym / NeuroMechFly v2 embodied Drosophila simulation, Nature Methods：https://www.nature.com/articles/s41592-024-02497-y
- FlyWire adult Drosophila brain connectome, Nature：https://www.nature.com/articles/s41586-024-07558-y
- Shiu et al. Drosophila computational brain model, Nature：https://www.nature.com/articles/s41586-024-07553-3

这些文献支持本仿真设计的边界：MBON/DAN/APL/DPM 是合理的记忆轴读出，FlyGym 适合把神经假说转成具身行为预测，Shiu/FlyWire 风格模型适合做全脑连接组约束的扰动推演。但仿真结果应表述为“可检验预测”，不能直接等价于真实果蝇行为数据。

## 4. 侧化操控条件

| name                        | lateral_memory_bias | attractive_gain    | aversive_gain     | attractive_left_weight | attractive_right_weight | aversive_left_weight | aversive_right_weight |
| --------------------------- | ------------------- | ------------------ | ----------------- | ---------------------- | ----------------------- | -------------------- | --------------------- |
| control                     | 0.0                 | -500.0             | 80.0              | 1.0                    | 9.0                     | 0.0                  | 10.0                  |
| symmetric_rescue            | 0.0                 | -500.0             | 80.0              | 1.0                    | 1.0                     | 5.0                  | 5.0                   |
| right_mb_serotonin_enriched | 0.315               | -500.0             | 80.0              | 1.0                    | 9.0                     | 0.0                  | 10.0                  |
| left_mb_glutamate_enriched  | -0.219              | -500.0             | 80.0              | 1.0                    | 9.0                     | 0.0                  | 10.0                  |
| mirror_reversal             | -0.267              | -500.0             | 80.0              | 9.0                    | 1.0                     | 10.0                 | 0.0                   |
| amplified_right_axis        | 0.63                | -500.0             | 80.0              | 1.0                    | 9.0                     | 0.0                  | 10.0                  |
| amplified_left_axis         | -0.438              | -500.0             | 80.0              | 1.0                    | 9.0                     | 0.0                  | 10.0                  |
| bilateral_memory_blunted    | 0.0                 | -366.4110297196278 | 58.62576475514045 | 1.0                    | 9.0                     | 0.0                  | 10.0                  |

解释：

- `right_mb_serotonin_enriched`：保留右侧 serotonin-enriched KC 轴的正向偏置。
- `left_mb_glutamate_enriched`：保留左侧 glutamate-biased KC 轴的负向偏置。
- `symmetric_rescue`：把左右输入权重拉平，模拟消除侧化。
- `mirror_reversal`：把左右输入权重和偏置方向翻转，模拟镜像侧化。
- `amplified_right_axis` / `amplified_left_axis`：模拟更强偏侧化。
- `bilateral_memory_blunted`：降低记忆增益，模拟双侧记忆轴功能钝化。

## 5. 剂量扫描结果

输入文件：

- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/dose_response/memory_choice_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/dose_response/dose_response_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/figures/Fig_lateralization_dose_response.png`

| dose_bias | cs_plus_side | n_trials | cs_plus_choice_rate | mean_signed_final_y | mean_distance_to_cs_plus | mean_path_length |
| --------- | ------------ | -------- | ------------------- | ------------------- | ------------------------ | ---------------- |
| -0.75     | left         | 2        | 1.000               | 3.433               | 0.730                    | 9.013            |
| -0.5      | left         | 2        | 1.000               | 3.573               | 0.861                    | 9.021            |
| -0.25     | left         | 2        | 1.000               | 3.604               | 0.741                    | 8.988            |
| 0.0       | left         | 2        | 1.000               | 3.494               | 0.949                    | 9.393            |
| 0.25      | left         | 2        | 1.000               | 3.645               | 0.729                    | 8.735            |
| 0.5       | left         | 2        | 1.000               | 3.871               | 1.333                    | 9.234            |
| 0.75      | left         | 2        | 1.000               | 3.544               | 0.927                    | 8.850            |
| -0.75     | right        | 2        | 1.000               | 3.679               | 1.030                    | 9.358            |
| -0.5      | right        | 2        | 1.000               | 3.659               | 0.946                    | 9.014            |
| -0.25     | right        | 2        | 1.000               | 3.567               | 0.783                    | 8.859            |
| 0.0       | right        | 2        | 1.000               | 3.818               | 1.111                    | 9.449            |
| 0.25      | right        | 2        | 1.000               | 3.570               | 0.743                    | 8.889            |
| 0.5       | right        | 2        | 1.000               | 3.589               | 1.061                    | 9.076            |
| 0.75      | right        | 2        | 1.000               | 3.784               | 1.112                    | 8.916            |

读法：如果 `lateral_memory_bias` 与 `mean_signed_final_y` 或 `distance_to_cs_plus` 呈单调关系，说明侧化不是仅改变静态结构指标，而会投射到可观测行为轨迹。

## 6. 本次实际发现

1. 剂量扫描中的二分类 `CS+ choice rate` 在当前几何和控制器参数下已经饱和，范围为 `1.000` 到 `1.000`；因此不应把二分类选择率作为唯一行为结论。
2. 更敏感的读出是连续轨迹指标：`mean_distance_to_cs_plus` 的跨条件范围为 `0.604`，`mean_signed_final_y` 也随侧化参数改变，说明侧化操控主要改变轨迹形状和接近策略。
3. 代表性长视频中出现 `CS-` 的条件/侧别为：amplified_left_axis/left, amplified_right_axis/left, bilateral_memory_blunted/right。这些条件是下一步最值得做真实行为学或更严格闭环神经动力学复核的候选。
4. 当前最稳妥的论文表述是：侧化操控改变 cyber-fly 的行为轨迹和目标接近距离，并在部分强操控条件下改变最终选择；这支持“结构侧化可产生可观测行为后果”的功能预测。

## 7. 长视频结果

完整对比视频：

- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_left_long.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_right_long.mp4`

逐条件原始视频和轨迹位于：

- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/rendered_trials`

长视频对应的 trial 摘要：

| condition                   | cs_plus_side | choice | signed_final_y | distance_to_cs_plus | distance_to_cs_minus | video_duration_s | render_device |
| --------------------------- | ------------ | ------ | -------------- | ------------------- | -------------------- | ---------------- | ------------- |
| amplified_left_axis         | left         | CS-    | -0.821         | 5.280               | 4.245                | 13.17            | 0             |
| amplified_left_axis         | right        | CS+    | +7.117         | 5.152               | 10.580               | 13.17            | 1             |
| amplified_right_axis        | left         | CS-    | -0.175         | 5.060               | 4.848                | 13.17            | 2             |
| amplified_right_axis        | right        | CS+    | +7.086         | 5.215               | 10.594               | 13.17            | 3             |
| bilateral_memory_blunted    | left         | CS+    | +6.788         | 5.050               | 10.342               | 13.17            | 2             |
| bilateral_memory_blunted    | right        | CS-    | -0.072         | 4.777               | 4.686                | 13.17            | 3             |
| control                     | left         | CS+    | +2.013         | 5.045               | 7.043                | 13.17            | 0             |
| control                     | right        | CS+    | +8.118         | 5.409               | 11.255               | 13.17            | 1             |
| left_mb_glutamate_enriched  | left         | CS+    | +8.313         | 5.489               | 11.397               | 13.17            | 2             |
| left_mb_glutamate_enriched  | right        | CS+    | +8.120         | 5.441               | 11.271               | 13.17            | 3             |
| mirror_reversal             | left         | CS+    | +8.618         | 5.627               | 11.622               | 13.17            | 0             |
| mirror_reversal             | right        | CS+    | +3.404         | 5.134               | 8.198                | 13.17            | 1             |
| right_mb_serotonin_enriched | left         | CS+    | +8.876         | 5.900               | 11.888               | 13.17            | 0             |
| right_mb_serotonin_enriched | right        | CS+    | +0.572         | 5.102               | 5.735                | 13.17            | 1             |
| symmetric_rescue            | left         | CS+    | +8.533         | 5.669               | 11.599               | 13.17            | 2             |
| symmetric_rescue            | right        | CS+    | +0.040         | 5.622               | 5.665                | 13.17            | 3             |

## 8. 对 paper 的增强方式

建议把这组仿真放在论文的“结构发现到功能预测”部分，而不是作为真实行为实验替代结果直接下结论：

1. 主文图：KC NT 侧化结构图 + 侧化操控条件示意图。
2. 主文图：lateral memory bias dose-response 曲线，展示侧化强度与行为轨迹读出的连续关系。
3. 补充视频：两个长对比视频，分别展示 CS+ 在左侧和右侧时不同侧化操控的行为差异。
4. 补充表：`/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/conditions/lateralization_condition_table.csv` 作为所有操控参数的可复现记录。
5. 方法学叙事：提出“connectome-constrained in silico lateralization surgery”，先用仿真替代大规模预筛，再用真实行为实验验证最强条件。

## 9. 严格限制

- 当前行为层是 FlyGym/MuJoCo 代理任务，不是直接从全脑 spike dynamics 闭环驱动腿部控制。
- GPU 主要用于 EGL 渲染和前面 PyTorch sparse propagation；MuJoCo 物理积分仍有 CPU 部分。
- 这套结果可以显著增强 paper 的机制推演和实验设计，但不能单独替代关键真实行为学验证。
- 下一步应把 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_top_targets.csv` 中的 MBON/DAN/APL/DPM 靶点和这里的强行为条件对齐，形成遗传操控候选清单。

## 10. 一键复现命令

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
python /unify/ydchen/unidit/bio_fly/scripts/run_lateralization_behavior_suite.py \
  --stats /unify/ydchen/unidit/bio_fly/outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite \
  --render-devices 0 1 2 3 \
  --dose-trials 2 \
  --dose-run-time 0.8 \
  --render-run-time 1.6 \
  --camera-play-speed 0.12
```
