# GPT Image prompts for group-meeting schematic figures

保存路径：`/unify/ydchen/unidit/bio_fly/ppt/IMAGE_PROMPTS_FOR_GROUP_MEETING.md`

用途：下面的 prompt 用于生成组会汇报中可替换现有简单框图的高质量示意图。建议统一风格：Nature / Cell 风格科学插图、白色背景、清晰分区、少量高饱和强调色、无夸张 3D、无装饰性渐变、无虚构统计数字。图中文字可以留空或只放非常短的英文标签，最终标签在 PPT 里用 LaTeX 添加。

## Prompt 1: Project story overview

```text
Create a clean scientific schematic for a neuroscience group meeting slide.
Topic: from neurotransmitter lateralization in the adult Drosophila mushroom body to CyberFly-style connectome propagation and wet-lab validation.

Canvas: 16:9 landscape, white background, Nature-style multi-panel figure.
Visual structure:
Left panel: simplified adult fly brain with two mushroom bodies, left side tinted blue and right side tinted orange. Show Kenyon cell inputs entering both sides.
Middle panel: connectome propagation layer, represented as a sparse graph with highlighted seed nodes. Use orange nodes for right-serotonin-rich KC seeds and blue nodes for left-glutamate-rich KC seeds. Show arrows to memory-axis readouts: DAN, APL, DPM, MBON.
Right panel: validation outputs, split into two icons: DPM optogenetic stimulation with red light and OCT/MCH T-maze behavior assay.

Scientific message:
Right hemisphere KC input is serotonin-enriched.
Left hemisphere KC input is glutamate-biased.
The model propagates these side-specific seeds through the FlyWire connectome and prioritizes DPM optogenetic and OCT/MCH behavioral validation.

Style:
Use restrained colors: serotonin/right = warm orange-red; glutamate/left = blue-cyan; neutral circuits = gray.
Use clean vector-like shapes, thin black outlines, no cartoon exaggeration.
Do not include fake p-values or numbers.
Leave generous whitespace for LaTeX labels.
No decorative background, no glowing neural network, no futuristic cyberpunk style.
```

## Prompt 2: DPM optogenetic validation design

```text
Create a scientific experimental design schematic for DPM optogenetic validation in Drosophila.

Canvas: 16:9 landscape, white background.
Panels:
A. Adult fly brain with dorsal paired medial neuron (DPM) highlighted, projecting to mushroom body compartments. Use red light beam labeled conceptually as "red light stimulation" but keep labels minimal.
B. Two imaging orientations: normal orientation and 180-degree horizontal rotation. Show that analysis is registered to brain left/right, not camera left/right.
C. Readout panel showing two simplified traces: right-side 5-HT/KC readout higher than left-side readout after DPM activation. Do not put exact numeric values unless the chart axis is unlabeled.
D. Control panel icons: no-opsin, red-light-only, retinal-minus, and brain-side registration.

Scientific message:
If DPM-driven serotonin/KC readout is truly brain-side lateralized, the right-biased signal should remain right-biased after brain-side registration even when the fly is rotated 180 degrees. Camera artifacts should flip in image coordinates.

Style:
Nature Methods style, clean and technical.
Use red light sparingly; avoid dramatic glow.
Use orange for right-side 5-HT and blue/gray for left-side comparison.
Keep biological anatomy schematic, not photorealistic.
No claims of completed wet-lab validation; this is a validation design.
```

## Prompt 3: OCT/MCH behavioral assay scene

```text
Create a realistic but schematic top-down Drosophila olfactory behavior assay figure for a group meeting.

Canvas: 16:9 landscape, white background, multi-panel layout.
Main panel: top-down circular arena or T-maze-like chamber. Include a small fly silhouette with trajectory tail. On one side place an OCT odor cup; on the opposite side place an MCH odor cup. Show faint odor plumes, a sucrose reward droplet in reward conditions, and a subtle shock grid in punishment conditions.
Inset: a compact statistical panel with placeholder bars for choice index and approach margin, no exact numbers.
Side labels: CS+ side and CS- side, with mirror-side design indicated by a small left/right swap icon.

Scientific message:
OCT and MCH are counterbalanced odor identities. CS+ side is mirrored across trials to avoid spatial bias. The weak-OCT / strong-MCH conflict condition is used to detect subtle memory-related modulation.

Style:
Clean scientific illustration, restrained colors.
OCT = blue, MCH = amber/orange, reward = green, shock = dark gray.
Avoid cartoon food objects; use lab assay objects such as odor cups, filter paper, sucrose droplet and grid.
No fake labels like "significant" unless it is a placeholder.
```

## Prompt 4: Evidence chain and risk boundaries

```text
Create a concise evidence-chain schematic for a neuroscience manuscript or group meeting.

Canvas: 16:9 landscape, white background.
Show four horizontal blocks connected by arrows:
1. Structural discovery: FlyWire neurotransmitter-resolved KC inputs, right 5-HT enrichment, left Glu bias.
2. Functional propagation: sparse connectome propagation to memory-axis, DAN, APL, DPM, MBON/MBIN readouts.
3. Simulation prediction: DPM optogenetic release pattern and OCT/MCH behavioral choice prediction.
4. Wet-lab validation: GRASP/split-GFP, 5-HT sensor or GCaMP imaging, group T-maze behavior.

Below the chain, add a separate caution band with three icons:
"Not full Eon reproduction", "Not connectome-alone behavior emergence", "MB perturbation behavior not yet significant".
Use icons but minimal text. Leave room for final labels in PPT.

Style:
High-end academic schematic, clean vector art, no 3D, no decorative gradients.
Use blue/orange side colors consistently.
Make the caution band visually distinct but not alarming.
```

## Prompt 5: Mushroom-body lateralization mechanism

```text
Create a mechanistic schematic of left-right neurotransmitter lateralization in the Drosophila mushroom body.

Canvas: 16:9 landscape, white background.
Draw paired left and right mushroom bodies in simplified anatomical form.
Left side:
Highlight glutamate-biased upstream input to alpha-prime beta-prime Kenyon cells using blue arrows.
Right side:
Highlight serotonin-biased upstream input to alpha-prime beta-prime Kenyon cells using orange-red arrows.
Downstream:
Show both sides projecting to shared memory-related readouts: DAN, APL, DPM, MBON. Use thinner gray arrows for generic connections.

Scientific message:
The key finding is not that the two hemispheres have different sizes, but that the chemical composition of upstream input differs by side, strongest in alpha-prime beta-prime memory-consolidation-related KC compartments.

Style:
Publication-quality biological schematic.
Do not overcomplicate with all neuron names. Keep only KC, 5-HT input, Glu input, alpha-prime beta-prime lobe, memory readouts.
Use a clean white background and restrained colors.
```

## Recommended usage in the PPT

- Prompt 1 can replace the current TikZ flowchart slide.
- Prompt 2 can replace or supplement the DPM optogenetic protocol slide.
- Prompt 3 can replace the OCT/MCH video-frame-only slide when a cleaner conceptual assay figure is needed.
- Prompt 4 can be used as the final summary or risk-boundary slide.
- Prompt 5 can be used near the first result slide to make the biological mechanism more intuitive.

