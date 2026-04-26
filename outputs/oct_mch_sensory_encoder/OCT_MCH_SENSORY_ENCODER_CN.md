# OCT/MCH 气味身份 sensory encoder 报告

保存路径：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/OCT_MCH_SENSORY_ENCODER_CN.md`

## 目的

上一版 OCT/MCH 条件表只把 `OCT_3-octanol` 和 `MCH_4-methylcyclohexanol` 作为实验标签。本轮新增 glomerulus-level sensory encoder：先把气味身份映射到候选 antennal-lobe glomeruli，再从 FlyWire 注释表中选择 ORN 和 ALPN root ids，最后可选地通过 FlyWire signed propagation 计算 KC readout。

## 重要边界

该编码器是 `literature_constrained_glomerular_encoder`，不是实测 OCT/MCH 受体响应矩阵。默认 glomerulus 列表用于生成可复现假说，后续应替换或校准为真实 ORN/PN calcium imaging、电生理或 DoOR/odor-response 数据。

## 摘要

           odor_identity  n_configured_glomeruli  total_glomerulus_weight  n_orn_seeds  n_pn_seeds  n_kc_readout  kc_abs_mass  kc_laterality_index
MCH_4-methylcyclohexanol                       3                     2.40        158.0        10.0          2203     0.526523            -0.115850
           OCT_3-octanol                       9                     5.95        426.0        44.0          2757     0.461211            -0.062238

## 输出

- glomerulus 映射表：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_glomerulus_map.csv`
- ORN/PN seed neuron 表：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_seed_neurons.csv`
- KC readout 表：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_kc_readout.csv`
- 编码器摘要：`/unify/ydchen/unidit/bio_fly/outputs/oct_mch_sensory_encoder/oct_mch_encoder_summary.csv`

## 论文写法

可以写：我们实现了一个文献约束的 OCT/MCH glomerulus-level encoder，用 FlyWire 注释自动选取 ORN/ALPN seeds，并通过连接组传播得到 KC readout。

不能写：我们已经测得 OCT/MCH 在每个 ORN 的真实响应强度，或已经复刻 Eon 私有 sensory encoder。
