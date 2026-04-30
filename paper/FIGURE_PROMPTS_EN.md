# Figure-generation prompts for the revised paper

Path: `/unify/ydchen/unidit/bio_fly/paper/FIGURE_PROMPTS_EN.md`

This document is written for GPT Image 2. The goal is to replace rough schematic boxes with publication-quality figures that match the manuscript story:

1. structural transmitter lateralization in KC inputs,
2. CyberFly-style connectome propagation,
3. DPM optogenetic validation,
4. OCT/MCH behavioural assay scenes.

## Global style instructions

Use these instructions for every figure unless a prompt explicitly overrides them.

- Make the image look like a Nature/Cell-style scientific figure, not like a presentation slide.
- White background, restrained palette, no decorative gradients, no glowing blobs, no unnecessary shadows.
- Prefer crisp vector-like shapes, thin lines, clean labels, and evenly spaced panels.
- Use a 2x2 or 1x4 layout when multiple panels are needed.
- Use clear panel labels A, B, C, D in the upper-left corner of each panel.
- Keep text minimal and legible. If a label will become tiny, move it into the caption instead of putting it inside the image.
- Use the same color mapping across all figures:
  - left side: blue,
  - right side: red,
  - neutral or baseline: gray,
  - serotonin / 5-HT: warm orange-red,
  - glutamate / Glu: teal-blue or cool blue-green,
  - DPM / memory consolidation: muted purple or warm gold, but not saturated neon.
- Avoid cartoonish animals. If a fly is shown, make it anatomically believable and small relative to the assay scene.
- Avoid crowded topology diagrams with many crossing edges.
- Each figure should tell one story only. Do not combine unrelated subplots.
- If the figure includes bars or heat maps, make the values and axis labels large enough to read in a printed manuscript.

## Prompt 1: Study logic and CyberFly bridge

Use this to regenerate the current overview figure with a cleaner, more editorial look.

**Prompt**

Create a clean scientific multi-panel figure for a Nature-style manuscript about adult fly mushroom-body lateralization. The figure should be a 2x2 panel infographic on a white background. The subject is the adult Drosophila mushroom body, connectome-constrained propagation, DPM validation, and OCT/MCH behavioural testing.

Panel A: a high-level workflow starting from FlyWire v783, then selecting transmitter-defined KC seed ensembles, then sparse GPU propagation through the connectome, then downstream readouts in memory-axis / MBON / DAN / APL / DPM, then wet-lab validation. Use a simple left-to-right flow diagram with 4 or 5 boxes only. Add a small stylized fly brain silhouette, but keep it simple and scientifically clean.

Panel B: a compact structural result summary showing right-serotonin enrichment and left-glutamate bias across KC types, with the strongest effects in the alpha-prime beta-prime lobe. Use a horizontal diverging bar plot or compact heatmap. Right side should be red/orange, left side should be blue. Make the largest effect in the alpha-prime beta-prime row visually dominant.

Panel C: a functional bridge schematic showing transmitter-selected KC seeds propagating into memory-axis, DAN, APL, DPM, and MBON/MBIN readouts, contrasted with matched random KC controls. Use a clean arrow-based diagram, not a network spaghetti drawing. Add a small inset bar chart for effect size.

Panel D: a validation ladder showing three evidence levels: structural proof, functional imaging proof, and group behaviour proof. Indicate GRASP or split-GFP, DPM optogenetic imaging with 180-degree rotation control, and OCT/MCH group T-maze testing. Make it look like a rigorous experimental decision tree.

Overall style: scientific publication figure, crisp typography, balanced spacing, no decorative backgrounds, no 3D rendering, no comic style, no exaggerated colors, no crowded text. Use the figure to communicate the story from structure to function to validation.

**Negative prompt**

No glitter, no gradients, no neon colors, no stock-photo fly, no excessive tiny labels, no clutter, no repeated arrows, no topology network explosion, no blurry text.

## Prompt 2: Structural transmitter lateralization in KCs

Use this to replace the current structural result figure with a polished figure that focuses only on the biological discovery.

**Prompt**

Create a publication-quality biology figure for a Nature-style paper about transmitter lateralization in the adult fly mushroom body. The figure must focus only on the structural discovery that Kenyon-cell inputs are chemically lateralized.

Layout: 1 large panel plus 2 smaller panels, or a 1x3 arrangement. White background, clean axes, minimal text.

Main panel: a diverging heatmap of Cohen's d values across KC types and neurotransmitters. The rows should correspond to KC subtypes, grouped by lobe system. The columns should include serotonin, glutamate, dopamine, GABA, octopamine, and acetylcholine. Right-biased values should be in warm red/orange, left-biased values in blue. The strongest positive serotonin values should appear in the alpha-prime beta-prime rows, and the strongest negative glutamate values should appear in the same rows. Make the heatmap readable and publication-ready.

Secondary panel 1: a simple schematic of the mushroom body lobes showing alpha-prime beta-prime, alpha beta, and gamma. Highlight the alpha-prime beta-prime lobe as the strongest memory-consolidation-related region. Show left and right hemispheres, but keep the cartoon simple and anatomical.

Secondary panel 2: a small bar chart or dot plot of lobe-level laterality indices, emphasizing that serotonin is right-enriched and glutamate is left-biased, with weaker or mixed effects for the other transmitters. Include a clean legend.

Style instructions: use crisp scientific illustration aesthetics, clear labels, restrained colors, no shadowed boxes, no playful icons, no overlapping labels, no excessive arrows. The figure should look like a serious primary-data panel in Nature.

**Negative prompt**

No topology diagrams, no graph neural network charts, no dense mesh of neuron edges, no cartoon fruit, no decorative blobs, no illegible labels, no rainbow palette.

## Prompt 3: Functional bridge from structure to memory-circuit targets

Use this to regenerate the functional propagation / target prioritization figure.

**Prompt**

Create a Nature-style scientific figure showing how transmitter-lateralized KC ensembles propagate into memory-circuit readouts. The figure should communicate that right-serotonin and left-glutamate KC seeds are not equivalent to matched random KC controls.

Panel A: an absolute-effect comparison across readout classes, including memory-axis, DAN, APL, DPM, MBON, MBIN, and response laterality. Show two conditions: right-serotonin KC seed set and left-glutamate KC seed set. Use a compact heatmap or grouped bar chart with clear significance annotations. Make the left-glutamate condition visibly broader than the right-serotonin condition.

Panel B: a clean connectome bridge schematic with three layers only: transmitter-defined KC seeds, memory-axis / feedback readouts, and downstream target families. Use arrows, but keep the diagram sparse and elegant.

Panel C: a target-priority ranking panel showing the top candidate experimental targets, such as DPM, APL, MBON, and DAN families. Use a ranked horizontal bar chart or lollipop plot. Highlight that the purpose is wet-lab prioritization, not a claim of complete causal proof.

Panel D: a small inset comparing the selected seed ensembles against matched random KC controls. Show that the random controls have lower or different propagation signatures.

Style: highly readable, publication ready, minimal clutter, white background, red for right-biased readouts, blue for left-biased readouts, gray for controls. No topology-heavy network diagram. This figure should feel like a mechanistic bridge, not a software workflow slide.

**Negative prompt**

No dense node-link graphs, no tiny annotations inside every bar, no cartoon neurons, no multicolor clutter, no noisy background, no presentation slide style.

## Prompt 4: DPM optogenetic and OCT/MCH validation path

Use this to replace the current validation figure with a cleaner experimental story.

**Prompt**

Create a Nature-style multi-panel figure about DPM optogenetic validation and OCT/MCH behavioural testing in adult flies. The figure should explain the experimental logic, the protocol scan, the rotation control, and the behavioural prediction.

Panel A: a protocol scan plot for CsChrimson and ReaChR, showing wavelength versus predicted effect or priority score. Use a clear line plot or heatmap. Highlight the best protocols around 617 to 627 nm, 40 Hz, 20 ms pulses, and 5 s stimulation duration. Make red-shifted protocols visually preferred and blue-light protocols visually secondary.

Panel B: a rotation-control schematic showing a fly or fly brain being rotated by 180 degrees. The key message is that true brain-side lateralization should keep the sign after brain-side registration, while camera-coordinate artifacts would flip. Make the control visually obvious and clean.

Panel C: a group-level behavioural prediction plot for OCT/MCH. Show the weak-OCT/strong-MCH conflict assay as the most sensitive condition. Use a bar chart or line plot with choice index or approach margin. The best protocol should produce an approximately +0.104 choice-index shift in the conflict condition. Keep the message clear that this is a prediction, not a measured wet-lab result.

Panel D: a realistic assay-frame illustration of the OCT/MCH setup. Show an arena or T-maze with visible odor sources, a tracked fly path, trail traces, and a small inset summary statistic. The scene should feel like a real experimental photograph or polished scientific reconstruction, not a schematic. Include OCT and MCH labels, CS+ and CS- positions, and a subtle scale bar.

Style: serious experimental biology figure. White or light background. Clean labels. Avoid clutter. Make the assay scene look like an actual experimental setup with realistic objects, not a blue-yellow placeholder.

**Negative prompt**

No abstract wireframe boxes, no toy icons, no neon colors, no fake 3D rendering, no unreadable tiny text, no dense background, no whimsical style.

## Prompt 5: DPM optogenetic release video frame

Use this to create a still image for the DPM release video or as a supplementary figure thumbnail.

**Prompt**

Create a polished scientific video frame for a supplementary movie about DPM optogenetic activation and 5-HT release prediction in the adult fly brain. The frame should show a stylized but anatomically credible fly brain with left and right hemispheres, a highlighted DPM region, a 5-HT release trace or heat map, and a brain-registered laterality index inset. Include a small arrow indicating red-light stimulation with CsChrimson or ReaChR.

The frame should look like a high-quality supplementary figure from a Nature paper: clean, informative, and balanced. Use a limited palette, with serotonin in warm orange-red and the two hemispheres coded consistently as blue and red. The key visual message is that the release pattern is right-biased after brain-side registration and that rotation control matters.

Do not make it look like a raw screenshot from analysis software. It should look polished enough to sit next to a main-figure panel.

**Negative prompt**

No dirty UI, no giant labels, no cartoon fly, no excess arrows, no crowded heatmap legends, no background noise.

## Prompt 6: OCT/MCH assay scene video frame

Use this to replace the current assay frame with a more realistic behavioural scene.

**Prompt**

Create a realistic scientific video frame for an OCT/MCH memory assay in adult flies. Show a clear behavioural arena or T-maze with visible odor sources for OCT and MCH, a tracked fly or small group of flies, trajectory traces, and an inset showing the formal statistics for the condition. The image should communicate that this is a real behavioural experiment, not a symbolic diagram.

The environment should include experimental objects that a biologist would recognize: arena floor, odor ports or odor cups, a scale bar, and a clean legend indicating CS+ and CS-. If the condition is a weak-OCT/strong-MCH conflict assay, make that explicit in the inset or caption area. The fly track should visibly curve toward one odor under the predicted condition.

Style: clean, realistic, publication-quality, lightly stylized but not cartoonish. No extra decorative objects. The main visual should be the assay geometry and the fly trajectory, with statistics inset placed neatly in one corner.

**Negative prompt**

No abstract blobs, no placeholder blue/yellow blocks, no overdone glow, no text that is too small to read, no scientific illustration that feels like a toy.

## Suggested insertion workflow

1. Generate one image per prompt.
2. Replace the corresponding figure placeholder in `/unify/ydchen/unidit/bio_fly/paper/main_merged0601.tex`.
3. Recompile the manuscript.
4. If a generated figure is too busy, simplify it before reusing it.

## Recommended output files to replace later

- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig0_story_and_validation0429.pdf`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig3_hemisphere_asymmetry.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig7_lobe_memory_schematic.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig2_functional_metric_heatmap.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_structure_behavior_linkage.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_memory_axis_target_priorities.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_dpm_optogenetic_protocol_predictions.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_dpm_wetlab_validation_design.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_group_behavior_observable_predictions.png`
- `/unify/ydchen/unidit/bio_fly/paper/figures/Fig_oct_mch_assay_v2_key_conditions_frame.png`
