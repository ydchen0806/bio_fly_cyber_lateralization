# OCT/MCH sensory encoder 与 calibrated motor bridge 总结

保存路径：`/unify/ydchen/unidit/bio_fly/docs/MOTOR_AND_ODOR_BRIDGE_CN.md`

## 本轮目标

本轮把项目从“行为标签和代理视频”推进到两个更清楚的中间层：

1. `OCT/MCH sensory encoder`：把 `OCT_3-octanol` 和 `MCH_4-methylcyclohexanol` 从实验标签推进到 FlyWire ORN/ALPN seed sets。
2. `calibrated motor bridge`：把 motor calibration 表中的 readout-derived motor targets 转成现有 FlyGym 记忆行为仿真的 `MemoryCondition` 参数。

这两个模块形成新的可执行链条：

`OCT/MCH 条件表 -> glomerulus-level ORN/ALPN seeds -> KC readout -> calibrated motor target -> MemoryCondition -> FlyGym behavior screen`

## 新增代码

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/odor_sensory_encoder.py`
- `/unify/ydchen/unidit/bio_fly/scripts/build_oct_mch_sensory_encoder.py`
- `/unify/ydchen/unidit/bio_fly/tests/test_odor_sensory_encoder.py`
- `/unify/ydchen/unidit/bio_fly/src/bio_fly/connectome_motor_bridge.py`
- `/unify/ydchen/unidit/bio_fly/scripts/build_connectome_motor_bridge.py`
- `/unify/ydchen/unidit/bio_fly/tests/test_connectome_motor_bridge.py`

## OCT/MCH sensory encoder

运行命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/build_oct_mch_sensory_encoder.py \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder \
  --device cuda:0 \
  --steps 2 \
  --max-active 5000
```

输出文件：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_glomerulus_map.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_seed_neurons.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_kc_readout.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_encoder_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/OCT_MCH_SENSORY_ENCODER_CN.md`

当前结果：

| odor_identity | n_configured_glomeruli | n_orn_seeds | n_pn_seeds | n_kc_readout | kc_abs_mass | kc_laterality_index |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `MCH_4-methylcyclohexanol` | 3 | 158 | 10 | 2203 | 0.526523 | -0.115850 |
| `OCT_3-octanol` | 9 | 426 | 44 | 2757 | 0.461211 | -0.062238 |

变量解释：

- `n_configured_glomeruli`：该气味配置了多少候选 antennal-lobe glomeruli。
- `n_orn_seeds`：FlyWire 注释中被选中的 olfactory receptor neuron 数量。
- `n_pn_seeds`：FlyWire 注释中被选中的 antennal-lobe projection neuron 数量。
- `n_kc_readout`：连接组传播后被招募的 Kenyon cell 数量。
- `kc_abs_mass`：传播到 KC 的总绝对响应量。
- `kc_laterality_index`：`(right KC mass - left KC mass) / (right KC mass + left KC mass)`，负值表示左侧 KC readout 更强。

严谨边界：该模块是 `literature_constrained_glomerular_encoder`，不是实测 OCT/MCH 受体响应矩阵。默认 glomerulus 列表用于构建可运行假说，后续应以真实 ORN/PN 响应数据替换。

## calibrated motor bridge

运行命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/build_connectome_motor_bridge.py \
  --motor-target-table /unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge \
  --run-screen \
  --n-trials 1 \
  --run-time 0.2 \
  --render-device 0
```

输出文件：

- `/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/CONNECTOME_MOTOR_BRIDGE_CN.md`
- `/unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/screen_trials/oct_mch_calibrated_screen_summary.csv`

当前 screen 结果是轻量无渲染 sanity check，每个条件 1 次、每次 0.2 s，只能证明流程可执行，不能作为统计显著性证据。结果中：

- `oct_sucrose_appetitive_wt` 选择 `CS+`，approach margin 为 `0.539841`。
- `oct_shock_aversive_wt` 选择 `CS-`，approach margin 为 `-0.677602`，符合惩罚记忆方向。
- `weak_oct_strong_mch_conflict` 选择 `CS+`，approach margin 为 `0.607921`，符合“记忆可部分覆盖弱 CS+ 感觉强度”的代理预测。
- `mch_sucrose_appetitive_wt_counterbalanced` 和 `oct_sucrose_right_mb_silenced` 在当前 0.2 s screen 中选择 `CS-`，提示右侧摆放/右侧扰动条件需要更长仿真或更多 seeds 评估，不能直接当作负结论。

## 当前科学结论

可以写：

> We introduced a glomerulus-level OCT/MCH sensory encoder and a calibrated connectome-to-motor bridge, allowing odor-identity-specific FlyWire seeds and readout-derived motor targets to drive embodied memory-choice simulations.

不能写：

> OCT/MCH 的真实 ORN 响应已经被完整测量并复现，或者 Eon 的 sensory encoder / motor controller 已经被恢复。

## 下一步

1. 用真实 odor-response 数据替换默认 glomerulus 权重。
2. 把 `oct_mch_kc_readout.csv` 的左右 KC readout 直接接入 MB 侧化扰动，而不是只经行为参数桥接。
3. 对 `oct_mch_calibrated_screen_summary.csv` 扩展到每条件至少 50 个 seeds，并用四卡并行跑统计。
4. 修复或替换视觉 tracking proxy，使视觉 motor calibration 不再由失败代理决定。

## OCT/MCH 多 seed pilot

新增脚本：

- `/unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py`

运行命令：

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
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

pilot 结果：

| condition | n | expected_choice_rate | mean_approach_margin | interpretation |
| --- | ---: | ---: | ---: | --- |
| `mch_sucrose_appetitive_wt_counterbalanced` | 4 | 1.0 | 1.121587 | MCH 奖励记忆选择 CS+ |
| `oct_sucrose_appetitive_wt` | 4 | 1.0 | 0.962411 | OCT 奖励记忆选择 CS+ |
| `oct_shock_aversive_wt` | 4 | 1.0 | -0.673866 | 电击条件回避 CS+ |
| `weak_oct_strong_mch_conflict` | 4 | 1.0 | 0.672881 | 弱 OCT / 强 MCH 冲突仍偏向 CS+ |

统计边界：`n=4` 时 expected choice 的二项检验 FDR 为 `0.125`，因此只能作为 pilot 方向验证。正式结果需要每条件至少 `50` 个 seeds：

```bash
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite_n50 \
  --n-trials 50 \
  --run-time 0.8 \
  --max-workers 4
```

## n=50 正式代理仿真

已经完成两套 `n=50` 代理仿真：

- late/terminal assay：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite_n50`
- early-decision assay：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_early_suite_n50`

late assay 的关键结果：

| condition | expected_choice_rate | mean_approach_margin | expected_choice_fdr_q |
| --- | ---: | ---: | ---: |
| `oct_sucrose_appetitive_wt` | 1.0 | 5.747301 | 1.776e-15 |
| `mch_sucrose_appetitive_wt_counterbalanced` | 1.0 | 5.732041 | 1.776e-15 |
| `oct_shock_aversive_wt` | 1.0 | -5.351253 | 1.776e-15 |
| `weak_oct_strong_mch_conflict` | 1.0 | 5.770910 | 1.776e-15 |

early-decision assay 的关键结果：

| condition | expected_choice_rate | mean_approach_margin | expected_choice_fdr_q |
| --- | ---: | ---: | ---: |
| `oct_sucrose_appetitive_wt` | 0.80 | 0.252239 | 2.386e-05 |
| `mch_sucrose_appetitive_wt_counterbalanced` | 0.86 | 0.265210 | 2.798e-07 |
| `oct_shock_aversive_wt` | 0.92 | -0.226482 | 1.785e-09 |
| `weak_oct_strong_mch_conflict` | 0.86 | 0.244648 | 2.798e-07 |

关键负结果：

- late assay 中 MB perturbation 相对 WT 的 `welch_fdr_q >= 0.984`。
- early-decision assay 中 MB perturbation 相对 WT 的 `welch_fdr_q = 1.0`。
- 因此当前 motor bridge 能稳定表达 valence 和 CS+/CS- 方向，但还不能支持“MB 侧化扰动产生显著行为差异”的强声明。

这不是失败，而是一个明确的下一步工程目标：需要引入更灵敏的 early-turning metric、真实 OCT/MCH response weights，或把 MBON/DAN/APL/DPM readout 更直接地接到 DN/motor 层。

## n=50 mirror-side 早期动力学正式结果

为避免 `CS+` 左右摆放混杂，本轮新增 mirror-side 选项并实际运行正式套件：

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

新增输出：

- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_trials.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_condition_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/oct_mch_formal_wt_comparisons.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/figures/Fig_oct_mch_formal_suite.png`
- `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50/OCT_MCH_FORMAL_SUITE_CN.md`
- `/unify/ydchen/unidit/bio_fly/docs/OCT_MCH_MIRROR_KINEMATICS_CN.md`

本轮每条件 `n=100`，其中 `50` 条为 nominal side，`50` 条为 mirror side。关键结果如下：

| condition | expected_choice_rate | mean_approach_margin | expected_choice_fdr_q | mean_expected_laterality_index |
| --- | ---: | ---: | ---: | ---: |
| `oct_sucrose_appetitive_wt` | 0.86 | 0.265371 | 9.468e-14 | 0.089150 |
| `mch_sucrose_appetitive_wt_counterbalanced` | 0.85 | 0.245904 | 4.825e-13 | 0.084061 |
| `oct_shock_aversive_wt` | 0.86 | -0.244407 | 9.468e-14 | 0.083488 |
| `weak_oct_strong_mch_conflict` | 0.88 | 0.264908 | 3.823e-15 | 0.089230 |

MB 扰动相对 `oct_sucrose_appetitive_wt` 的比较仍未通过 FDR：approach margin、early expected lateral velocity、expected laterality index 和 physical laterality index 的 `welch_fdr_q` 均为 `1.0`；曲率趋势最强的 `left_MB_gain_0.25` 与 `left_right_MB_weights_swapped` 的 `welch_fdr_q_expected_curvature_rad_per_mm` 均为 `0.170533`，不能写成显著。

结论更新：calibrated motor bridge 可以稳定表达 OCT/MCH valence memory，但当前 `MemoryCondition` 低维接口对 MB 侧化扰动不够敏感。下一步应把 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_kc_readout.csv` 直接接入 `MBON/DAN/APL/DPM -> DN/motor` readout，而不是继续只调 `lateral_memory_bias`。
