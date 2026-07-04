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
  Numbered per participant (*Quintesse XIX*), with a **status phrase** kept verbatim —
  the vocabulary is open and playful: *achetée par l'analisante*, *autorisée à la vente*,
  *détruite pour…*, *suspendue*, *troquée*, *inachevée*, *réservée*, *offerte*, up to
  hapaxes like *anniverchetée* or *achetée-confiturée*. Never normalize it to a closed
  list. Kept **invariant** (he never pluralizes it).
- **description** — each quinte carries a **one-line description** (the site's old
  `soustitre`). Surface it: title + description + the quinte.
- **écrivanalyse** (n.f.) — the practice: writing-analysis modeled on psychoanalysis, no
  therapeutic aim. **écrivanalyste** = the practitioner, **Ivan Joseph** (civil name Ivan Robin).
- **séance de p(au)se** (pun pause/pose) with a **p(au)seur / p(au)seuse** — the (often
  random, street) participant. The original pages label them *P(au)seur / P(au)seuse*
  (plain *Pauseuse* only in the earliest ~2010 P.-S. blocks); the data key is normalized
  to `pauseur`/`pauseuse` but the **displayed label uses his parenthesized form**.
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
- **Landing** — direction C2 « le mur, puis l'encre » : the whole corpus inks in as a wall
  of titles (with a live count of the quintes), the camera dives into one title, and that
  quinte *writes itself* word by word — reveal led by a nib, a breath at each punctuation
  sign, ink drying — then stillness (the chrome fades until the visitor moves).
  "rencontre au hasard" pulls back to the wall and dives into another. Return visits get a
  shorter wall beat (localStorage); `prefers-reduced-motion` gets a full static composition.
- **Quinte page** (`/quinte/[id]`) — intimate reading: title, description, the quinte,
  then the **quintesse** it was written on (number + status + participant + mode + collection + date).
- **Archive** (`/archive`) — quintes by year, facets p(au)se vs écrivanalyse.
- **Le projet** — the manifesto + the quinte/quintesse distinction, using the project
  photos (quintesse-en-cours, Ivan, Annick, the clothesline) and the video. Assets in
  `site/public/media/` (video: YouTube short aGdme5n1ots).

## Typography (French-first: « » guillemets, œ ligature, accented capitals)
- **Quintes / display:** Spectral (Production Type, Paris — OFL; static weights 300/400/500
  + true italics 300/400; never synthesize italics). **Interface:** Instrument Sans.
  **Metadata:** JetBrains Mono. Self-hosted via Fontsource. (Never Inter / Space Grotesk.)
- Font assets (OG-card TTFs + the traced favicon é) regenerate via `site/scripts/gen-fonts.py`.

## Color — encre sur papier
Paper `#F6F1E7` / raised `#FBF8F1` / ink `#17130F` / muted `#6B635A` / hairline `#E2DACA` /
accent ocre-red `#B0472C` (rare). Dark: charcoal `#1E1A16`, ink `#EDE6D8`, accent `#CE7659`.

## Motion
One signature choreography, then stillness. The choreography is mass↔one (the wall of every
title ↔ a single quinte) plus the writing itself (per-word reveal led by a nib, pauses at
punctuation, ink drying). Rules: animate transform/opacity/clip-path only; custom easing
(never default ease-in-out); every animation is skippable by the input that would follow it;
exits are designed, not just entrances; zero autonomous motion once the writing ends.
Honor `prefers-reduced-motion` with a complete static composition.

## Content model & storage (Astro + Keystatic)
Store **one Markdown file per quinte** (`src/content/quintes/[id].md`): the five lines in the
body; frontmatter = `title, description, lines, mode, participant_role, participant_name,
quintesse_num, status, collection, recueil, date, author, is_5x5`. `status` holds the
**full original phrase** ("achetée par l'analisante", "suspendue pour la p(au)seuse"),
free text — not an enum. Keystatic edits these natively (Git-based, no DB). Astro loads
them via a glob collection. Regenerable from
`ecrivanalyse-backup/data/quintesses.json` via `enrich.py` + a generator.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-04 | Dive sharpness: the GPU zooms a raster made at scale 1, so the wall went pixelated as it grew. Now the **real title** (full-resolution raster, scaled down then animated to identity — only ever minified) flies from the wall title's place to its exact landing seat; the wall fades earlier (gone ~72 %) and the zoom tops at 6×; the stage reveals by opacity alone so the flying title lands seamlessly. Rhythm: line-break breath 0.12 → 0.22 s (a line break ≥ a comma); first-visit dive at 2.15 s. | Raster big, animate small→identity — downscaling stays sharp at every frame. The blurred mass receding behind one crisp voice is also the right metaphor. |
| 2026-07-04 | **Spectral remplace Fraunces** partout (site, cartes OG, favicon é retracé) — poids 300 (grande quinte), 400 (lecture), 500 ; italiques vraies 300/400. Les axes WONK/SOFT disparaissent avec Fraunces. `/specimen` (comparatif Fraunces / Spectral / Cormorant / EB Garamond sur texte réel) a servi la décision puis a été supprimé. | Choix de Romain sur spécimen : plus littéraire et plus calme que Fraunces (qui datait les sites 2021-2025), Production Type **Paris** — la provenance française a du sens pour ce corpus. Libre (SIL OFL). Cormorant éliminée (trop fine au corps du mur), EB Garamond trop sage. |
| 2026-07-02 | Direction C + A, tokens, fonts | /design-consultation. |
| 2026-07-02 | Lexicon v1; "poème" banned | Corpus read. |
| 2026-07-02 | Lexicon v2 (corrected) + no grid + Markdown-per-quinte | Ulule page: **quinte = the text**, **quintesse = the acquirable object**; dispositif 5/5/5 but "liberty" over rigidity, so the 5×5 grid is dropped; one-line description surfaced; content stored as Markdown files for Keystatic. |
| 2026-07-03 | Comments = **« réponses »**, JSON files in the repo, pre-moderated by a one-click email (`site/COMMENTS.md`) | 10 SPIP comments (2011–2018) imported; Ivan is non-technical, so publishing = one link in an email, ignoring = rejection. Never appears without him. |
| 2026-07-04 | Favicon = Fraunces italic **é** traced to a path (light/dark SVG); the old 5×5-grid favicon dropped | Grid motif was already banned; the é is type-forward, French, and survives 16 px. Feather/quill rejected: generic, wrong register. |
| 2026-07-04 | Per-quinte OG card (1200×630, quinte set in Fraunces on paper, `/og/[id].png`), full OG/Twitter/canonical/JSON-LD meta, sitemap, quiet « partager » (Web Share / copy) | Sharing happens by pasting a link; the unfurled card *is* the quinte. No social-button rows (trackers, off-brand). Default description fixed — it misused *quintesse* for the text. |
| 2026-07-04 | Landing C2 « le mur, puis l'encre » + motion doctrine rewritten | AWWWards push (user delegated the call): wall of every title → dive → per-word nib writing → stillness. The drawn swash flourish is retired; motion = one choreography, skippable, designed exits, nothing moves after the writing ends. |
| 2026-07-04 | Participant + quintesse status recovered corpus-wide; `status` = full verbatim phrase (free text, no enum); role label displayed as **P(au)seur/P(au)seuse** | The old parser missed the *P(au)seuse* spelling and the ~2010 P.-S. block: 697 roles, 744 statuses, 2 quintes (186, 219) were silently absent (e.g. 2564 lost "P(au)seuse : anonyme / Quintesse suspendue pour la p(au)seuse"). The status vocabulary is open (*anniverchetée*, *achetée-confiturée*) — a closed select falsifies it. |
| 2026-07-04 | Mobile pass: the wall bleeds 9vw past both screen edges (titles cut mid-word, clipped — no x-scroll); archive gets a sticky year rail + `content-visibility` (the page holds 3 000 rows); swipe / ←→ leaf between quintes; finger-sized tap targets via padding+negative-margin | The ragged right margin made the wall look composed *for* the screen; bleeding it makes the mass feel like it continues beyond. Archive lede now says "archivées de 2009 à 2026" (the practice is *depuis 2006*, the dated holdings start 2009). |
| 2026-07-04 | **True Fraunces italic imported** (`wght-italic.css` + preload) — every italic had been a synthesized slant. Wall bleed fixed to exceed the widest title (`clamp(-280px,-17vw,-170px)`): smaller bleeds leave lines ending short of the edge because an unfitting title wraps whole. | AWWWards pass, part 1: typographic truth first. |
| 2026-07-04 | Search results re-set in the archive's language: default PagefindUI dropped for a custom renderer on the Pagefind JS API — whole row clickable, serif title (qtitle morph), italic excerpt with ocre-washed `<mark>`, mono `year · numéro` column (`data-pagefind-meta="r:…"`), French count/zero states ("rien pour « x » — tenter une rencontre au hasard ↻"), `?q=` deep links, « voir plus » pagination. Breadcrumb is `data-pagefind-ignore`d and quinte lines emit a separator space, so excerpts stopped reading "« Séances… » · séance de p(au)se" and "bleue,à". | A search hit is an archive entry that happens to match — it must look like one. |
| 2026-07-04 | One transition language site-wide: a clicked title (wall, archive, collection) is named `qtitle` just-in-time and **travels** to the destination page's h1; browser Back reverses it. Direct arrivals (shared links) get a per-line ink-in entrance instead — never both. Also: designed 404 in the quintesse status vocabulary ("dérobée… troquée, suspendue, détruite pour de bon"), print stylesheet (a printed quinte page = a museum label: text + colophon), « qu'est-ce qu'une quintesse ? » footnote → `/projet#quintesse`, ☾/☀︎ theme glyph names the destination, 3px hover nudge on list entries, hover-prefetch, skip link + ocre `:focus-visible` everywhere. | Mass↔one is the site's only motion metaphor — page transitions must speak it too, not stack a second vocabulary (no slides, no custom cursors). Entrance and morph are mutually exclusive so nothing animates twice. |
