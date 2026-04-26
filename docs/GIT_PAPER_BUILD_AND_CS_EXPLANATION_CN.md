# Git 配置、论文编译和 CS+/CS- 行为实验解释

保存路径：`/unify/ydchen/unidit/bio_fly/docs/GIT_PAPER_BUILD_AND_CS_EXPLANATION_CN.md`

## 1. Git 信息

本地仓库路径：`/unify/ydchen/unidit/bio_fly`

已配置：

```bash
cd /unify/ydchen/unidit/bio_fly
git config user.name "ydchen0806"
git config user.email "yindachen@mail.ustc.edu.cn"
```

当前远程仓库：

```bash
origin  https://github.com/ydchen0806/bio_fly_cyber_lateralization.git
```

安全说明：GitHub token 不应写入仓库、README、脚本或 `.git/config`。如果 token 已经在任何对话、日志或终端历史中出现，应立即在 GitHub 里撤销并重新生成。后续推送建议使用 GitHub CLI、credential helper 或一次性环境变量，不要把 token 固化到项目文件。

## 2. CS+/CS- 是什么

`CS` 是 conditioned stimulus，即“条件刺激”。在果蝇嗅觉记忆实验中，它通常是一种气味，而不是食物本身。

- `CS+`：训练时和糖/食物奖励绑定的气味。果蝇学会“闻到这个气味意味着有糖或食物”。
- `CS-`：训练时不和奖励绑定的中性气味，或在冲突实验中作为竞争/诱饵气味。

因此，CS+/CS- 的核心不是“视频里有一个食物物体”，而是“气味是否预测食物”。训练阶段可以同时出现气味和糖；测试阶段通常只出现气味，观察果蝇是否靠近 CS+。

## 3. 为什么之前视频里没有食物

当前 FlyGym 仿真模拟的是“记忆测试阶段”，不是“训练阶段”。测试阶段只需要呈现两个气味源：

- 橙色标记：CS+，表示学会后预测糖/食物奖励的气味。
- 蓝色标记：CS-，表示中性或诱饵气味。

所以视频里没有实体食物并不是仿真错误，而是实验范式的设计：我们要测的是“果蝇是否根据记忆靠近预测食物的气味”。为了让非生物背景读者看懂，我已经重新生成了带图例的视频，画面上方明确写出：

- `CS+ learned food/sugar cue`
- `CS- neutral/decoy odour`

新版视频路径：

- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_left.mp4`
- `/unify/ydchen/unidit/bio_fly/paper/video/food_memory_cs_plus_right.mp4`

## 4. 论文编译环境

已通过 `apt-get` 安装本地 TeX 工具链，包括：

- `latexmk`
- `pdflatex`
- `texlive-latex-base`
- `texlive-latex-recommended`
- `texlive-latex-extra`
- `texlive-fonts-recommended`

编译命令：

```bash
cd /unify/ydchen/unidit/bio_fly/paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main_merged.tex
```

已生成：

- `/unify/ydchen/unidit/bio_fly/paper/main_merged.tex`
- `/unify/ydchen/unidit/bio_fly/paper/main_merged.pdf`
- `/unify/ydchen/unidit/bio_fly/paper/main_merged.log`

编译结果：`main_merged.pdf` 成功生成，大小约 `3.6M`，共 `38` 页。日志中没有未解析引用或未解析 citation。

## 5. 文章中已补充的关键解释

`/unify/ydchen/unidit/bio_fly/paper/main_merged.tex` 的 Methods 中已经明确写入：

- 仿真是测试阶段，不是训练阶段。
- CS+ 是 sugar-associated conditioned odour。
- CS- 是 neutral or competing odour。
- 没有实体食物是因为测试阶段看的是对“预测食物气味”的趋近。
- 新版补充视频已经在 overlay 中显式标注 CS+ 和 CS- 的含义。

## 6. 论文级表述建议

可以写：

> The assay models the test phase of an appetitive olfactory-memory paradigm. The CS+ is a sugar-associated odour cue rather than a consumable object rendered in the arena; the behavioural readout is whether the simulated fly approaches the odour predicting food.

不要写：

> The fly directly eats rendered food in the arena.

因为当前仿真没有建模进食动作、食物摄取或强化学习训练过程，而是建模学习后选择测试。
