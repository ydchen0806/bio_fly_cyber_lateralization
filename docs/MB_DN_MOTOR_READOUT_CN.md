# MBON/DAN/APL/DPM 到 DN 再到 motor primitive 的直接读出

保存路径：`/unify/ydchen/unidit/bio_fly/docs/MB_DN_MOTOR_READOUT_CN.md`

## 这次实现的目的

用户关心的是：Eon/CyberFly 原文强调连接组能驱动或约束果蝇行为，我们能不能更接近这个逻辑，而不是只用一个手工 `lateral_memory_bias` 控制果蝇转向。

本轮实现了一个公开可审计的替代接口：

`FlyWire MBON/DAN/APL/DPM seeds -> FlyWire v783 signed propagation -> descending neurons -> DN family -> motor primitive`

这个接口比之前 `/unify/ydchen/unidit/bio_fly/src/bio_fly/inverse_motor_fit.py` 更直接。旧接口是从多模态 readout 特征逆向拟合低维 motor motif；新接口直接问：蘑菇体输出、强化学习和反馈调控神经元能否通过公开连接组传播到下降神经元，并形成与转向、回避、梳理、取食或记忆表达相关的可检验 motor primitive 偏置。

## 公开依据

- Eon embodied brain emulation 公开说明：`https://eon.systems/updates/embodied-brain-emulation`
- FlyWire whole-brain connectome：`https://www.nature.com/articles/s41586-024-07558-y`
- FlyWire annotation/cell typing：`https://www.nature.com/articles/s41586-024-07686-5`
- Shiu 等连接组约束 brain model：`https://www.nature.com/articles/s41586-024-07763-9`
- MBON/DAN 蘑菇体学习回路：`https://elifesciences.org/articles/04580`
- 蘑菇体 compartment architecture：`https://elifesciences.org/articles/04577`
- NeuroMechFly/FlyGym 身体仿真：`https://www.nature.com/articles/s41592-024-02497-y`

这些资料支持“分层 embodied brain emulation”和“连接组约束的 sensorimotor readout”，但不支持我们声称已经恢复 Eon 内部 DN-to-body 私有权重。

## 新增代码

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/mb_dn_motor_readout.py`：核心模块。
- `/unify/ydchen/unidit/bio_fly/scripts/run_mb_dn_motor_readout.py`：一键运行脚本。
- `/unify/ydchen/unidit/bio_fly/tests/test_mb_dn_motor_readout.py`：回归测试。

## 一键复现命令

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_mb_dn_motor_readout.py \
  --devices cuda:0 cuda:1 cuda:2 cuda:3 \
  --steps 3 \
  --max-active 5000 \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout
```

本轮实际运行：

- 本地 GPU：4 张 `NVIDIA H20Z`，每张约 `139.7 GiB` 显存。
- 连接表：`/unify/ydchen/unidit/bio_fly/external/Drosophila_brain_model/Connectivity_783.parquet`，`15,091,983` 条 signed connectivity 边。
- 注释表：`/unify/ydchen/unidit/bio_fly/data/processed/flywire_neuron_annotations.parquet`，`139,244` 个注释神经元。
- 蘑菇体注释表：`/unify/ydchen/unidit/bio_fly/data/processed/flywire_mushroom_body_annotations.parquet`，`5,608` 个 MB 相关神经元。
- seed 条件数：`18`。
- 传播步数：`3` hop。
- 每步最大 active 节点：`5000`。
- 四卡耗时：`31.81` 秒。

## 变量解释

- `MBON`：mushroom body output neuron，蘑菇体输出神经元，把学习后的气味价值和记忆状态传给下游网络。
- `DAN`：dopaminergic neuron，多巴胺神经元，参与奖励、惩罚和记忆更新。
- `APL`：anterior paired lateral neuron，蘑菇体内广泛抑制细胞，调节 KC 稀疏编码和反馈。
- `DPM`：dorsal paired medial neuron，与记忆维持和蘑菇体反馈调控有关。
- `DN`：descending neuron，下降神经元，从脑下行到腹神经索和身体运动系统，是脑内计算进入身体动作的关键出口。
- `seed_side`：seed 来自 `left`、`right` 或 `bilateral`。
- `odor_KC_context`：OCT/MCH sensory encoder 先传播到 KC，再选取 top KC 作为气味上下文 seed。
- `dn_abs_mass`：传播到 DN 层的绝对响应总量。越大表示该 seed 条件越强地影响下行出口。
- `dn_signed_mass`：带符号响应总量。符号来自 signed connectivity，不应直接等同于行为好坏。
- `laterality_index_right_minus_left`：`(right_dn_abs_mass - left_dn_abs_mass)/(right_dn_abs_mass + left_dn_abs_mass)`。正值表示右侧 DN 响应偏强，负值表示左侧偏强。
- `dn_family`：用 DN cell type 前缀粗分的下行神经元家族，例如 `DNa`、`DNg`、`DNge`、`DNp`、`DNpe`、`MDN_backward_walk`。
- `motor primitive`：低维动作原语，不是肌肉级命令。当前包括 `forward_drive`、`turning_drive`、`avoidance_drive`、`grooming_drive`、`feeding_drive`、`memory_expression_drive`、`state_modulation_drive`。

## 输出文件

- seed 表：`/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/mb_seed_table.csv`
- 条件 manifest：`/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/mb_dn_condition_manifest.csv`
- DN 单神经元响应：`/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/mb_dn_response_by_neuron.csv`
- DN family 汇总：`/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/mb_dn_family_summary.csv`
- 条件汇总：`/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/mb_dn_condition_summary.csv`
- motor primitive 汇总：`/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/mb_dn_motor_primitives.csv`
- top DN targets：`/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/mb_dn_top_targets.csv`
- 运行 metadata：`/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/suite_metadata.json`
- 输出报告：`/unify/ydchen/unidit/bio_fly/outputs/mb_dn_motor_readout/MB_DN_MOTOR_READOUT_CN.md`

论文图表副本：

- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_family_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_motor_primitive_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_laterality_index.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_mb_dn_motor_mechanism.png`

论文视频副本：

- `/unify/ydchen/unidit/bio_fly/paper/video/mb_dn_motor_readout_summary.mp4`

## 主要发现

按 DN 绝对响应量排序，最强条件是 `left_MBON_to_DN`：

| condition | seed 数 | recruited DN | dn_abs_mass | laterality index | top DN family | top DN |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `left_MBON_to_DN` | 48 | 202 | 0.064815 | +0.082 | `DNa` | `DNa02` |
| `bilateral_MBON_to_DN` | 96 | 177 | 0.046990 | +0.222 | `DNa` | `DNa03` |
| `right_MBON_to_DN` | 48 | 149 | 0.034105 | +0.307 | `DNa` | `DNp42` |
| `bilateral_memory_axis_to_DN` | 431 | 108 | 0.024549 | +0.230 | `DNa` | `DNa03` |
| `right_memory_axis_to_DN` | 215 | 110 | 0.021524 | +0.420 | `DNa` | `DNp42` |
| `left_memory_axis_to_DN` | 216 | 111 | 0.021501 | -0.016 | `DNa` | `DNa02` |

解释：

- `MBON` 比 `DAN`、`APL/DPM` 更强地连到 DN 层，符合 MBON 作为蘑菇体输出读出的生物学直觉。
- `right_MBON_to_DN` 和 `right_memory_axis_to_DN` 的 DN laterality index 明显右偏，提示右侧输出轴可能更容易把记忆状态传到下行运动出口。
- `left_MBON_to_DN` 的总 DN 响应更强，但侧化指数较小，说明“强度”和“右偏/左偏”不是同一个概念。
- OCT/MCH KC odor-context 到 DN 的响应很弱，说明早期气味身份读出主要仍在 KC/MB 内部，直接 DN 输出需要 MBON/DAN 层进一步整合。

## motor primitive 读出

DN family 映射到 motor primitive 的规则是透明手工先验，不是 Eon 私有权重。当前最常见的 dominant primitive 是 `turning_drive`，因为 `DNa`、`DNg`、`DNp`、`DNpe` 在 family summary 中占比高。`DNge` 提高 `grooming_drive`，`MDN_backward_walk` 提高 `avoidance_drive`，`DAN` 和 `APL/DPM` 条件额外提高 `state_modulation_drive`。

这可以用于论文中的方法学叙事：

> 我们没有把 DN 输出直接解释成完整行为，而是先把它压缩成低维 motor primitive。这一步把缺失的 DN-to-body 接口显式暴露出来，使它可以被后续真实行为轨迹、钙成像或 Eon/FlyGym 控制器替换。

## 不能过度声称

不能写：

- “我们已经复现 Eon 私有闭环系统。”
- “我们恢复了 Eon DN-to-body 权重。”
- “连接组单独自动涌现完整果蝇行为。”
- “MB-DN 读出已经证明真实果蝇会产生相同行为。”

可以写：

- “我们实现了一个公开可审计的 MB-to-DN-to-motor primitive 替代接口。”
- “FlyWire 公开连接组支持 MBON/memory-axis 到 DN 层的侧化读出。”
- “该读出为左右蘑菇体侧化如何影响行为提供了新的可实验验证假说。”
- “最终因果结论仍需单侧 MBON/DAN/APL/DPM 或 DN 操控、钙成像和真实 OCT/MCH 行为学验证。”
