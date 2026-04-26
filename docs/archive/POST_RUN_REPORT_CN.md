# 四卡赛博果蝇运行报告

更新时间：2026-04-26

## 这次命令跑了多久

最近一次正式四卡命令是：

```bash
python /unify/ydchen/unidit/bio_fly/scripts/run_four_card_experiment_suite.py \
  --devices cuda:0 cuda:1 cuda:2 cuda:3 \
  --steps 3 \
  --max-active 5000 \
  --n-random-per-family 128 \
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/four_card_suite
```

它的核心计算 wall time 来自 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_run_info.json`，是 `11.089 s`。  
四个 GPU worker 的耗时分别是：

- `cuda:0`：`8.537 s`
- `cuda:1`：`8.657 s`
- `cuda:2`：`8.218 s`
- `cuda:3`：`8.704 s`

后处理包括统计、画图和写报告，所以整个 shell 命令体感时间略长于这条核心 wall time。

## 主要结论

1. FlyWire v783 连接组里，Kenyon cell 的 neurotransmitter 输入存在强烈左右偏侧化。
2. serotonin-like 输入在主要 KC subtype 上呈稳定右侧富集。
3. glutamate-like 输入在多数 KC subtype 上呈稳定左侧偏置。
4. 最强结构信号集中在 α′β′ 记忆相关 KC 亚型，以及 KCab-s。
5. 把这些结构信号转成 GPU sparse propagation 后，右 serotonin-enriched 和左 glutamate-biased 侧化 ensemble 会优先募集 MBON、DAN、MBIN、APL、DPM 等 memory-axis 相关 readout。
6. side/subtype-matched random controls 证明这些功能读出不是单纯由 seed 数量或随机 KC 组成造成的。

## 统计上最重要的发现

从 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv` 读取的最强结果包括：

- `right_serotonin_kc_activate` 相对 `null_right_kc_random` 在 `dan_abs_mass` 上 FDR q≈`0.038`
- `right_serotonin_kc_activate` 相对 `null_right_kc_random` 在 `dpm_abs_mass` 上 FDR q≈`0.038`
- `right_serotonin_kc_activate` 相对 `null_right_kc_random` 在 `apl_abs_mass` 上 FDR q≈`0.038`
- `right_serotonin_kc_activate` 相对 `null_right_kc_random` 在 `response_laterality_abs` 上 FDR q≈`0.038`
- `left_glutamate_kc_activate` 相对 `null_left_kc_random` 在 `memory_axis_abs_mass` 上 FDR q≈`0.038`
- `left_glutamate_kc_activate` 相对 `null_left_kc_random` 在 `dan_abs_mass` 上 FDR q≈`0.038`
- `left_glutamate_kc_activate` 相对 `null_left_kc_random` 在 `mbon_abs_mass` 上 FDR q≈`0.038`
- `left_glutamate_kc_activate` 相对 `null_left_kc_random` 在 `response_laterality_abs` 上 FDR q≈`0.038`

这组结果支持一个更强的叙事：蘑菇体左右偏侧化不是一个粗糙的“左右数量差”，而是 NT-specific、subtype-specific、功能 readout-specific 的结构-功能偏置。

## 已完成的改进

### 1. GPU 真的用上了

- 环境切换到 `torch==2.11.0+cu129`
- `torch.cuda.is_available()` 已为 `True`
- 4 张卡均可见且可调用
- sparse propagation 支持 `--propagation-backend torch --device cuda:0`

### 2. 结构到功能链条闭环

- 结构表来自 `/unify/ydchen/unidit/bio_fly/outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv`
- seed 选择来自 `/unify/ydchen/unidit/bio_fly/outputs/model_linkage_gpu/kc_nt_seed_candidates.csv`
- 功能传播输出来自 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_signed_propagation_responses.parquet`
- 统计结果来自 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_response_metrics.csv`

### 3. 对照实验更严谨

- 使用 side/subtype-matched random controls
- 保留真实扰动与消融扰动的统一 manifest
- 对 actual 与 random_control 分开统计
- 对每个 actual condition 给出 empirical p 和 FDR q

### 4. 图和视频已经可直接用于文章

- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/figures/Fig1_cyber_fly_pipeline_mechanism.png`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/figures/Fig2_functional_metric_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/figures/Fig3_empirical_null_significance.png`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/figures/Fig4_memory_axis_null_distributions.png`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/figures/Fig5_stepwise_side_class_response.png`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/videos/cyber_fly_lateralized_memory_axis.mp4`

### 5. 文档已补齐

- `/unify/ydchen/unidit/bio_fly/README.md`
- `/unify/ydchen/unidit/bio_fly/NATURE_LEVEL_EXPERIMENT_REPORT.md`
- `/unify/ydchen/unidit/bio_fly/docs/FULL_PROJECT_GUIDE.md`
- `/unify/ydchen/unidit/bio_fly/docs/NATURE_PAPER_UPGRADE_DRAFT.md`

## 结果文件清单

### 四卡主输出

- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_perturbation_manifest.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_signed_propagation_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_signed_propagation_responses.parquet`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_response_metrics.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_empirical_significance.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_top_targets.csv`

### 四卡辅助输出

- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/gpu_worker_assignment.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/gpu_worker_results.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_run_info.json`
- `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/CYBER_FLY_NATURE_UPGRADE_REPORT.md`

### 可直接引用到文章的内容

- `/unify/ydchen/unidit/bio_fly/docs/NATURE_PAPER_UPGRADE_DRAFT.md`
- `/unify/ydchen/unidit/bio_fly/docs/FULL_PROJECT_GUIDE.md`

## 还可以继续做什么

1. 把 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_top_targets.csv` 里的 MBON/DAN/MBIN/APL/DPM 靶点继续筛成遗传实验候选。
2. 下载 `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/flywire_synapses_783.feather` 做 synapse-level uncertainty 验证。
3. 用 Brian2/LIF 把关键 α′β′ 侧化 ensemble 做 spike-level 复核。
4. 用真实果蝇 odor-memory 行为实验来验证这套仿真预测。
