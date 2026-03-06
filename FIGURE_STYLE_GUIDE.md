# Figure Style Options and Regeneration

This project now supports selectable figure style presets for all generated PNGs.

## Available styles

- `executive_navy` — default balanced look for strategy/technical business content
- `blueprint` — cooler, sharper, more technical visual tone
- `warm_editorial` — warmer, softer editorial look
- `mono_print` — high-contrast grayscale-friendly print-safe look

## Preview samples

Preview output is generated in:

- `output/figure_style_options/contact_sheet_executive_navy.png`
- `output/figure_style_options/contact_sheet_blueprint.png`
- `output/figure_style_options/contact_sheet_warm_editorial.png`
- `output/figure_style_options/contact_sheet_mono_print.png`

Also includes per-style rendered examples under:

- `output/figure_style_options/<style_name>/...`

## Regenerate all figures with chosen style

Use the original backups as source for clean rerender:

```bash
/Users/varunsiddaraju/Documents/GitHub/Book/.venv/bin/python scripts/figures/restyle_figure_images.py --source generated_original --style executive_navy
```

Replace `executive_navy` with your selected style.

## Commands

List styles:

```bash
/Users/varunsiddaraju/Documents/GitHub/Book/.venv/bin/python scripts/figures/restyle_figure_images.py --list-styles
```

Generate style previews again:

```bash
/Users/varunsiddaraju/Documents/GitHub/Book/.venv/bin/python scripts/figures/generate_figure_style_options.py
```

Generate previews for a subset:

```bash
/Users/varunsiddaraju/Documents/GitHub/Book/.venv/bin/python scripts/figures/generate_figure_style_options.py --styles executive_navy mono_print
```
