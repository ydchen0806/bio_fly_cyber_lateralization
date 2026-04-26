# 数据下载与 FlyWire 蘑菇体连接组深挖报告

保存路径：`/unify/ydchen/unidit/bio_fly/docs/DATA_DOWNLOAD_AND_MB_DISCOVERY_CN.md`

## 1. 新下载/确认的数据

本轮使用代理下载并确认了 FlyWire v783 Zenodo 记录和官方注释仓库。

公开来源：

- Zenodo FlyWire v783 connectivity：`https://zenodo.org/records/10676866`
- FlyWire annotations GitHub：`https://github.com/flyconnectome/flywire_annotations`

本地数据：

- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/proofread_root_ids_783.npy`
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/per_neuron_neuropil_count_pre_783.feather`
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/per_neuron_neuropil_count_post_783.feather`
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/proofread_connections_783.feather`
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/flywire_synapses_783.feather`
- `/unify/ydchen/unidit/bio_fly/external/flywire_annotations/supplemental_files/Supplemental_file1_neuron_annotations.tsv`

下载记录：

- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866_downloads.csv`
- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866_downloads_extended.csv`

当前数据大小：

- `/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866`：`9.9G`
- `/unify/ydchen/unidit/bio_fly/data/processed`：`8.8M`
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery`：`34M`
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior`：`9.2M`

## 2. 新增代码

- `/unify/ydchen/unidit/bio_fly/src/bio_fly/mb_connectome_discovery.py`：直接读取 FlyWire v783 连接表和 annotation 表，挖掘蘑菇体左右偏侧化连接模块。
- `/unify/ydchen/unidit/bio_fly/scripts/run_mb_connectome_discovery.py`：一键运行 MB 连接组深挖。
- `/unify/ydchen/unidit/bio_fly/scripts/download_flywire_data.py`：新增 `--download-neuropil-post` 和 `--download-all`。

复现命令：

```bash
export http_proxy=http://192.168.32.28:18000
export https_proxy=http://192.168.32.28:18000
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/download_flywire_data.py --prepare-annotations --download-all
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_mb_connectome_discovery.py --output-dir /unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery
```

## 3. 数据规模和变量解释

- `root_id`：FlyWire 中一个神经元分割体的唯一 ID。
- `pre_pt_root_id`：突触前神经元 ID，即发送信号的一方。
- `post_pt_root_id`：突触后神经元 ID，即接收信号的一方。
- `syn_count`：两个神经元之间聚合后的突触数量。
- `neuropil`：突触所在脑区，例如蘑菇体、视觉区或其他神经纤维区。
- `gaba_avg`、`ach_avg`、`glut_avg`、`oct_avg`、`ser_avg`、`da_avg`：该连接被预测为 GABA、乙酰胆碱、谷氨酸、章鱼胺、血清素、多巴胺的平均概率。
- `family`：本项目根据 annotation 把细胞归入 KC、MBON、DAN、APL、DPM、OAN 等记忆相关家族。
- `right_laterality_index`：右侧偏侧化指数，公式为 `(right - left) / (right + left)`；负值表示左侧更强，正值表示右侧更强。
- `priority_score`：候选边优先级，综合突触数、是否属于记忆轴、是否同侧连接；用于筛选真实实验靶点。

本轮挖掘规模：

- 蘑菇体相关注释神经元：`5608`。
- 与蘑菇体相连的边：`817036`。
- 蘑菇体内部边：`654483`。
- KC 上游汇总行：`3135`。
- 记忆轴候选边组合：`45982`。
- 完整突触级表行数：`130054535`，列数 `18`。

## 4. 新的结构发现

### 4.1 蘑菇体细胞家族计数

| family | side | n_neurons | n_cell_types |
| --- | --- | --- | --- |
| APL | left | 1 | 1 |
| APL | right | 1 | 1 |
| DAN | left | 166 | 27 |
| DAN | right | 165 | 27 |
| DPM | left | 1 | 1 |
| DPM | right | 1 | 1 |
| KC | left | 2580 | 10 |
| KC | right | 2597 | 10 |
| MBON | left | 48 | 35 |
| MBON | right | 48 | 35 |

解释：KC 数量左右接近，但不是完全相同；MBON、APL、DPM 是高度成对的少数细胞群；DAN 左右数量也接近。这说明后续偏侧化主要不是简单由“某侧细胞多很多”解释，而更可能来自连接强度和连接模式。

### 4.2 主要家族连接的左右偏侧化

| pre_family | post_family | left | right | right_laterality_index | total_ipsilateral_syn_count |
| --- | --- | --- | --- | --- | --- |
| KC | KC | 2.032e+05 | 1.761e+05 | -0.07155 | 3.793e+05 |
| KC | MBON | 8.932e+04 | 8.921e+04 | -0.0006162 | 1.785e+05 |
| KC | APL | 6.056e+04 | 5.626e+04 | -0.03677 | 1.168e+05 |
| APL | KC | 5.349e+04 | 4.514e+04 | -0.08458 | 9.863e+04 |
| KC | DPM | 4.82e+04 | 3.982e+04 | -0.0952 | 8.803e+04 |
| KC | DAN | 4.094e+04 | 3.607e+04 | -0.0632 | 7.7e+04 |
| DAN | KC | 2.017e+04 | 1.725e+04 | -0.07816 | 3.742e+04 |
| MBON | MBON | 5127 | 4933 | -0.01928 | 1.006e+04 |
| DPM | KC | 5169 | 4109 | -0.1142 | 9278 |
| DAN | MBON | 3721 | 3995 | 0.03551 | 7716 |
| MBON | KC | 4329 | 2625 | -0.245 | 6954 |
| MBON | DAN | 2393 | 2747 | 0.06887 | 5140 |
| APL | DPM | 1276 | 661 | -0.3175 | 1937 |
| MBON | APL | 880 | 995 | 0.06133 | 1875 |
| APL | MBON | 979 | 893 | -0.04594 | 1872 |
| DAN | APL | 953 | 839 | -0.06362 | 1792 |
| DPM | MBON | 900 | 865 | -0.01983 | 1765 |
| DPM | APL | 1058 | 679 | -0.2182 | 1737 |
| DAN | DAN | 602 | 553 | -0.04242 | 1155 |
| APL | DAN | 645 | 484 | -0.1426 | 1129 |

生物意义：

- `KC→KC`、`APL→KC`、`KC→DPM`、`DPM→KC` 等内在/反馈环路整体偏左。
- `DAN→MBON`、`MBON→DAN` 有轻度右偏，提示调制/输出轴可能与 KC 内在反馈轴具有不同侧化方向。
- `KC→MBON` 基本左右平衡，说明输出通路不是全局单侧缺失，而是更细粒度的 cell type / neuromodulator 差异。

### 4.3 记忆轴候选边

| pre_family | post_family | pre_side | post_side | pre_cell_type | post_cell_type | dominant_edge_nt | syn_count | n_pre | n_post | priority_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KC | KC | left | left | KCab | KCab | ACh | 7.846e+04 | 844 | 844 | 9.022e+04 |
| KC | KC | right | right | KCab | KCab | ACh | 7.352e+04 | 799 | 799 | 8.455e+04 |
| KC | KC | left | left | KCg-m | KCg-m | ACh | 6.565e+04 | 1066 | 1069 | 7.55e+04 |
| KC | KC | right | right | KCg-m | KCg-m | ACh | 5.455e+04 | 1120 | 1120 | 6.273e+04 |
| KC | APL | left | left | KCg-m | APL | ACh | 2.377e+04 | 1066 | 1 | 4.1e+04 |
| KC | APL | right | right | KCg-m | APL | ACh | 2.158e+04 | 1120 | 1 | 3.722e+04 |
| APL | KC | left | left | APL | KCg-m | GABA | 2.074e+04 | 1 | 1069 | 3.577e+04 |
| KC | APL | right | right | KCab | APL | ACh | 1.882e+04 | 799 | 1 | 3.246e+04 |
| KC | APL | left | left | KCab | APL | ACh | 1.834e+04 | 844 | 1 | 3.163e+04 |
| APL | KC | right | right | APL | KCg-m | GABA | 1.721e+04 | 1 | 1120 | 2.969e+04 |
| APL | KC | left | left | APL | KCab | GABA | 1.67e+04 | 1 | 844 | 2.88e+04 |
| APL | KC | right | right | APL | KCab | GABA | 1.534e+04 | 1 | 799 | 2.646e+04 |
| KC | DPM | left | left | KCg-m | DPM | ACh | 1.513e+04 | 1066 | 1 | 2.609e+04 |
| KC | DPM | left | left | KCab | DPM | ACh | 1.269e+04 | 844 | 1 | 2.19e+04 |
| KC | DPM | right | right | KCg-m | DPM | ACh | 1.21e+04 | 1120 | 1 | 2.086e+04 |
| KC | MBON | left | left | KCg-m | MBON09 | ACh | 1.073e+04 | 1064 | 2 | 1.851e+04 |
| KC | MBON | right | right | KCab | MBON14 | ACh | 1.062e+04 | 798 | 2 | 1.833e+04 |
| KC | MBON | left | left | KCab | MBON07 | ACh | 1.045e+04 | 844 | 2 | 1.802e+04 |
| KC | MBON | right | right | KCab | MBON07 | ACh | 1.019e+04 | 799 | 2 | 1.758e+04 |
| KC | MBON | left | left | KCab | MBON14 | ACh | 9239 | 842 | 2 | 1.594e+04 |
| KC | DPM | right | right | KCab | DPM | ACh | 9222 | 796 | 1 | 1.591e+04 |
| KC | MBON | right | right | KCg-m | MBON09 | ACh | 8859 | 1111 | 2 | 1.528e+04 |
| KC | KC | left | left | KCapbp-m | KCapbp-m | ACh | 1.286e+04 | 164 | 164 | 1.478e+04 |
| KC | MBON | right | left | KCg-m | MBON05 | ACh | 9263 | 1111 | 1 | 1.389e+04 |
| KC | MBON | left | right | KCg-m | MBON05 | ACh | 8709 | 1064 | 1 | 1.306e+04 |

生物意义：

- `KCg-m→APL` 和 `APL→KCg-m` 构成强反馈环，且左侧突触数高于右侧，是“左侧抑制反馈增强”的强候选。
- `KC→DPM` 和 `DPM→KC` 同样左偏，适合连接到记忆维持和巩固假说。
- `KC→MBON09/MBON14/MBON07` 是输出候选，可作为行为读出的下游靶点。

## 5. 基于新结构发现的仿真验证

根据新增结构结果，构造了 5 个行为条件：

- `balanced_connectome_control`：平衡对照。
- `left_kc_apl_dpm_loop_enriched`：模拟左侧 KC-APL-DPM 反馈环增强。
- `left_kc_intrinsic_recurrent_enriched`：模拟左侧 KC 内在递归环增强。
- `right_dan_mbon_output_enriched`：模拟右侧 DAN-MBON 输出/调制轴增强。
- `left_feedback_right_output_conflict`：模拟左侧反馈增强与右侧输出增强冲突。

条件表：`/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior/conditions/mb_discovery_behavior_conditions.csv`

行为结果：

| condition | n_trials | cs_plus_choice_rate | mean_approach_margin | mean_signed_final_y | mean_path_length |
| --- | --- | --- | --- | --- | --- |
| balanced_connectome_control | 2 | 1 | 5.389 | 2.72 | 7.307 |
| left_feedback_right_output_conflict | 2 | 1 | 5.336 | 2.759 | 7.259 |
| left_kc_apl_dpm_loop_enriched | 2 | 1 | 5.415 | 2.726 | 7.264 |
| left_kc_intrinsic_recurrent_enriched | 2 | 1 | 5.091 | 2.83 | 6.942 |
| right_dan_mbon_output_enriched | 2 | 1 | 5.198 | 2.722 | 7.419 |

解释：当前小样本行为仿真中所有条件均选择 CS+，说明二分类选择率已经饱和；但 `mean_approach_margin`、`mean_signed_final_y`、`mean_path_length` 仍可用于比较轨迹差异。论文中应把连续轨迹指标作为主结果，而不是只报告 choice rate。

## 6. 新图和视频

结构图：

- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_mb_family_transition_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_mb_transition_laterality.png`
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_kc_upstream_nt_by_side.png`
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/figures/Fig_memory_axis_candidate_targets.png`

机制视频：

- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_discovery/videos/mb_lateralization_mechanism.mp4`

行为视频：

- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior/videos/mb_discovery_behavior_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/mb_connectome_behavior/videos/mb_discovery_behavior_cs_plus_right.mp4`

## 7. 可补入文章的核心句子

> Direct mining of FlyWire v783 neuron-to-neuron connectivity identified a left-biased KC-APL-DPM feedback module, whereas DAN-MBON modulatory/output transitions showed a weak right-biased tendency. This dissociation suggests that mushroom-body lateralization may not represent a global left-right imbalance, but a division between recurrent memory stabilization and modulatory output channels.

中文含义：FlyWire v783 连接表显示，左侧 KC-APL-DPM 反馈模块更强，而 DAN-MBON 调制/输出通路有轻度右偏。这提示蘑菇体左右侧化不是简单的一侧更强，而可能是“左侧偏记忆反馈/稳定，右侧偏调制输出”的分工。

## 8. 下一步最值得做的真实实验

1. 用 `3-octanol` 和 `isoamyl acetate` 做 CS+/CS- 可交换嗅觉记忆实验。
2. 单侧抑制或激活 APL/DPM，测试左侧反馈增强是否改变长期记忆保持。
3. 单侧操控 DAN/MBON09/MBON14，测试右侧调制/输出轴是否改变冲突条件下的选择。
4. 主指标使用 `approach margin`、`side-specific margin shift` 和轨迹曲率，不只使用 `choice rate`。
5. 对 `cs_plus_weak_conflict` 条件做高重复数真实行为验证，因为该条件最能区分感觉强度与记忆强度。
