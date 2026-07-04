# Écrivanalyse

Rebuilding a 20-year French archive (originally SPIP 3.2.8) as a modern,
type-forward personal showcase for the écrivanalyste **Ivan Joseph**. The corpus:
~3,000 **quintesses** (his word — 5 lines × 5 words, 25 words; **never call them "poèmes"**),
made in two modes: *séances de p(au)se* with pauseurs/pauseuses (strangers) and ongoing
*écrivanalyses* with a regular *analisant(e)*. Full lexicon is in DESIGN.md.

- Full public backup lives in `ecrivanalyse-backup/` (structured JSON in `data/`;
  crawl method documented in `ecrivanalyse-backup/PLAN.md`). Crawler: `scrape.py` (venv `.venv`).
- Content pipeline: `enrich.py` (backup -> `data/quintesses.json`), then
  `site/scripts/gen-content.py` (-> `site/src/content/quintes` + `textes`).
- `DESIGN.md` is the design system of record.
- Deploy: GitHub Pages via `.github/workflows/deploy.yml` on every push to main
  (BASE_PATH/SITE_URL env there until the custom domain is attached).

## Design System
Always read `DESIGN.md` before making any visual or UI decision. Fonts, colors,
spacing, motion, and the 5×5 system are defined there. Do not deviate without
explicit user approval. In QA, flag any code that doesn't match DESIGN.md.
