# Design System — Écrivanalyse

> Read before any visual, UI, or copy decision. The lexicon is binding — these are
> Ivan Joseph's own words, confirmed against ecrivanalyse.net and fr.ulule.com/se-donner-a-sa-main.
> **Never call a quinte a "poème."**

## Lexicon (binding)
- **quinte** (n.f.) — **the text itself**, the short written piece you read. "Ce livre
  réunit de courts textes, les quintes." The *dispositif*: **cinq lignes, cinq mots par
  ligne, cinq signes de ponctuation** — but "de cette contrainte naît une liberté": the
  form is characteristic, **not a rigid cage**. Pluralizes normally: *les quintes*.
- **quintesse** (n.f.) — **the object**: the paper the quinte is written on, which the
  participant may acquire. "Le p(au)seur pourra choisir d'acquérir sa quintesse."
  Numbered per participant (*Quintesse XIX*), with a **status**: *achetée* (acquired),
  *autorisée à la vente*, *détruite*, *achevable*. Kept **invariant** (he never pluralizes it).
- **description** — each quinte carries a **one-line description** (the site's old
  `soustitre`). Surface it: title + description + the quinte.
- **écrivanalyse** (n.f.) — the practice: writing-analysis modeled on psychoanalysis, no
  therapeutic aim. **écrivanalyste** = the practitioner, **Ivan Joseph** (civil name Ivan Robin).
- **séance de p(au)se** (pun pause/pose) with a **p(au)seur / p(au)seuse** — the (often
  random, street) participant. In the data the label reads *Pauseur / Pauseuse*.
- **analisant / analisante** — the participant in an ongoing écrivanalyse (a **regular**
  person; his spelling, with an *i*). e.g. the écrivanalyse with **Annick Lebédyk**.
- **recueil / objet-livre** — a book collecting quintes, e.g. *« Se donner à sa main »*.
- **Le Point** — the studio, 43 rue Notre-Dame-de-Nazareth, Paris 3e. **ÉOK** — his imprint.

## Product Context
A 20-year archive of ~3,000 **quintes** by Ivan Joseph, made in two modes: **séances de
p(au)se** with p(au)seur·euses (strangers) and ongoing **écrivanalyses** with a regular
analisant·e. Each quinte was written on a **quintesse** (object) the participant could acquire.
Personal showcase. North star: **literary & intimate**.

## Form & layout — NO rigid grid
The 5/5/5 dispositif is the quinte's signature, but the design must not cage it:
- Render each quinte as **free verse lines** (serif, generous leading), whatever the count.
- **Do not** force a 5×5 cell grid (dropped). Five is a light rhythmic motif at most.
- Some quintes bend the form; the layout must hold them without breaking.

## Pages
- **Landing** — direction C: a random quinte *writes itself* (SVG handwriting), then stillness.
  Shows title, one-line description, the quinte. "rencontre au hasard" draws another.
- **Quinte page** (`/quinte/[id]`) — intimate reading: title, description, the quinte,
  then the **quintesse** it was written on (number + status + participant + mode + collection + date).
- **Archive** (`/archive`) — quintes by year, facets p(au)se vs écrivanalyse.
- **Le projet** — the manifesto + the quinte/quintesse distinction, using the project
  photos (quintesse-en-cours, Ivan, Annick, the clothesline) and the video. Assets in
  `site/public/media/` (video: YouTube short aGdme5n1ots).

## Typography (French-first: « » guillemets, œ ligature, accented capitals)
- **Quintes / display:** Fraunces (variable, ital). **Interface:** Instrument Sans.
  **Metadata:** JetBrains Mono. Self-hosted via Fontsource. (Never Inter / Space Grotesk.)

## Color — encre sur papier
Paper `#F6F1E7` / raised `#FBF8F1` / ink `#17130F` / muted `#6B635A` / hairline `#E2DACA` /
accent ocre-red `#B0472C` (rare). Dark: charcoal `#1E1A16`, ink `#EDE6D8`, accent `#CE7659`.

## Motion
Minimal, one flourish: the landing handwriting (`clip-path` line reveal, per-line delay set
by index so any line count works) + a drawn swash. Honor `prefers-reduced-motion`.

## Content model & storage (Astro + Keystatic)
Store **one Markdown file per quinte** (`src/content/quintes/[id].md`): the five lines in the
body; frontmatter = `title, description, lines, mode, participant_role, participant_name,
quintesse_num, status, collection, recueil, date, author, is_5x5`. Keystatic edits these
natively (Git-based, no DB). Astro loads them via a glob collection. Regenerable from
`ecrivanalyse-backup/data/quintesses.json` via `enrich.py` + a generator.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-02 | Direction C + A, tokens, fonts | /design-consultation. |
| 2026-07-02 | Lexicon v1; "poème" banned | Corpus read. |
| 2026-07-02 | Lexicon v2 (corrected) + no grid + Markdown-per-quinte | Ulule page: **quinte = the text**, **quintesse = the acquirable object**; dispositif 5/5/5 but "liberty" over rigidity, so the 5×5 grid is dropped; one-line description surfaced; content stored as Markdown files for Keystatic. |
| 2026-07-03 | Comments = **« réponses »**, JSON files in the repo, pre-moderated by a one-click email (`site/COMMENTS.md`) | 10 SPIP comments (2011–2018) imported; Ivan is non-technical, so publishing = one link in an email, ignoring = rejection. Never appears without him. |
| 2026-07-04 | Favicon = Fraunces italic **é** traced to a path (light/dark SVG); the old 5×5-grid favicon dropped | Grid motif was already banned; the é is type-forward, French, and survives 16 px. Feather/quill rejected: generic, wrong register. |
| 2026-07-04 | Per-quinte OG card (1200×630, quinte set in Fraunces on paper, `/og/[id].png`), full OG/Twitter/canonical/JSON-LD meta, sitemap, quiet « partager » (Web Share / copy) | Sharing happens by pasting a link; the unfurled card *is* the quinte. No social-button rows (trackers, off-brand). Default description fixed — it misused *quintesse* for the text. |
