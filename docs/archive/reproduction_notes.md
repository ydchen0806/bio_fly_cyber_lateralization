# 复现与运行说明

## 代码入口

```bash
cd /unify/ydchen/unidit/bio_fly
source env/bin/activate
python scripts/estimate_resources.py
python scripts/run_repro_smoke.py
python scripts/extract_paper_findings.py
python scripts/run_functional_validation.py --top-n 2 --steps 2 --max-active 1000
python scripts/download_flywire_data.py --prepare-annotations --download-small
python scripts/analyze_kc_nt_lateralization.py
python scripts/run_behavior_memory_experiment.py --conditions control right_mb_serotonin_enriched --n-trials 1 --run-time 0.2
```

## 复现层级

### Level 1：Shiu 全脑 LIF

`src/bio_fly/repro.py` 封装了 `external/Drosophila_brain_model/model.py`，默认使用：

- `external/Drosophila_brain_model/Completeness_783.csv`
- `external/Drosophila_brain_model/Connectivity_783.parquet`
- `outputs/repro`

`scripts/run_repro_smoke.py` 已验证可跑通。批量实验不要直接全组合运行，先用 `scripts/run_functional_validation.py` 生成候选和 cheap screening。

### Level 2：结构不对称分析

输入 metadata 表至少需要：

- `root_id`
- `side` 或 `hemisphere`
- `cell_type`/`type`/`classification`
- `paired_root_id` 或 `pair_id`

运行：

```bash
python scripts/analyze_mushroom_body_asymmetry.py \
  --metadata path/to/flywire_metadata.csv \
  --output-dir outputs/asymmetry_real
```

### Level 3：功能验证

运行：

```bash
python scripts/run_functional_validation.py \
  --pairwise outputs/asymmetry_real/mushroom_body_pairwise_asymmetry.csv \
  --top-n 50 \
  --steps 3 \
  --max-active 5000
```

如需 Brian2/LIF：

```bash
python scripts/run_functional_validation.py \
  --pairwise outputs/asymmetry_real/mushroom_body_pairwise_asymmetry.csv \
  --top-n 10 \
  --steps 3 \
  --execute-lif \
  --lif-max-experiments 20 \
  --lif-t-run-ms 100 \
  --lif-n-run 3
```

## 输出文件

- `outputs/paper_findings/paper_inventory.json`：论文 zip 文件组成。
- `outputs/paper_findings/memory_lateralization_claims.csv`：从论文包抽取的 KC/NT/记忆相关 claims。
- `outputs/functional_validation/perturbation_manifest.csv`：左右激活/沉默实验清单。
- `outputs/functional_validation/signed_propagation_summary.csv`：快速功能传播读出。
- `outputs/functional_validation/signed_propagation_responses.parquet`：每个条件多跳传播节点分数。
- `outputs/functional_validation/left_right_response_overlap.csv`：左右激活下游 top response overlap。
- `data/processed/flywire_neuron_annotations.parquet`：FlyWire neuron annotation parquet。
- `data/processed/flywire_mushroom_body_annotations.parquet`：蘑菇体相关注释子集。
- `outputs/kc_nt_lateralization/kc_nt_lateralization_effects.csv`：KC subtype × NT 左右输入差异。
- `outputs/kc_nt_lateralization/serotonin_dominant_upstream_by_class.csv`：serotonin-dominant KC 输入上游类别分解。
- `outputs/behavior_oriented/*.mp4`：FlyGym/MuJoCo 离屏渲染行为视频。
- `outputs/behavior_oriented/memory_choice_summary.csv`：行为 choice/trajectory 指标汇总。

## 当前关键观察

用户论文包 `Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip` 中没有检测到 FlyWire root ID，因此它不能单独驱动仿真。它可以提供 hypotheses 和 figure/claim inventory；真正仿真必须补充 Codex/FlyWire 导出的 root ID 级别表。

当前 demo 运行显示，两对示例神经元左右激活的 top200 response Jaccard 约 `0.58–0.61`，说明左右输入并非完全同分布；但 demo metadata 过小，不能作为生物学结论。
