# 行为学实验实现状态

## 已跑通

当前已完成 FlyGym/MuJoCo 行为仿真和离屏视频渲染：

```bash
source env/bin/activate
python scripts/run_behavior_memory_experiment.py \
  --conditions control right_mb_serotonin_enriched left_mb_glutamate_enriched bilateral_memory_blunted \
  --n-trials 1 \
  --run-time 0.25 \
  --cs-plus-sides left right \
  --mujoco-gl egl \
  --output-dir outputs/behavior_oriented
```

输出：

- `outputs/behavior_oriented/memory_choice_summary.csv`
- `outputs/behavior_oriented/*trial0*.mp4`
- `outputs/behavior_oriented/*trajectory.csv`
- `outputs/behavior_oriented/*trajectory.png`

修正初始朝向并覆盖默认输出后，8 个左右镜像短实验中 `8/8` 选择了 CS+，说明 odor-memory choice 行为任务和渲染链路可用。

## 条件定义

当前实现位于 `src/bio_fly/behavior.py`：

- `control`：无左右记忆偏置。
- `right_mb_serotonin_enriched`：模拟右侧 MB neuromodulatory enrichment 导致的 lateral memory bias。
- `left_mb_glutamate_enriched`：模拟左侧 glutamatergic bias。
- `bilateral_memory_blunted`：模拟双侧记忆回路削弱/沉默。

这些条件目前是 mechanistic proxy：把连接组层发现映射到下降控制信号和 odor choice bias。下一步要把 `outputs/functional_validation/signed_propagation_summary.csv` 或真实 Brian2/LIF spike readouts 作为参数来源，自动设定 `lateral_memory_bias`、`attractive_gain` 和 `aversive_gain`。

## 如何扩展为论文级实验

1. 使用真实 FlyWire/Codex synapse-level NT input 表，重建 KC subtype × hemisphere × NT 输入差异。
2. 将 strongest KC/DAN/MBON 候选送入 `scripts/run_functional_validation.py --execute-lif` 得到 spike/readout laterality。
3. 将 LIF readout 映射到行为控制参数，而不是手工指定 proxy bias。
4. 每个条件运行 `n_trials >= 20`，左右 CS+ 位置平衡，随机初始扰动。
5. 统计：
   - CS+ choice fraction；
   - distance-to-CS+；
   - signed final lateral displacement；
   - path length；
   - turn-bias onset latency。
6. 做 ablation：
   - 右侧 KC/DAN/MBON silencing；
   - 左侧 KC/DAN/MBON silencing；
   - bilateral silencing；
   - NT-weight perturbation；
   - degree/weight-matched null。

## 当前限制

- 当前容器内 GPU 不可用，`torch.cuda.is_available() == False`，但 MuJoCo EGL 渲染可用。
- 当前行为实验是 proof-of-concept，不是最终生物学证据。
- 要证明论文结论，需要把行为参数从真实连接组功能仿真自动推导出来，并跑足随机重复和统计对照。
