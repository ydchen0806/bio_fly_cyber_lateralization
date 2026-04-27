# OCT/MCH mirror-side 论文视频渲染说明

保存路径：`/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_ASSAY_VIDEO_RENDERING_CN.md`

## 本轮目的

本轮把 OCT/MCH mirror-side 正式实验渲染成与食物气味记忆视频一致的 paper 风格视频。视频用于补充 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50` 中最重要的 OCT/MCH 结果：奖励条件接近 `CS+`，电击条件回避 `CS+`，并且每个条件都有 `CS+` 左侧和右侧两种摆放。

2026-04-27 又新增 `assay_video_v2`，目标是解决旧版视频仍像 FlyGym 原始画面加蓝黄 CS+/CS- 标签的问题。v2 不再把 raw FlyGym video 作为背景，而是从 trajectory CSV 直接重画实验场景：培养皿、滤纸、OCT/MCH 气味杯、气味羽流、蔗糖滴、电击栅格、果蝇身体朝向、轨迹尾迹和正式统计 inset。

需要特别区分两类证据：

- 视频中的轨迹来自 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview`，每个条件每个 side 各 1 条渲染 trial，主要用于论文补充视频和汇报展示。
- 视频右下角统计 inset 来自 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50`，即每个条件 `nominal 50 + mirror 50 = 100` 条正式统计 trial。

因此可以说“视频展示了正式统计结果对应条件下的代表性轨迹”，但不能把单条视频 trial 当成显著性证据。

## 运行命令

渲染预览 trial：

```bash
cd /unify/ydchen/unidit/bio_fly
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview \
  --n-trials 1 \
  --run-time 0.8 \
  --decision-interval 0.05 \
  --max-workers 4 \
  --mirror-sides \
  --render \
  --keep-trajectories \
  --render-devices 0 1 2 3 \
  --camera-fps 30 \
  --camera-play-speed 0.16 \
  --camera-width 720 \
  --camera-height 540
```

合成 paper 视频：

```bash
cd /unify/ydchen/unidit/bio_fly
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/make_oct_mch_assay_scene_videos.py \
  --summary /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/oct_mch_formal_trials.csv \
  --aggregate /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_condition_summary.csv \
  --comparisons /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_wt_comparisons.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos \
  --paper-video-dir /unify/ydchen/unidit/bio_fly/paper/video \
  --panel-width 480 \
  --panel-height 360 \
  --fps 30
```

生成 v2 视频：

```bash
cd /unify/ydchen/unidit/bio_fly
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/make_oct_mch_assay_v2_videos.py \
  --summary-path /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/oct_mch_formal_trials.csv \
  --aggregate-path /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_condition_summary.csv \
  --comparisons-path /unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_wt_comparisons.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2 \
  --paper-video-dir /unify/ydchen/unidit/bio_fly/paper/video \
  --fps 30 \
  --seconds-per-condition 5
```

## 输出文件

渲染预览目录：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/oct_mch_formal_trials.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/oct_mch_formal_condition_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/oct_mch_formal_wt_comparisons.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/figures/Fig_oct_mch_formal_suite.png`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/trial_artifacts`：16 条 raw mp4、16 条 trajectory CSV 和轨迹图。

视频合成目录：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_cs_plus_right.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_key_conditions.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_mb_perturbations.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_full_both_sides.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_assay_scene_video_manifest.json`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_video_qc.json`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/thumbnails`
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_video_qc.json`：QC 的论文目录副本。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_oct_mch_mirror_assay_video_frame.png`：代表性中帧缩略图，已复制到论文图目录，便于随 git 推送。

论文视频副本：

- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_cs_plus_right.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_key_conditions.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_mb_perturbations.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_mirror_assay_scene_full_both_sides.mp4`

v2 输出：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/oct_mch_assay_v2_key_conditions.mp4`：4 个核心条件，左右 mirror-side 成对展示，20 秒、600 帧、1920x1080。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/oct_mch_assay_v2_mb_perturbations.mp4`：WT 与 4 个 MB perturbation 条件，25 秒、750 帧、1920x1080。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/oct_mch_assay_v2_qc.json`：v2 视频 QC。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/OCT_MCH_ASSAY_VIDEO_V2_CN.md`：v2 变量解释和边界报告。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_key_conditions.mp4`：v2 核心条件 paper 副本。
- `/unify/ydchen/unidit/bio_fly/paper/video/oct_mch_assay_v2_mb_perturbations.mp4`：v2 MB perturbation paper 副本。
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_oct_mch_assay_v2_key_conditions_frame.png`：v2 代表性中帧缩略图。

## 视频画面变量解释

- `OCT`：3-octanol，是经典果蝇嗅觉条件化气味之一。
- `MCH`：4-methylcyclohexanol，也是经典果蝇嗅觉条件化气味之一。
- `CS+`：训练时与非条件刺激配对的气味。奖励任务中预期接近 `CS+`；电击任务中预期回避 `CS+`。
- `CS-`：未配对对照气味。
- `US`：unconditioned stimulus，非条件刺激。本项目中 `US=sucrose` 表示糖奖励，`US=shock` 表示电击惩罚。
- `CS+L` / `CS+R`：`CS+` 分别放在左侧或右侧。
- `nom`：nominal side，原始条件表中的摆放。
- `mir`：mirror side，把 `CS+` 摆放左右互换后的镜像条件。
- 绿色圆点：该 trial 起点。
- 粉色尾迹：从起点到当前时刻的近期轨迹尾迹，来自 trajectory CSV，不是手动画的任意箭头。
- 黑白圆点：当前视频帧对应的轨迹位置。
- 黄色/橙色杯和羽流：`OCT` 或 `MCH` 气味源，颜色根据气味身份区分。
- 糖滴：`US=sucrose` 条件下的奖励标注。
- 电极/闪电：`US=shock` 条件下的惩罚标注。
- 右下角 inset：正式 mirror-side `n=100` 统计，不是当前单条视频 trial 的统计。

## 视频 QC

本轮 QC 文件是 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_video_qc.json`。所有合成视频均为非空帧，首帧像素方差大于 `3300`，说明不是黑屏或空白写入。

| video | frames | fps | width | height |
| --- | ---: | ---: | ---: | ---: |
| `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_cs_plus_left.mp4` | 146 | 30 | 1920 | 720 |
| `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_cs_plus_right.mp4` | 146 | 30 | 1920 | 720 |
| `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_key_conditions.mp4` | 146 | 30 | 1920 | 720 |
| `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_mb_perturbations.mp4` | 146 | 30 | 2400 | 720 |
| `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_render_preview/videos/oct_mch_mirror_assay_scene_full_both_sides.mp4` | 146 | 30 | 1920 | 1440 |

v2 QC：

| video | frames | fps | width | height | duration | nonblank |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/oct_mch_assay_v2_key_conditions.mp4` | 600 | 30 | 1920 | 1080 | 20.0 s | true |
| `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_assay_video_v2/oct_mch_assay_v2_mb_perturbations.mp4` | 750 | 30 | 1920 | 1080 | 25.0 s | true |

## 预览 trial 结果

本轮 16 条渲染 trial 与条件预期一致：

- `oct_sucrose_appetitive_wt`：左右 mirror 均选择 `CS+`。
- `mch_sucrose_appetitive_wt_counterbalanced`：左右 mirror 均选择 `CS+`。
- `oct_shock_aversive_wt`：左右 mirror 均选择 `CS-`。
- `weak_oct_strong_mch_conflict`：左右 mirror 均选择 `CS+`。
- 四个 MB 扰动相关视频 trial 均选择 `CS+`。

正式统计仍以 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50` 为准：奖励和惩罚 valence memory 均显著，但 MB 扰动相对 WT 的行为差异未通过 FDR。

## 严谨边界

- 培养皿、糖滴、电极、气味杯、滤纸和羽流是 post-render scene overlay，用于让论文读者看懂实验结构。
- FlyGym 原始输入仍是 `OdorArena` 中的两个气味源；糖滴不是可摄取的力学对象，电极不是真实电生理刺激。
- 当前视频不能支持“连接组单独自动涌现完整果蝇行为”的强声称。
- 当前视频可以支持“公开替代闭环能够把 OCT/MCH 条件表、mirror-side 控制、代表性轨迹和正式统计组织成可审计的补充材料”。
