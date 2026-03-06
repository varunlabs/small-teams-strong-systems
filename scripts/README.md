# Scripts

Organized utility scripts for this book project.

## Structure

- `cover/` — cover and KDP wrap generation
- `figures/` — figure generation, restyling, and image processing
- `review/` — manuscript QA and audit checks

## Common commands

```bash
python3 scripts/review/preflight_publish.py
python3 scripts/review/readability_review.py
python3 scripts/review/audit_figures.py
python3 scripts/review/final_review.py
python3 scripts/cover/generate_cover_assets.py
python3 scripts/cover/generate_kdp_wrap_cover.py
python3 scripts/figures/restyle_figure_images.py --list-styles
python3 scripts/figures/generate_figure_style_options.py
```
