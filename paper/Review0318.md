## Title:

## Abstract
Dense connectome reconstructions now provide synaptic-resolution maps of entire brains
Dense 与 entire 是两个概念，分别体现密度和跨度，这里这样讲是不合理的。

A hierarchical graph neural network enables contrastive learning on finely sampled skeletons (3,500 nodes), improving classification by up to 31\%;
提升是量化指标，但是设计目的是让对比学习能够提取更多信息，指标说明了这种能力。

We define neurotransmitter (NT)-based 
前面加一个连接词。

establish a design principle: optimal feature scale matches circuit architecture—modulatory circuits favour local context whereas hierarchical circuits favour global context—replicated across datasets and validated by an end-to-end Graph Attention Network. U
design principle 应该不能用这个词，如果是principle起码要在多物种中验证，这里的across datasets是果蝇全脑和果蝇半脑，加上果蝇脑的刻板性，不能用来得出principle，起码用词上变更一下。
end-to-end Graph Attention Network 不确定是否有必要在Abstract中强调，end to end，起码要从连接组数据直接出发，而不是从embedding出发。

## Introduction
第一段 entire brains 用的不对，半脑和MICrONS都不是全脑，换种说法，能提供大规模连接和形态甚至于全脑（FlyWire）

handle the computational burden of finely sampled skeletons  finely sampled skeletons以及节点数出现的太突然了，这里不要提节点数，finely sampled skeletons应该是采用的形式，这里应该用抽象的词汇，例如：保留原始形态的神经元骨架。to handle还是太突然。

enrich each skeleton node with synaptic annotations and target-neuron embeddings
这个 target-neuron embeddings没有实际采用，舍弃相关描述。synaptic annotations没有显著提升，但此处暂时保留。

全文措辞注意，Kenyon Cell 是Class，KCab- 之类的是Cell type

columnar visual neurons (Tm cells) 应该改为例如(such as Tm cells) 表示只是其中的一种

Hemispheric functional asymmetry is a fundamental organising principle
across species[ 10 , 11 ], and in Drosophila long-term memory requires an anatomically asymmetric body
这个留着，我后续检查一下表述是否准确。

α′β′ KCs 这个倒了，必须是KCα′β′ neurons

原文：For connectivity, we use the mushroom body (MB) as a natural test bed for two open questions.
意见：测试发生在多个groups中，不开头就提这个，应用对象。
改为：对于连接性，NTAC等方法借助已有的细胞类型，表征神经元的连接性，这里我们在没有先验细胞类型信息的假设下尝试构建连接性，对整个十几万的神经元网络构建邻居矩阵会带来巨大的计算困难。因此，我们采用一种探查式的研究方法，借助FlyWIre提供的突触信息，尤其是突触递质类型信息，定义了邻接神经元NT统计表征和关联网络NT统计表征。

## Results
We then counted the number ，用算法统计是否不合适用count，用什么合适

一个差异是，这里的NT邻接指的是突触的NT类型，在骨架图网络中当我尝试融合突触的时候，用的是邻接神经元的NT，这样是比较