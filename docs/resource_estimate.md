# 资源与存储估算

更新时间：2026-04-26。当前主机实测资源充足：`180` 个逻辑 CPU、`920 GiB` RAM、`/unify` 可用约 `66 TB`。当前项目目录约 `7.6 GB`，主要新增来自 FlyGym/MuJoCo/PyTorch 行为仿真依赖和 FlyWire proofread connection 表；代码和输出本身仍较小。

## 当前数据足迹

| 组件 | 实测规模 | 说明 |
|---|---:|---|
| `Connectivity_783.parquet` | `96.13 MB` | 公开 FlyWire v783 连接矩阵，压缩后很小 |
| `Connectivity_783.parquet` 读入内存 | `921.14 MB` | `pandas` 展开后约 10 倍膨胀 |
| `Completeness_783.csv` | `3.17 MB` | `138,639` 个神经元索引与完成状态 |
| 连接边 | `15,091,983` | Shiu 模型使用的有向边表 |
| 用户论文包 zip | `44.59 MB` 解压内容 | 目前为文稿/图，不含可直接仿真的 root ID 表 |
| FlyWire 注释仓库 | `51 MB` | 已下载到 `external/flywire_annotations` |
| FlyWire 小型 Zenodo 文件 | `~18 MB` | 已下载 root IDs 与 per-neuron pre neuropil counts |
| `proofread_connections_783.feather` | `813 MB` | 已下载，含 `gaba/ach/glut/oct/ser/da` NT 平均值 |
| 处理后注释 | `26 MB` | `data/processed/*.parquet/csv` |
| `outputs/functional_validation` | MB 级 | 快速 signed propagation 的候选验证输出 |
| FlyGym 行为输出 | `5 MB` 级 | 已生成 MP4、轨迹 CSV 和轨迹图 |
| Python 环境 | `6.3 GB` | FlyGym examples 安装了 MuJoCo、Torch/CUDA runtime 等依赖 |

## 运行层级

### 1. 最小复现

- CPU：`8–16` 核。
- RAM：`24–48 GB`。
- 存储：`20 GB`。
- GPU：不需要。
- 用途：跑通 `Drosophila_brain_model`、单条件 Brian2 smoke test、少量输出。

### 2. 系统复现

- CPU：`16–32` 核。
- RAM：`64–128 GB`。
- 存储：`100–300 GB`。
- GPU：可选。
- 用途：批量左/右刺激、沉默、结构扰动、signed propagation、多参数 Brain2/LIF 仿真。

### 3. 深入研究与行为闭环

- CPU：`32+` 核。
- RAM：`128–256 GB`。
- 存储：`0.5–2 TB`。
- GPU：建议 1 张中高端 GPU，用于 MuJoCo/视觉输入/策略学习/大规模可视化。
- 用途：接 `NeuroMechFly/FlyGym` 身体模型，保存行为轨迹、状态缓存、多个 FlyWire/Codex 版本和论文图表中间结果。

## 为什么要预留更大存储

本仓库当前只包含 Shiu 模型所需的压缩连接矩阵；如果纳入 Nature 级证据链，需要额外保存：

- FlyWire/Codex 注释导出：`root_id`、side、cell type、paired/mirror ID、KC subtype、MBON/DAN/MBIN 标签。
- synapse-level NT 预测表：用于验证 serotonin/dopamine/glutamate/GABA 等输入组成，不在当前 zip 中。
- skeleton 与 morphology 特征：若复用你们论文中的 HGNNA/GraphDINO 表示，节点采样、路径分布和 embedding 会显著增大。
- 批量仿真输出：Shiu 仓库说明原论文 raw output 达数 GB；如果按多 seed、多参数、多随机种子、多行为场景扩展，结果会升至百 GB 到 TB 级。

## 当前机器结论

当前 `/unify` 机器足够支撑第一阶段和第二阶段：`env/bin/python scripts/run_repro_smoke.py` 已在 `2 s` 左右跑通最小 Brian2 smoke；`scripts/run_functional_validation.py --top-n 2 --steps 2` 已完成全连接矩阵上的快速 signed propagation；`scripts/analyze_kc_nt_lateralization.py` 已用真实 FlyWire proofread connections 复现 KC NT 输入侧化方向。下一阶段的瓶颈不是硬件，而是是否下载完整 `flywire_synapses_783.feather`（约 `9.5 GB`）来做 synapse-level 位置/NT 不确定性验证。

## GPU 状态

当前容器/会话中 `nvidia-smi` 已能看到 `4× NVIDIA H20Z`，每张约 `143,771 MiB` 显存，driver 为 `550.144.03`，系统 CUDA 为 `12.9`。这和用户口头描述的 `4×H200` 不完全一致，需要后续确认集群分配或 GPU 型号标签。

已修复 PyTorch CUDA：

- `torch==2.11.0+cu129`；
- `torchvision==0.26.0+cu129`；
- `torch.version.cuda == "12.9"`；
- `torch.cuda.is_available() == True`；
- `torch.cuda.device_count() == 4`。

原问题是环境里装了 `torch==2.11.0+cu130` 和 CUDA 13 runtime wheel，当前 driver/runtime 只能稳定支持 CUDA 12.9。已换成官方 `cu129` wheel，并清理/重装了匹配的 `nvidia-*-cu12` 依赖。FlyWire signed propagation 已增加 PyTorch sparse GPU 后端，真实 KC-NT 6 个扰动、3 hop、top5000 的 benchmark 约 `3.9 s`：

```bash
cd /unify/ydchen/unidit/bio_fly
source env/bin/activate
python scripts/build_model_linkage.py --steps 3 --max-active 5000 --propagation-backend torch --device cuda:0 --output-dir outputs/model_linkage_gpu
python scripts/benchmark_gpu_propagation.py --device cuda:0 --steps 3 --max-active 5000 --max-specs 6
```

FlyGym/MuJoCo 行为渲染仍可用 `MUJOCO_GL=egl`；它主要依赖物理仿真，不一定会被 PyTorch GPU 显著加速。后续真正适合 4 卡并行的是大规模 LIF 参数扫描、GPU 版图传播、视觉模型/FlyVis、RL 或批量视频编码。
