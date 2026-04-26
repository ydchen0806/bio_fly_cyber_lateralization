# Nature 级果蝇蘑菇体侧化结构-功能仿真实验报告

生成时间：2026-04-26 02:58:06  
项目目录：`/unify/ydchen/unidit/bio_fly`  
环境目录：`/unify/ydchen/unidit/bio_fly/env`

## 1. 一句话结论

本工程已经可以运行：`FlyWire v783` 结构数据下载与整理、Eon/Shiu 风格全脑 LIF smoke 复现、KC neurotransmitter 输入侧化统计、真实 KC-NT 候选到 signed propagation 功能传播、FlyGym/MuJoCo 行为渲染和 2×2 论文对比视频。当前最强证据是结构组学发现：主要 KC subtype 中 serotonin 输入呈一致右侧富集，glutamate 输入呈显著左侧偏置，α′β′ 记忆相关 Kenyon cell subtype 的效应最大。

## 2. 当前可发表级核心发现

### 2.1 方向一致性

| NT   | 预期方向 | 成功 subtype | 最小 FDR q |
| ---- | ---- | ---------- | -------- |
| ser  | 右侧富集 | 9/9        | 9.19e-48 |
| glut | 左侧偏置 | 7/9        | 1.52e-50 |
| gaba | 左侧偏置 | 5/9        | 1.13e-20 |
| da   | 右侧富集 | 6/9        | 1.30e-22 |

### 2.2 最大效应候选

| KC subtype | NT   | left n | right n | LI     | Cohen d | FDR q    |
| ---------- | ---- | ------ | ------- | ------ | ------- | -------- |
| KCa'b'-ap2 | glut | 138    | 160     | -0.250 | -1.467  | 7.58e-26 |
| KCa'b'-m   | glut | 164    | 174     | -0.238 | -1.467  | 3.10e-28 |
| KCab-s     | glut | 311    | 310     | -0.274 | -1.457  | 1.52e-50 |
| KCa'b'-ap2 | ser  | 138    | 160     | +0.323 | +1.446  | 1.09e-25 |
| KCa'b'-ap1 | da   | 148    | 132     | +0.143 | +1.423  | 1.30e-22 |
| KCa'b'-m   | ser  | 164    | 174     | +0.274 | +1.348  | 5.76e-28 |
| KCa'b'-ap1 | ser  | 148    | 132     | +0.348 | +1.338  | 2.12e-27 |
| KCa'b'-ap2 | da   | 138    | 160     | +0.122 | +1.262  | 1.91e-20 |
| KCa'b'-ap2 | gaba | 138    | 160     | -0.123 | -1.260  | 1.13e-20 |
| KCa'b'-ap1 | gaba | 148    | 132     | -0.109 | -1.108  | 3.11e-17 |

解释：`LI = (right - left) / (right + left)`，正值表示右侧富集，负值表示左侧偏置。这个表说明 α′β′ 和 KCab-s 是当前最值得深挖的结构切入点，其中 `KCa'b'` 与记忆形成、调制输入和 MBON/DAN 回路最直接相关。

## 3. 复现和运行命令

```bash
cd /unify/ydchen/unidit/bio_fly
source env/bin/activate

# 0) 可选：使用网络代理
export http_proxy=http://192.168.32.28:18000
export https_proxy=http://192.168.32.28:18000

# 1) 环境和资源检查
python -m pip check
python scripts/estimate_resources.py

# 2) Eon/Shiu 风格全脑 LIF smoke 复现
python scripts/run_repro_smoke.py

# 3) FlyWire 注释与 proofread connection 数据
python scripts/download_flywire_data.py --prepare-annotations --download-small --download-connections

# 4) KC neurotransmitter 输入侧化统计与图
python scripts/analyze_kc_nt_lateralization.py

# 5) 真实结构候选 -> GPU signed propagation -> 行为参数
python scripts/build_model_linkage.py --steps 3 --max-active 5000 \
  --propagation-backend torch --device cuda:0 --output-dir outputs/model_linkage_gpu

# 5b) GPU benchmark
python scripts/benchmark_gpu_propagation.py --device cuda:0 --steps 3 --max-active 5000 --max-specs 6

# 6) 数据驱动 FlyGym 行为仿真和轨迹图
python scripts/run_behavior_memory_experiment.py \
  --condition-table outputs/model_linkage_gpu/derived_behavior_conditions.csv \
  --n-trials 1 --run-time 0.5 --output-dir outputs/behavior_data_driven

# 7) 行为汇总图和 2×2 论文对比视频
python scripts/summarize_behavior_results.py --summary outputs/behavior/memory_choice_summary.csv
python scripts/make_behavior_comparison_video.py --cs-plus-side left
python scripts/make_behavior_comparison_video.py --cs-plus-side right --output outputs/behavior/paper_comparison_cs_plus_right.mp4

# 8) 回归测试
python -m pytest -q
```

## 4. 生成文件含义

| 名称               | 含义                                                             | 路径                                                                      | 大小        |
| ---------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------- | --------- |
| KC NT 神经元输入表     | 每个 KC 的输入突触数与 GABA/ACh/Glu/Oct/Ser/DA fraction                 | outputs/kc_nt_lateralization/kc_neuron_nt_inputs.parquet                | 644.82 KB |
| 侧化统计表            | subtype × NT 的 Mann–Whitney/Welch/FDR/effect size/bootstrap CI | outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv                   | 19.99 KB  |
| 方向一致性检验          | Ser/Glu/GABA/DA 在主要 KC subtype 上的方向 binomial test              | outputs/kc_nt_lateralization/nt_direction_binomial_tests.csv            | 147.00 B  |
| Serotonin 上游来源   | ser_avg≥0.5 的 KC 上游输入按 pre class/type 汇总                       | outputs/kc_nt_lateralization/serotonin_dominant_upstream_by_class.csv   | 21.69 KB  |
| NT 侧化热图          | 红=右侧富集，蓝=左侧富集，用于主文结构发现图                                        | outputs/kc_nt_lateralization/figures/Fig_NT_lateralization_heatmap.png  | 175.70 KB |
| Ser/Glu forest 图 | 展示 Ser 右偏与 Glu 左偏的 bootstrap CI                                | outputs/kc_nt_lateralization/figures/Fig_serotonin_glutamate_forest.png | 92.05 KB  |
| 功能候选 manifest    | 真实 KC-NT 侧化候选被转成传播扰动 seed/silence/readout                      | outputs/model_linkage_gpu/kc_nt_perturbation_manifest.csv               | 40.30 KB  |
| 数据驱动行为参数         | 由 α′β′ Ser/Glu laterality 自动估计 FlyGym condition 参数             | outputs/model_linkage_gpu/derived_behavior_conditions.csv               | 898.00 B  |
| 行为汇总表            | 每个 condition × CS+ side 的轨迹、距离、选择结果                            | outputs/behavior/memory_choice_summary.csv                              | 3.25 KB   |
| 论文对比视频           | 2×2 panel，四个条件同步比较，适合补充视频初稿                                    | outputs/behavior/paper_comparison_cs_plus_left.mp4                      | 180.28 KB |

## 5. 结构到功能链条

| 对象                 | 行数   | 路径                                                                                        | 大小        |
| ------------------ | ---- | ----------------------------------------------------------------------------------------- | --------- |
| seed groups        | 16   | /unify/ydchen/unidit/bio_fly/outputs/model_linkage_gpu/kc_nt_seed_summary.csv             | 2.62 KB   |
| perturbation specs | 6    | /unify/ydchen/unidit/bio_fly/outputs/model_linkage_gpu/kc_nt_perturbation_manifest.csv    | 40.30 KB  |
| signed propagation | 6    | /unify/ydchen/unidit/bio_fly/outputs/model_linkage_gpu/signed_propagation_summary.csv     | 28.79 KB  |
| top targets        | 1200 | /unify/ydchen/unidit/bio_fly/outputs/model_linkage_gpu/signed_propagation_top_targets.csv | 215.71 KB |

当前实现不是只做手工参数视频，而是把真实 FlyWire KC-NT 结构发现转成了：

- `right_serotonin_kc_activate`：右侧 serotonin-enriched KC ensemble 激活；
- `left_glutamate_kc_activate`：左侧 glutamate-enriched KC ensemble 激活；
- `right_serotonin_activate_silence_left_glutamate`：激活右侧 serotonin ensemble，同时沉默左侧 glutamate ensemble；
- `left_glutamate_activate_silence_right_serotonin`：相反方向的对照；
- `right_alpha_prime_beta_prime_serotonin_activate` 与 `left_alpha_prime_beta_prime_glutamate_activate`：专门针对 α′β′ 记忆 subtype 的核心扰动。

输出的 `signed_propagation_top_targets.csv` 可以继续筛 MBON、DAN、MBIN、APL、OAN 等下游/上游回路，作为下一轮 functional validation 和实验遗传靶点候选。

## 6. 行为仿真和视频结果

### 6.1 当前视频批次

| condition                   | trial 数 | CS+ 选择率 | mean signed y | mean d(CS+) |
| --------------------------- | ------- | ------- | ------------- | ----------- |
| control                     | 2       | 1.00    | +0.475        | 3.433       |
| right_mb_serotonin_enriched | 2       | 1.00    | +0.259        | 3.588       |
| left_mb_glutamate_enriched  | 2       | 1.00    | +0.436        | 3.559       |
| bilateral_memory_blunted    | 2       | 1.00    | +0.237        | 3.825       |

### 6.2 数据驱动参数批次

| condition                   | trial 数 | CS+ 选择率 | mean signed y | mean d(CS+) |
| --------------------------- | ------- | ------- | ------------- | ----------- |
| control                     | 2       | 1.00    | +1.913        | 1.656       |
| right_mb_serotonin_enriched | 2       | 1.00    | +1.943        | 1.423       |
| left_mb_glutamate_enriched  | 2       | 1.00    | +1.963        | 1.700       |
| bilateral_memory_blunted    | 2       | 1.00    | +1.677        | 1.795       |

解释：FlyGym/MuJoCo 视频当前是“结构发现驱动的行为预测可视化”，不是湿实验结果。它的价值是展示 lateralized MB memory-bias 如何改变 odor choice trajectory，并为行为实验设计提供参数方向；Nature 级论文中必须用真实行为数据或更严谨的闭环模型来验证。

## 7. 资源和存储估计

- 当前核心数据已足够运行结构发现和功能传播：`proofread_connections_783.feather` 约 813 MB，Shiu `Connectivity_783.parquet` 约 96 MB。
- 建议 Nature 级完整包预留 `0.5–2 TB`，用于 synapse-level 表、morphology/skeleton、批量 LIF、行为视频、图表中间结果。
- 完整 `flywire_synapses_783.feather` 约 9.5 GB，建议下载后用于 synapse-level NT 位置、uncertainty 和 neuropil spatial validation。
- GPU 状态：GPU 0: NVIDIA H20Z (UUID: GPU-30223b65-8b3c-2527-d509-ab7c197f1c04); GPU 1: NVIDIA H20Z (UUID: GPU-29724d58-932e-a51c-783f-30124f012d82); GPU 2: NVIDIA H20Z (UUID: GPU-16b4829c-a8f1-6418-f760-8a2b6711ae82); GPU 3: NVIDIA H20Z (UUID: GPU-ac854859-1a99-4b9d-5a45-cdba3750d89d)；PyTorch 2.11.0+cu129: cuda_available=True, device_count=4。当前可见 GPU 与用户口头描述的 `H200` 不完全一致，`nvidia-smi` 显示为 `H20Z`；PyTorch 已切换到兼容系统 CUDA 12.9 的 `cu129` wheel，GPU 版 signed propagation 已可用。MuJoCo/FlyGym 离屏渲染已经可用，但物理仿真本身不一定主要受 PyTorch GPU 加速。

## 8. Nature 级证据链评价

### 已经较强的部分

- 真实 FlyWire proofread connection 数据支持 KC NT 输入左右侧化，不依赖 toy 数据。
- 主要 KC subtype 方向一致性强，尤其 serotonin `9/9` subtype 右侧富集。
- α′β′ 记忆相关 subtype 在 Ser/Glu/GABA/DA 上都有大效应，是明确的结构切入点。
- 已经生成主文候选图、统计表、功能传播 manifest、行为对比视频。

### 还不能过度声称的部分

- 当前 FlyGym 行为是 model-generated prediction，不等同于真实果蝇行为实验。
- signed propagation 是快速功能近似，不等价于完整 biophysical 全脑动力学。
- 完整 synapse-level 表尚未纳入，因此还缺少突触位置、NT uncertainty 和空间分布验证。
- 当前 GPU 可被 `nvidia-smi` 和 PyTorch 同时看到；批量图传播、深度模型、RL 和大规模参数扫描可以使用 GPU，Brian2 smoke 与 MuJoCo 物理仿真仍有大量 CPU 组件。

## 9. 下一步 Nature 级实验路线

1. 下载完整 `flywire_synapses_783.feather`，复现 Ser/Glu 侧化在 synapse-level 位置和 confidence 上是否稳定。
2. 把 `signed_propagation_top_targets.csv` 中的 MBON/DAN/MBIN/APL/OAN 靶点转成遗传操作候选。
3. 批量跑 Brian2/LIF：右 α′β′ serotonin 激活、左 α′β′ glutamate 激活、互作沉默和 sham control。
4. 在 FlyGym 中加入随机初始朝向、多个 odor geometry、blind analysis 和 bootstrap CI。
5. 做真实行为实验：左右 odor memory、短期/长期记忆、药理或遗传扰动、左右脑 rescue。
6. 将结构、功能传播、仿真行为和真实行为放入同一 Bayesian/causal mediation model，形成可投高水平期刊的闭环证据链。

## 10. 论文图/视频建议

- 主文图 1：FlyWire KC NT 侧化 heatmap + α′β′ 聚焦结构图。
- 主文图 2：Ser/Glu forest plot + volcano + direction consistency。
- 主文图 3：右 serotonin / 左 glutamate seed 的 signed propagation 下游靶点。
- 主文图 4：FlyGym odor memory trajectory + 数据驱动条件对比。
- 扩展视频 1：`outputs/behavior/paper_comparison_cs_plus_left.mp4`。
- 扩展视频 2：`outputs/behavior/paper_comparison_cs_plus_right.mp4`。
- 扩展表：`kc_nt_fraction_stats.csv`、`kc_nt_seed_candidates.csv`、`signed_propagation_top_targets.csv`。

## 11. 四卡系统仿真升级结果

本轮新增 `outputs/four_card_suite` 作为正式四卡系统仿真交付目录。该套件在 `cuda:0 cuda:1 cuda:2 cuda:3` 上并行运行 `534` 个扰动/对照实验，包括真实 KC-NT ensemble、subtype-level ensemble、以及每组 `128` 个 side/subtype-matched random controls。总 wall time 为 `11.089 s`，输出包括全脑 propagation responses、memory-axis metrics、empirical significance、论文级图表和机制动态视频。

关键统计结论：

- `right_serotonin_kc_activate` 相对 `null_right_kc_random` 显著改变 DAN/DPM/APL/max-target/laterality 指标，FDR q≈`0.038`。
- `left_glutamate_kc_activate` 相对 `null_left_kc_random` 显著增强 memory-axis、DAN、DPM、MBIN 和 response laterality，FDR q≈`0.038`。
- α′β′ 核心 ensemble 的效应方向与结构假说一致，但在 128 个 matched controls 下部分指标仍是趋势级，提示后续需要更高 random count、synapse-level validation 和 Brian2/LIF spiking validation。

核心交付物：

- `outputs/four_card_suite/suite_perturbation_manifest.csv`：534 个真实/对照扰动。
- `outputs/four_card_suite/suite_response_metrics.csv`：memory-axis、MBON、DAN、MBIN、APL/DPM、response laterality 指标。
- `outputs/four_card_suite/suite_empirical_significance.csv`：empirical p、effect z、FDR q。
- `outputs/four_card_suite/figures/Fig1_cyber_fly_pipeline_mechanism.png`：机制与 pipeline 示意图。
- `outputs/four_card_suite/figures/Fig2_functional_metric_heatmap.png`：功能响应 heatmap。
- `outputs/four_card_suite/figures/Fig3_empirical_null_significance.png`：matched-null 消融统计图。
- `outputs/four_card_suite/figures/Fig4_memory_axis_null_distributions.png`：随机对照分布图。
- `outputs/four_card_suite/figures/Fig5_stepwise_side_class_response.png`：逐步传播 class response 图。
- `outputs/four_card_suite/videos/cyber_fly_lateralized_memory_axis.mp4`：高清动态机制演示视频。
- `outputs/four_card_suite/CYBER_FLY_NATURE_UPGRADE_REPORT.md`：四卡仿真专用实验报告。
- `docs/FULL_PROJECT_GUIDE.md`：完整项目使用指南。
- `docs/NATURE_PAPER_UPGRADE_DRAFT.md`：论文升级稿与 Nature 风格叙事框架。
