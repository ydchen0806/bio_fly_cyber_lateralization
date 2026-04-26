# 左右脑蘑菇体不对称性与记忆研究计划

目标不是只“复现一个仿真”，而是把你们在 FlyWire 统计中发现的 KC/蘑菇体 NT 不对称转化为可检验的功能预测：结构不对称是否会改变活动传播、记忆回路读出和闭环行为。

## 0. 外部复现目标

Eon Systems 的路线可以拆成两层：第一层是基于 FlyWire 全脑连接组的脑网络仿真，第二层是把脑输出接到物理身体/行为环境中做 embodied brain emulation。当前仓库先复现第一层，并预留第二层接口。

关键参考：

- Eon Systems embodied brain emulation：<https://eon.systems/updates/embodied-brain-emulation>
- Shiu 等 Nature 2024 全脑 LIF 模型：<https://www.nature.com/articles/s41586-024-07763-9>
- Shiu 官方代码：<https://github.com/philshiu/Drosophila_brain_model>
- FlyWire Codex 数据入口：<https://codex.flywire.ai/>
- NeuroMechFly/FlyGym 闭环身体模型：<https://neuromechfly.org/>、<https://github.com/NeLy-EPFL/flygym>

## 1. 当前实现程度

已完成：

- `external/Drosophila_brain_model`：本地已有 Shiu 模型与 FlyWire v783/v630 连接矩阵。
- `env`：Python 3.10 venv 已补齐 `pytest`，`pip install -e ".[dev]"` 已成功。
- `scripts/run_repro_smoke.py`：Brian2 最小 smoke test 已跑通，输出在 `outputs/repro/smoke_test.parquet`。
- `scripts/estimate_resources.py`：可报告全脑连接矩阵 footprint。
- `scripts/analyze_mushroom_body_asymmetry.py`：可从 FlyWire metadata 表生成左右成对 MB/KC/MBON laterality 指标。
- `scripts/extract_paper_findings.py`：可解析用户论文 zip 中的 memory/lateralization 文本 claims 和 figure inventory。
- `scripts/run_functional_validation.py`：可把结构不对称候选对转成扰动 manifest，并用 signed multi-hop propagation 做快速功能验证；可选 `--execute-lif` 运行有限 Brian2/LIF 实验。
- `scripts/analyze_kc_nt_lateralization.py`：已用 `proofread_connections_783.feather` 计算 KC subtype × hemisphere × NT 输入，当前复现到 serotonin 9/9 subtype 右富集、glutamate 8/9 subtype 左偏。
- `scripts/run_behavior_memory_experiment.py`：已用 FlyGym/MuJoCo EGL 离屏渲染跑通左右镜像 odor-memory choice，生成 MP4、轨迹 CSV 和 summary。

目前限制：

- 用户 zip 是文稿和图，`root_id_hits = 0`，缺少可直接仿真的候选 root ID 表。
- 当前 demo metadata 只有 2 对神经元；真实研究需要 FlyWire/Codex 导出的 KC subtype、side、paired root、NT input profile、upstream class 表。
- Shiu 模型连接表只有 excitatory/inhibitory signed weight，不包含完整 synapse-level NT 分类；NT 结论需要额外接入 NT 表。

## 2. 中心假设

### H1：结构层

左右蘑菇体不是完全镜像，尤其在 KC `α′β′` lobe、serotonin/dopamine/glutamate/GABA 输入组成上存在稳定 laterality。

### H2：功能层

这些 laterality 不是纯统计差异，而会改变从 KC/MBIN/DAN/MBON 到下游回路的活动传播：右侧 serotonin/DAN 富集应使部分 `α′β′` KC subtype 在记忆巩固相关扰动下产生更强或更持久的响应。

### H3：行为层

如果结构差异能在仿真中放大到 MBON/DAN/descending pathway readout，就可能对应 odor memory retrieval、approach/avoidance、左右转向偏置或抗干扰记忆保持差异。

## 3. 研究路线

### Phase A：复现全脑脑模型

1. 固定 Python/Brian2/数据版本。
2. 跑通 smoke test。
3. 批量运行左激活、右激活、同侧/对侧沉默。
4. 输出 spike parquet、实验 manifest、参数 JSON。

### Phase B：把你们论文发现转成候选节点

1. 从论文 zip 抽取 claims：serotonin right-enrichment、glutamate left-bias、`α′β′` strongest effect、DAN upstream imbalance。
2. 从 FlyWire/Codex 导出表补齐 root ID：KC subtype、side、pair/mirror ID、upstream NT、upstream cell class。
3. 生成候选列表：每个 subtype 的 top asymmetric KC、DAN/MBIN、MBON、APL/OAN。
4. 生成扰动设计：单侧激活、对侧沉默、同侧 upstream silencing、NT-weight perturbation。

### Phase C：快速功能筛选

1. 使用 signed multi-hop propagation 先做 cheap screening。
2. 对每个候选计算：
   - left/right response absolute mass；
   - top downstream overlap；
   - MBON/DAN/readout score；
   - silence 后 response drop；
   - degree/weight-matched null model z-score。
3. 只把最强的候选送入 Brian2/LIF，避免全组合爆炸。

### Phase D：Brian2/LIF 功能验证

1. 复用 Shiu 模型的 activation/silencing 接口。
2. 对候选 pair 运行：
   - `left_activate` vs `right_activate`；
   - `left_activate_silence_right` vs `right_activate_silence_left`；
   - upstream DAN/MBIN silencing；
   - weight scaling or sign-preserving perturbation。
3. 读出：
   - 全脑 spike count / active neuron count；
   - MBON/DAN/APL/readout 集合响应；
   - response laterality index；
   - trial-to-trial variability；
   - perturbation sensitivity。

### Phase E：闭环行为

1. 将 MBON/DAN/descending pathway 活动映射到行为变量。
2. 对接 NeuroMechFly/FlyGym 或 Eon 风格 MuJoCo 身体。
3. 做 odor learning / retrieval 的简化任务：
   - CS+/CS- 输入；
   - punishment/reward DAN input；
   - retrieval 阶段比较左/右 pathway；
   - readout 为趋近/回避、转向偏置、轨迹熵、速度变化。

## 4. 统计与对照

必须做的 Nature 级对照：

- hemisphere label permutation。
- degree/weight-preserving edge rewiring。
- pair-matched null：同 subtype 左右随机配对。
- NT-label uncertainty：尤其 serotonin 预测准确率与 DAN/serotonin co-occurrence 的解释。
- FlyWire v783/v630 与 hemibrain 交叉验证。
- 多参数鲁棒性：`w_syn`、activation rate、trial duration、threshold、random seed。
- 多读出一致性：signed propagation、Brian2 spike、闭环行为三层是否同向。

## 5. 近期可执行任务

1. 从 Codex/FlyWire 导出真实 metadata：`root_id, side, cell_type, subtype, pair_id/paired_root_id, super_class`。
2. 导出或整理 synapse-level NT input profile：至少按 KC subtype × hemisphere × NT 聚合。
3. 运行 `scripts/analyze_mushroom_body_asymmetry.py --metadata <metadata.csv>`。
4. 运行 `scripts/run_functional_validation.py --top-n 50 --steps 3`。
5. 对最强 10–20 个候选加 `--execute-lif` 做 Brian2 验证。
6. 汇总成一张主图：结构 laterality → signed propagation → LIF spike response → behavioral readout prediction。

## 6. 投稿定位

“Nature”级别需要的不只是算法复现，而是一个新生物学结论加跨层验证。最有潜力的主线是：

> Adult FlyWire connectome reveals neurotransmitter-specific lateralization in mushroom-body memory circuits, and connectome-constrained brain emulation predicts lateralized memory retrieval dynamics.

可投主图逻辑：

1. NT-level KC laterality 统计发现。
2. 上游 cell-class decomposition 指向 DAN/MBIN/DPM-like imbalance。
3. 结构 laterality 预测 signed propagation 差异。
4. Brian2/LIF perturbation 验证单侧激活/沉默产生非对称响应。
5. 闭环行为模型预测 odor memory retrieval 或 turning bias。
6. 最好补 wet-lab/公开 calcium/behavior 数据验证，否则更适合 Nature Communications / eLife / PNAS / Neuron computational track。
