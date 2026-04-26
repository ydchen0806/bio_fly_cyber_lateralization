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

