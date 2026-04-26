# bio_fly 项目整理与逐项实现状态

保存路径：`/unify/ydchen/unidit/bio_fly/docs/PROJECT_IMPLEMENTATION_STATUS_CN.md`

## 总体目标

项目根目录是 `/unify/ydchen/unidit/bio_fly`。当前目标不是夸大为“完全复刻 Eon 私有闭环系统”，而是建立一个可复现、可审计、可统计的公开替代体系：

`FlyWire 结构发现 -> 连接组传播 -> DN/行为接口读出 -> FlyGym/NeuroMechFly 行为代理 -> 图表/视频/论文`

这个体系用于验证用户论文 zip 中关于左右脑蘑菇体、KC 神经递质输入、记忆轴和行为侧化的结构发现。

## 九项任务状态

1. 审计 `/unify/ydchen/unidit/bio_fly` 当前实现：已完成。项目已有 `src/bio_fly` 核心包、`scripts` 命令入口、`tests` 回归测试、`outputs` 结果目录、`docs` 中文报告、`paper` 论文和视频目录。
2. 解压并解析 `Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip`：已完成。zip 主要包含论文 tex、bib、markdown 和 figure 文件，不是 root-id 级原始连接组仿真数据。解析与论文发现提取结果保存在 `/unify/ydchen/unidit/bio_fly/outputs/paper_findings`。
3. 下载或接入 FlyWire / Codex / neuPrint / NeuroMechFly 公开数据：部分完成。当前已接入 `/unify/ydchen/unidit/bio_fly/external/Drosophila_brain_model`、FlyWire v783/v630 连接表、注释表和 FlyGym/NeuroMechFly 环境。neuPrint/Codex 更深层数据仍需要按 API 权限继续扩展。
4. 实现 GPU 稀疏传播和四卡 trial sweep：已完成。四卡结果在 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite`，设备检测为 4 张 NVIDIA H20Z/H200 级 GPU，每卡约 139 GiB 显存。
5. 实现 OCT/MCH 或食物气味 CS+/CS- 嗅觉记忆实验：已完成原型。当前主要实现为糖奖励食物气味 `CS+` 与诱饵/竞争气味 `CS-`，输出在 `/unify/ydchen/unidit/bio_fly/outputs/food_memory_suite` 和 `/unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite`。
6. 实现 MB 侧化消融：已完成原型。包括右侧 serotonin KC、左侧 glutamate KC、双侧 blunting、对称/镜像/剂量相关行为代理；核心输出在 `/unify/ydchen/unidit/bio_fly/outputs/model_linkage_gpu`、`/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite`、`/unify/ydchen/unidit/bio_fly/outputs/structure_behavior_linkage`。
7. 生成统计表、主图、补充图、高清视频：已完成多批。论文视频集中在 `/unify/ydchen/unidit/bio_fly/paper/video`，图集中在 `/unify/ydchen/unidit/bio_fly/paper/figures` 和各输出目录下的 `figures`。
8. 更新 README、中文教学文档、实验报告和 LaTeX paper：持续完成。本轮新增逆向拟合接口层说明，并更新 `/unify/ydchen/unidit/bio_fly/README.md`。
9. 在论文中区分“公开复现”“替代接口”“原创侧化发现”“待湿实验验证”：已写入 README、Eon 多模态报告和本轮逆向拟合报告。后续投稿版 `main_merged.tex` 还应继续压缩措辞，避免过度声称。

## 本轮新增：逆向拟合接口层

新增模块：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/inverse_motor_fit.py`
- `/unify/ydchen/unidit/bio_fly/scripts/run_inverse_motor_fit.py`
- `/unify/ydchen/unidit/bio_fly/tests/test_inverse_motor_fit.py`

运行命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_inverse_motor_fit.py \
  --connectome-summary /unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark/connectome_readout/connectome_multimodal_readout_summary.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit
```

输出文件：

- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_training_table.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_interface_coefficients.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_interface_predictions.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/inverse_motor_interface_leave_one_out_cv.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/figures/Fig_inverse_motor_interface.png`
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/INVERSE_MOTOR_INTERFACE_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/inverse_motor_fit/suite_metadata.json`

## 逆向拟合接口层的含义

Eon 没有公开完整 DN-to-motor 权重，所以本项目不能恢复其真实内部参数。本轮实现的是一个公开替代层：

`connectome readout features -> low-dimensional motor motif scores`

输入是连接组传播得到的 readout 特征：

- `descending_abs_mass`：下行神经元总响应强度。
- `memory_axis_abs_mass`：KC、MBON、DAN、APL、DPM 等记忆轴响应强度。
- `visual_projection_abs_mass`：视觉投射通路响应强度。
- `gustatory_abs_mass`：味觉/糖接触通路响应强度。
- `mechanosensory_abs_mass`：机械感觉/接触通路响应强度。
- 对应的 `signed_mass`：带符号净响应，用于区分兴奋/抑制方向。

输出是低维行为控制目标：

- `forward_drive`：前进或接近驱动。
- `turning_drive`：转向驱动。
- `feeding_drive`：进食或口器伸展代理驱动。
- `grooming_drive`：梳理驱动。
- `visual_steering_drive`：视觉目标跟踪/视觉诱导转向驱动。

当前训练集只有四个条件：气味食物记忆、视觉目标跟踪、味觉进食和机械感觉梳理。因此训练集误差很小，但留一法误差偏大。这说明技术上可以实现接口层，但目前只适合做假说生成和工程闭环，不能单独作为 Nature 级定量证据。

## 当前项目目录整理建议

为了避免“东西太杂”，建议以后所有新增结果按下面方式放置：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly`：只放可复用 Python 模块。
- `/unify/ydchen/unidit/bio_fly/scripts`：只放命令行入口。
- `/unify/ydchen/unidit/bio_fly/tests`：只放回归测试。
- `/unify/ydchen/unidit/bio_fly/outputs/<suite_name>`：每个实验套件单独一个目录，目录内包含 `suite_metadata.json`、表格、图、视频和中文报告。
- `/unify/ydchen/unidit/bio_fly/docs`：放面向老师/合作者阅读的中文解释性文档。
- `/unify/ydchen/unidit/bio_fly/paper`：放投稿草稿、主图、补充视频索引，不放大型原始数据。
- `/unify/ydchen/unidit/bio_fly/data`：放本地数据，不建议提交 git。
- `/unify/ydchen/unidit/bio_fly/external`：放外部仓库和第三方公开模型，不建议直接改动。

## 下一步优先级

1. 把真实行为轨迹或更大规模 FlyGym rollout 加入逆向拟合目标表，替换当前 motif 默认标签。已新增第一版：`/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv`。
2. 为 OCT/MCH 经典嗅觉条件化单独建立 `odor_identity`、`CS+`、`CS-`、`US=sucrose/shock` 的条件表。已新增第一版：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/oct_mch_condition_table.csv`。
3. 扩展 MB 侧化消融到 `symmetrized`、`left-right swapped` 和 `degree-preserving random` 三类强对照。OCT/MCH 条件表已包含 `left_right_MB_weights_averaged` 与 `left_right_MB_weights_swapped`，但底层连接矩阵级扰动仍需继续实现。
4. 把逆向拟合接口层接入行为仿真，使 readout 预测值直接控制 `MemoryCondition` 或 NeuroMechFly motor drive。当前已生成校准接口，尚未直接接入控制器。
5. 对每个论文主结论保留三列证据等级：结构统计、仿真预测、待湿实验验证。当前 motor calibration 表已新增 `evidence_level` 字段，后续要扩展到全部主结果。

## 2026-04-26 后续推进：仿真校准和 OCT/MCH 实验计划

本轮继续新增两个模块：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/motor_calibration.py`
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/oct_mch_conditioning.py`

新增命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate

/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/build_motor_calibration.py \
  --eon-output-dir /unify/ydchen/unidit/bio_fly/outputs/eon_multimodal_benchmark \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/motor_calibration

/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/write_oct_mch_conditioning_plan.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning
```

新增输出：

- `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/MOTOR_CALIBRATION_FROM_SIMULATION_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/inverse_motor_interface_coefficients.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/inverse_motor_fit_calibrated/figures/Fig_inverse_motor_interface.png`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/oct_mch_condition_table.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/oct_mch_condition_table.yaml`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_conditioning/OCT_MCH_CONDITIONING_PLAN_CN.md`

motor calibration 表把四类行为接口拆成证据等级：

- `olfactory_food_memory`：来自食物气味 FlyGym 轨迹，证据等级为 `embodied_trajectory_proxy`。
- `visual_object_tracking`：来自视觉目标跟踪代理轨迹，证据等级为 `visual_proxy_trajectory`。当前这个条件的目标距离变大，因此 `visual_steering_drive` 被量化为 `0.0`，这是一个重要失败模式，不应删除。
- `gustatory_feeding`：来自 gustatory connectome readout，证据等级为 `connectome_proxy_only`，因为尚无完整口器力学。
- `mechanosensory_grooming`：来自梳理代理时间序列，证据等级为 `embodied_motor_proxy`。

校准后的留一法误差显示：`visual_steering_drive` 误差较低，但 `feeding_drive` 仍高，说明 feeding 缺少真实 proboscis mechanics 是当前最明显短板。

## 2026-04-26 继续推进：OCT/MCH sensory encoder 与行为桥接

本轮新增两个闭环模块：

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/odor_sensory_encoder.py`
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/connectome_motor_bridge.py`

对应命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate

/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/build_oct_mch_sensory_encoder.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder \
  --device cuda:0 \
  --steps 2 \
  --max-active 5000

/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/build_connectome_motor_bridge.py \
  --motor-target-table /unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge \
  --run-screen \
  --n-trials 1 \
  --run-time 0.2 \
  --render-device 0
```

新增输出：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_glomerulus_map.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_seed_neurons.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_kc_readout.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_encoder_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/screen_trials/oct_mch_calibrated_screen_summary.csv`
- `/unify/ydchen/unidit/bio_fly/docs/MOTOR_AND_ODOR_BRIDGE_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/INDEX_CN.md`

当前 encoder 结果：

| odor_identity | n_configured_glomeruli | n_orn_seeds | n_pn_seeds | n_kc_readout | kc_abs_mass | kc_laterality_index |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `MCH_4-methylcyclohexanol` | 3 | 158 | 10 | 2203 | 0.526523 | -0.115850 |
| `OCT_3-octanol` | 9 | 426 | 44 | 2757 | 0.461211 | -0.062238 |

当前行为桥接 screen 结果：

- `oct_sucrose_appetitive_wt`：选择 `CS+`，approach margin `0.539841`。
- `oct_shock_aversive_wt`：选择 `CS-`，approach margin `-0.677602`。
- `weak_oct_strong_mch_conflict`：选择 `CS+`，approach margin `0.607921`。
- `mch_sucrose_appetitive_wt_counterbalanced` 和 `oct_sucrose_right_mb_silenced` 在 0.2 秒 sanity check 中选择 `CS-`，需要长时程和多 seed 验证。

当前结论：项目已经具备 `OCT/MCH 条件表 -> ORN/ALPN seed -> KC readout -> calibrated motor target -> MemoryCondition -> FlyGym screen` 的可执行闭环。它仍然是公开替代系统，不是 Eon 私有闭环。

## 2026-04-26 多 seed OCT/MCH pilot

本轮新增 `/unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py`，用于把 OCT/MCH 行为 screen 扩展到多 seed pilot 和正式统计。

本轮实际运行：

```bash
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite \
  --n-trials 4 \
  --run-time 0.35 \
  --max-workers 4
```

输出：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/oct_mch_formal_trials.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/oct_mch_formal_condition_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/oct_mch_formal_wt_comparisons.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/figures/Fig_oct_mch_formal_suite.png`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite/OCT_MCH_FORMAL_SUITE_CN.md`

pilot 结论：

- 奖励条件 `oct_sucrose_appetitive_wt` 和 `mch_sucrose_appetitive_wt_counterbalanced` 都选择 CS+。
- 惩罚条件 `oct_shock_aversive_wt` 选择 CS-，说明行为参数方向可以表达奖励/惩罚反转。
- `weak_oct_strong_mch_conflict` 在弱 OCT / 强 MCH 冲突下仍选择 CS+，支持“记忆项能覆盖部分即时感觉强度差”的代理预测。
- `n=4` 的二项检验 FDR 为 `0.125`，不能写成显著性证据，只能写成 pilot 方向验证。

正式 Nature 级仿真建议：

```bash
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite_n50 \
  --n-trials 50 \
  --run-time 0.8 \
  --max-workers 4
```

实际已完成两套 `n=50`：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite_n50`：late/terminal assay，`run_time = 0.8 s`。
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_early_suite_n50`：early-decision assay，`run_time = 0.2 s`。

正式代理仿真结论：

- late assay：奖励条件和弱冲突条件 `expected_choice_rate = 1.0`，电击条件按预期回避 CS+，所有 expected choice 的 FDR 为 `1.776e-15`。
- early-decision assay：奖励条件 expected choice rate 为 `0.80-0.86`，电击条件为 `0.92`，FDR 范围 `1.785e-09` 到 `2.386e-05`。
- MB perturbation 相对 WT 的 approach margin 差异没有 FDR 显著：late assay `welch_fdr_q >= 0.984`，early assay `welch_fdr_q = 1.0`。

当前应写成：calibrated bridge 已经稳定表达 OCT/MCH valence memory 和 CS+/CS- 行为方向，但还没有证明蘑菇体侧化扰动会导致显著行为差异。下一步需要更灵敏的侧化 readout。

## docs 整理

当前主线文档入口是 `/unify/ydchen/unidit/bio_fly/docs/INDEX_CN.md`。早期计划、旧运行报告和临时说明已归档到 `/unify/ydchen/unidit/bio_fly/docs/archive`，没有直接删除，便于追溯。
