# OCT/MCH 镜像摆放与早期转向动力学正式报告

保存路径：`/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_MIRROR_KINEMATICS_CN.md`

## 目的

上一轮 OCT/MCH `n=50` 仿真已经证明 calibrated connectome-motor bridge 能稳定表达奖励趋近、惩罚回避和弱 CS+ 冲突下的记忆方向。但是，某些 MB 扰动条件的 `CS+` 在左侧，另一些条件的 `CS+` 在右侧，直接比较终点 `approach_margin` 会混入空间摆放因素。

本轮新增 `mirror_sides=True` 正式套件：每一个条件都同时运行 `CS+` 左侧和 `CS+` 右侧。这样每个条件有 `50` 个 nominal-side seeds 和 `50` 个 mirror-side seeds，总计 `100` 条轨迹；8 个条件总计 `800` 条短时程 FlyGym/MuJoCo 试验。

## 运行命令

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50 \
  --n-trials 50 \
  --run-time 0.2 \
  --max-workers 4 \
  --mirror-sides
```

本轮输出目录：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_trials.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_condition_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_wt_comparisons.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/figures/Fig_oct_mch_formal_suite.png`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/OCT_MCH_FORMAL_SUITE_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/suite_metadata.json`

## 2026-04-27 新增 mirror-side 论文视频

本轮新增一个独立渲染预览目录，用于生成 paper 级补充视频：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview`

该目录不是新的正式显著性统计，而是每个条件、每个 side 各 1 条渲染 trial。视频中右下角统计 inset 仍然引用本报告的正式 `n=100` mirror-side 统计结果。

新增视频：

- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_key_conditions.mp4`：四个核心条件，左右 mirror-side 成对展示。适合作为论文补充视频主入口。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_mb_perturbations.mp4`：WT 与四个 MB 扰动条件成对展示。适合说明“当前 MB 扰动相对 WT 未达到 FDR 显著”的负结果边界。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_cs_plus_left.mp4`：所有 8 个条件在 `CS+` 左侧时的代表性轨迹。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_cs_plus_right.mp4`：所有 8 个条件在 `CS+` 右侧时的代表性轨迹。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_full_both_sides.mp4`：所有 8 个条件、左右两种摆放的 16-panel 全量视频。

视频说明文档：

- `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_ASSAY_VIDEO_RENDERING_CN.md`

视频 QC：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_video_qc.json`
- 所有合成视频均为 `146` 帧、`30` fps；核心视频分辨率为 `1920x720`，全量 16-panel 视频为 `1920x1440`，MB perturbation 视频为 `2400x720`。
- 首帧像素方差均大于 `3300`，说明没有黑屏或空白写入。

画面变量解释：

- `OCT` 是 3-octanol，`MCH` 是 4-methylcyclohexanol。
- `CS+` 是训练时与糖奖励或电击配对的气味，`CS-` 是未配对对照气味。
- `US=sucrose` 表示糖奖励，预期行为是趋近 `CS+`。
- `US=shock` 表示电击惩罚，预期行为是回避 `CS+`、转向 `CS-`。
- 绿色圆点是起点，粉色线是 trajectory CSV 计算出的轨迹尾迹，黑白圆点是当前轨迹位置。
- 右下角 inset 的 `expected choice`、`q`、`approach margin` 和 `vs WT` 来自 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50`，不是单条视频 trial。

新增运行命令见 `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_ASSAY_VIDEO_RENDERING_CN.md`。

## 变量解释

- `OCT_3-octanol`：3-octanol，经典果蝇嗅觉条件化气味之一。
- `MCH_4-methylcyclohexanol`：4-methylcyclohexanol，经典果蝇嗅觉条件化气味之一。
- `CS+`：conditioned stimulus plus，训练时与奖励或惩罚配对的气味。
- `CS-`：conditioned stimulus minus，未配对的对照气味。
- `US`：unconditioned stimulus，非条件刺激。本项目中包括 `sucrose_reward` 和 `electric_shock`。
- `expected_choice_rate`：按条件预期计算的正确方向比例。奖励条件预期靠近 `CS+`；电击条件预期远离 `CS+`，也就是选择 `CS-`。
- `mean_approach_margin`：`d(CS-) - d(CS+)`。正值表示更靠近 `CS+`，负值表示更靠近 `CS-`。
- `n_nominal_side_trials`：按原始条件表摆放运行的 trial 数。
- `n_mirror_side_trials`：把 `CS+` 左右互换后运行的 trial 数。
- `mean_expected_laterality_index`：按预期行为方向校正后的横向位移除以路径长度。奖励任务朝 `CS+` 为正；电击任务远离 `CS+` 为正。
- `mean_early_expected_lateral_velocity`：前 `25%` 时间窗中，朝预期方向的横向速度。它用于捕捉终点 choice rate 饱和之前的早期转向。
- `mean_expected_curvature_rad_per_mm`：轨迹曲率按预期方向校正后的均值。它比终点更接近“转向策略”读数。
- `mean_physical_laterality_index`：不按 `CS+` 方向校正的真实左/右漂移，用于发现身体或 motor-side bias。
- `welch_fdr_q_*`：Welch t 检验后做 Benjamini-Hochberg FDR 校正的 q 值。一般 `q < 0.05` 才能说该代理仿真指标有显著差异。

## 条件汇总

| condition | n_trials | expected_choice_rate | mean_approach_margin | expected_choice_fdr_q | mean_expected_laterality_index | mean_early_expected_lateral_velocity | mean_physical_laterality_index |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `oct_sucrose_right_mb_silenced` | 100 | 0.89 | 0.303976 | 6.776e-16 | 0.102954 | -0.553725 | -0.003768 |
| `oct_sucrose_left_mb_silenced` | 100 | 0.89 | 0.297667 | 6.776e-16 | 0.099731 | -0.766174 | -0.004334 |
| `oct_sucrose_mb_symmetrized` | 100 | 0.89 | 0.292496 | 6.776e-16 | 0.095934 | -0.484511 | 0.004926 |
| `oct_sucrose_appetitive_wt` | 100 | 0.86 | 0.265371 | 9.468e-14 | 0.089150 | -0.575002 | 0.001040 |
| `weak_oct_strong_mch_conflict` | 100 | 0.88 | 0.264908 | 3.823e-15 | 0.089230 | -0.525155 | -0.011458 |
| `oct_sucrose_mb_swapped` | 100 | 0.87 | 0.263343 | 2.101e-14 | 0.088346 | -0.511283 | -0.008577 |
| `mch_sucrose_appetitive_wt_counterbalanced` | 100 | 0.85 | 0.245904 | 4.825e-13 | 0.084061 | -0.543153 | 0.001594 |
| `oct_shock_aversive_wt` | 100 | 0.86 | -0.244407 | 9.468e-14 | 0.083488 | -0.552929 | 0.007508 |

解释：

- 镜像摆放后，奖励条件仍显著趋近 `CS+`，电击条件仍显著回避 `CS+`。
- `weak_oct_strong_mch_conflict` 在 `CS+` 气味强度较弱、`CS-` 较强时仍达到 `expected_choice_rate = 0.88`，支持“记忆项能在代理系统中部分覆盖即时感觉强度差异”。
- `mean_physical_laterality_index` 接近 0，说明镜像摆放基本抵消了单纯左/右几何漂移。

## MB 扰动与 WT 对照比较

| condition | reference | delta_mean_approach_margin | q_approach | delta_early_velocity | q_early_velocity | delta_expected_laterality | q_expected_laterality | delta_physical_laterality | q_physical_laterality | delta_expected_curvature | q_expected_curvature |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `oct_sucrose_left_mb_silenced` | `oct_sucrose_appetitive_wt` | 0.032297 | 1.0 | -0.191173 | 1.0 | 0.010581 | 1.0 | -0.005374 | 1.0 | -1.561230 | 0.170533 |
| `oct_sucrose_mb_swapped` | `oct_sucrose_appetitive_wt` | -0.002028 | 1.0 | 0.063718 | 1.0 | -0.000804 | 1.0 | -0.009617 | 1.0 | -1.541453 | 0.170533 |
| `oct_sucrose_mb_symmetrized` | `oct_sucrose_appetitive_wt` | 0.027126 | 1.0 | 0.090491 | 1.0 | 0.006784 | 1.0 | 0.003886 | 1.0 | -0.594204 | 0.693157 |
| `oct_sucrose_right_mb_silenced` | `oct_sucrose_appetitive_wt` | 0.038605 | 1.0 | 0.021276 | 1.0 | 0.013804 | 1.0 | -0.004808 | 1.0 | -1.114470 | 0.314646 |
| `weak_oct_strong_mch_conflict` | `oct_sucrose_appetitive_wt` | -0.000463 | 1.0 | 0.049847 | 1.0 | 0.000080 | 1.0 | -0.012498 | 1.0 | -1.087326 | 0.314646 |

结论：

- 当前 calibrated motor bridge 能稳定表达 `CS+`/`CS-` valence memory。
- 在 side-balanced `n=50` early-kinematics 套件中，MB 扰动相对 WT 的 `approach_margin`、早期横向速度、预期方向 laterality、真实左/右漂移均没有通过 FDR。
- 曲率指标出现趋势，最小 `q = 0.170533`，但仍未达到显著性。
- 因此当前不能写成“仿真已经证明 MB 侧化扰动产生显著行为效应”。更严谨的 Nature 风格表述是：公开 calibrated bridge 已验证 valence memory readout 的可执行性，但当前低维接口对 MB 左右侧化不够敏感；侧化结构假说需要更直接的 `MBON/DAN/APL/DPM -> DN/motor` 映射或真实 OCT/MCH 响应矩阵继续检验。

## GPU 与资源解释

本轮命令使用 `--max-workers 4` 并行运行 FlyGym/MuJoCo 试验。无渲染的 MuJoCo 物理 rollout 主要消耗 CPU 和 Python 进程时间，不会像 PyTorch sparse propagation 那样高效占满 H200/H20Z GPU。GPU 在本项目中主要用于：

- `/unify/ydchen/unidit/bio_fly/scripts/run_four_card_experiment_suite.py` 的四卡 sparse connectome propagation。
- `/unify/ydchen/unidit/bio_fly/scripts/build_oct_mch_sensory_encoder.py --device cuda:0` 的连接组传播。
- 带 `--render` 的 FlyGym/MuJoCo EGL 视频渲染，受 `MUJOCO_EGL_DEVICE_ID` 和 `--render-devices` 控制。

如果要生成 paper 级预览视频，可以运行小样本渲染，不建议直接渲染全部 800 条正式 trial：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview \
  --n-trials 1 \
  --run-time 0.8 \
  --max-workers 4 \
  --mirror-sides \
  --render \
  --render-devices 0 1 2 3
```

## 下一步

1. 从 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_kc_readout.csv` 出发，把 OCT/MCH 气味身份特异的 KC readout 直接映射到 MBON/DAN/APL/DPM，而不是只通过低维 `MemoryCondition`。
2. 为 `MBON/DAN/APL/DPM -> DN` 建立直接 readout 表，比较左侧反馈稳定模块和右侧调制输出模块是否招募不同 DN family。
3. 把曲率趋势作为下一轮候选 readout，但不能在当前结果里写成显著发现。
4. 真实湿实验应优先测试 `weak_oct_strong_mch_conflict` 和单侧 MB/APL/DPM 操控，因为代理系统已经稳定表达 valence，但侧化效应需要更高灵敏度读数。
