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
- **Landing** — « le mur, puis l'encre » : the whole corpus inks in as a wall
  of titles (with a live count of the quintes), the camera dives into one title, and that
  quinte *writes itself* word by word — reveal led by a nib, a breath at each punctuation
  sign, ink drying — then stillness (the chrome fades until the visitor moves).
  "rencontre au hasard" pulls back to the wall, marks a beat (the chosen title lights up
  in ocre and grows slightly while the mass recedes behind a translucent paper veil,
  ~560 ms), then dives into it. Return visits get a shorter wall beat (localStorage);
  `prefers-reduced-motion` gets a full static composition. The most recent quinte is
  always in the dive sample, seated in the galley's first rows (the only zone visible
  on every viewport): the first visit, and every visit where a quinte was published
  since the last one, lands on it (localStorage `ea-latest`), then the hasard resumes.
- **Quinte page** (`/quinte/[id]`) — intimate reading: title, description, the quinte,
  then the **quintesse** it was written on (number + status + participant + mode + collection + date).
  Two variants: **hybrid** (the original page set prose around the quinte, e.g. 154
  "La maison dans la maison": the quinte sits inside the prose at reading size and
  weight, where the original placed it - a `<quinte>` marker in the `prose` field,
  default position the end; the fitted display treatment stays for standalone
  quintes) and
  **ghost** (39 séance records from 2010 whose quinte was never put online, the
  quintesse bought or print-only: the page states "La quinte n'a pas été mise en
  ligne : elle se lit dans le recueil « Faire une quinte de tout »" in place of the
  quinte; excluded from /hasard and the landing wall).
- **Texte page** (`/texte/[id]`) — the non-quinte œuvre (97: prose of "La petite fille
  à côté" co-signed Annick Lebédyk, "La danseuse de vélo", the serialized "Fluides ou
  Le singulier pluriel" chapters). Reading layout (Spectral 400, 680px measure),
  paragraphs with light <i>/<b>, réponses + form like a quinte, prev/next within the
  série. Listed in /archive (facet "textes"), collections, and search.
- **Archive** (`/archive`) — quintes by year, facets p(au)se vs écrivanalyse.
- **Le projet** — the manifesto + the quinte/quintesse distinction, using the project
  photos (quintesse-en-cours, Ivan, Annick, the clothesline) and the video. Assets in
  `site/public/media/` (video: YouTube short aGdme5n1ots).

## Typography (French-first: « » guillemets, œ ligature, accented capitals)
- **Quintes / display:** Spectral (Production Type, Paris — OFL; static weights 300/400/500
  + true italics 300/400; never synthesize italics). **Interface:** Instrument Sans.
  **Metadata:** JetBrains Mono. Self-hosted via Fontsource. (Never Inter / Space Grotesk.)
- Font assets (OG-card TTFs + the traced favicon é) regenerate via `site/scripts/gen-fonts.py`.
- **No em dashes in UI copy**: use a plain hyphen "-". Em dashes appear only inside
  corpus content quoted verbatim from the backup.

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

## Content model & storage (Astro)
Store **one YAML file per quinte** (`src/content/quintes/<id>.yaml`) with
`title, soustitre, lines, mode, participant_role, participant_name,
quintesse_num, status, collection, recueil, date, author, is_5x5`. `status` holds the
**full original phrase** ("achetée par l'analisante", "suspendue pour la p(au)seuse"),
free text — not an enum. The YAML files are edited directly (no CMS; Keystatic was
removed 2026-07-04). Astro loads
them via a glob collection. A second collection `src/content/textes/` holds the
non-quinte œuvre (`text` = paragraphs \n\n, breaks \n, light <i>/<b>). Both regenerate
from the backup via `enrich.py` + `site/scripts/gen-content.py`; quintes may carry
`prose` (hybrid pages) and ghosts keep `lines: []`.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-04 | **Collections triées par vie** (entrée la plus récente d'abord, plage d'années affichée). **« Revenir en haut »** discret sur les pages longues (apparaît après ~1,5 écran, cercle mono en bas à droite). **Barre de navigation non fixée** - la chrome recède, le rail des années de l'archive garde le haut de l'écran ; à la place, un **pied de page discret** (documentaires + hasard) sur toutes les pages sauf la landing. Journal des décisions resserré. | Le tri par volume enterrait les séries vivantes sous les années de séances de 2010 ; le retour en haut couvre le besoin qu'une barre fixe aurait servi, sans coût vertical permanent. |
| 2026-07-04 | **Pages documentaires** : `/ecrivanalyse` (la pratique en cinq chapitres par Perrine Tamerlis, articles 129-134) et `/editions` (intro ÉOK 14, livres Omar Kaczmar 123-125, côté Œuvres Komplètes 127 et 797 « Faire une quinte de tout »), extraites vers `src/data/legacy-pages.json`, liées depuis /projet ; les pages fantômes lient le recueil ; la 404 redirige leurs anciens ids. Le contact (118, 136) reste écarté. | 797 est la présentation du recueil que citent les 39 fantômes ; 129-134 est la présentation de la pratique écrite par Perrine Tamerlis pour le site d'origine, à côté de la voix éditoriale de /projet. |
| 2026-07-04 | **Mémoire des anciennes adresses** : la 404 redirige les URL SPIP (`articleN` -> quinte ou texte, mêmes ids ; `rubriqueN` -> collection ; `auteurN` -> /projet ; `page=plan`, `page=recherche` avec sa requête ; `id_article=N` des forums). **Photographie de 190** restaurée (`image`/`image_caption` ; seule page illustrée du corpus, vignette seule rescapée). **Cartes OG des textes**. **Recherche** : filtre quintes/textes. **Archive** : le rail des années suit le défilement. | Vingt ans de liens et de résultats de recherche pointent vers les adresses SPIP ; une archive ne casse pas ses liens. La carte des rubriques vient des fils d'Ariane des articles, `rubriques.json` étant une autre taxonomie. |
| 2026-07-04 | **La quinte d'une page hybride se lit dans la prose** : même corps, même graisse, à l'endroit exact où l'original la plaçait (marqueur `<quinte>` dans `prose`, position par défaut : la fin). Le traitement ajusté à la largeur reste réservé aux quintes seules. Markdown/MDX évalué et écarté : `lines` doit rester une donnée structurée (écriture mot à mot de la landing, cartes OG, recherche, fit) ; le marqueur donne la souplesse de position sans changer de format. | Sur la page d'origine de 154, la quinte achève la dernière phrase de la prose dans le même corps ; la grossir la sortait du récit. La prose sans quinte existe déjà : ce sont les textes. |
| 2026-07-04 | **Le temps de la rencontre** : entre le recul vers le mur et la plongée, un battement (~560 ms) où la quinte choisie s'allume (ocre, scale 1.3) pendant qu'un voile de papier (un élément, opacité seule) fait reculer la masse. **La quinte la plus récente** siège dans les premières lignes du mur ; la première visite, et chaque retour où du nouveau est paru, atterrissent dessus (localStorage `ea-latest`), puis le hasard reprend. | La sélection n'était pas lisible : le `.lit` s'appliquait dans la même frame que le départ de la caméra. Le battement rend le choix visible et porte la métaphore (une voix sort de la masse) ; la nouveauté sert les visiteurs fidèles sans figer le hasard. |
| 2026-07-04 | **Hébergement GitHub Pages** (repo public Ngopimas/ecrivanalyse, build via Actions : astro + pagefind, deploy-pages). **Keystatic retiré** (config, React et contournements Vite compris) : les YAML s'éditent à la main ou se régénèrent par gen-content.py ; pour Ivan, flux « e-mail + lien Publier » à construire sur le modèle des réponses. Restant : les deux endpoints réponses (functions/api) sont du code Cloudflare Pages Functions, à héberger en Worker avant mise en ligne publique ; le domaine reste à pointer. | GitHub Pages plutôt que Cloudflare Pages, qui plafonne à 20 000 fichiers par déploiement (19 173 au moment du choix). Keystatic ne servait qu'en local et dupliquait le schéma une troisième fois. |
| 2026-07-04 | **Taxonomie du corpus complet** (3 157 articles) : 3 047 quintes (dont 1 hybride avec prose, 154 ; 39 « fantômes » de 2010 sans texte en ligne, quintesse achetée, recueil « Faire une quinte de tout » ; 1024 en six lignes, produit de séance quand même) + 97 textes (nouvelle collection : « La petite fille à côté », « La danseuse de vélo », « Fluides ou Le singulier pluriel »…) + 13 pages de plomberie SPIP écartées (couvertes par /projet). 42 quintes récupérées en corrigeant le compteur de mots d'enrich.py (tirets d'incise comptés comme mots, œ hors de À-ÿ, sigles « O.R.L. », `<br style>` non splitté, tableau-photo de 190). Un texte n'est jamais présenté comme une quinte, et inversement. | Sur le site d'origine, une partie de l'œuvre n'était pas des quintes (prose, feuilletons, pièces dialoguées) ; l'extraction les écrasait au format quinte ou les perdait. is_5x5 reste le drapeau strict ; le dispositif est « caractéristique, pas une cage ». |
| 2026-07-04 | Dive sharpness: the GPU zooms a raster made at scale 1, so the wall went pixelated as it grew. Now the **real title** (full-resolution raster, scaled down then animated to identity — only ever minified) flies from the wall title's place to its exact landing seat; the wall fades earlier (gone ~72 %) and the zoom tops at 6×; the stage reveals by opacity alone so the flying title lands seamlessly. Rhythm: line-break breath 0.12 → 0.22 s (a line break ≥ a comma); first-visit dive at 2.15 s. | Raster big, animate small→identity — downscaling stays sharp at every frame. The blurred mass receding behind one crisp voice is also the right metaphor. |
| 2026-07-04 | **Spectral remplace Fraunces** partout (site, cartes OG, favicon é retracé) — poids 300 (grande quinte), 400 (lecture), 500 ; italiques vraies 300/400. Les axes WONK/SOFT disparaissent avec Fraunces. `/specimen` (comparatif Fraunces / Spectral / Cormorant / EB Garamond sur texte réel) a servi la décision puis a été supprimé. | Décision sur spécimen : plus littéraire et plus calme que Fraunces (qui datait les sites 2021-2025), Production Type **Paris** — la provenance française a du sens pour ce corpus. Libre (SIL OFL). Cormorant éliminée (trop fine au corps du mur), EB Garamond trop sage. |
| 2026-07-02 | Direction C + A, tokens, fonts | /design-consultation. |
| 2026-07-02 | Lexicon v1; "poème" banned | Corpus read. |
| 2026-07-02 | Lexicon v2 (corrected) + no grid + Markdown-per-quinte | Ulule page: **quinte = the text**, **quintesse = the acquirable object**; dispositif 5/5/5 but "liberty" over rigidity, so the 5×5 grid is dropped; one-line description surfaced; content stored as Markdown files for Keystatic. |
| 2026-07-03 | Comments = **« réponses »**, JSON files in the repo, pre-moderated by a one-click email (`site/COMMENTS.md`) | 10 SPIP comments (2011–2018) imported; Ivan is non-technical, so publishing = one link in an email, ignoring = rejection. Never appears without him. |
| 2026-07-04 | Favicon = Fraunces italic **é** traced to a path (light/dark SVG); the old 5×5-grid favicon dropped | Grid motif was already banned; the é is type-forward, French, and survives 16 px. Feather/quill rejected: generic, wrong register. |
| 2026-07-04 | Per-quinte OG card (1200×630, quinte set in Fraunces on paper, `/og/[id].png`), full OG/Twitter/canonical/JSON-LD meta, sitemap, quiet « partager » (Web Share / copy) | Sharing happens by pasting a link; the unfurled card *is* the quinte. No social-button rows (trackers, off-brand). Default description fixed — it misused *quintesse* for the text. |
| 2026-07-04 | Landing C2 « le mur, puis l'encre » + motion doctrine rewritten | Ambition AWWWards : wall of every title → dive → per-word nib writing → stillness. The drawn swash flourish is retired; motion = one choreography, skippable, designed exits, nothing moves after the writing ends. |
| 2026-07-04 | Participant + quintesse status recovered corpus-wide; `status` = full verbatim phrase (free text, no enum); role label displayed as **P(au)seur/P(au)seuse** | The old parser missed the *P(au)seuse* spelling and the ~2010 P.-S. block: 697 roles, 744 statuses, 2 quintes (186, 219) were silently absent (e.g. 2564 lost "P(au)seuse : anonyme / Quintesse suspendue pour la p(au)seuse"). The status vocabulary is open (*anniverchetée*, *achetée-confiturée*) — a closed select falsifies it. |
| 2026-07-04 | Mobile pass: the wall bleeds 9vw past both screen edges (titles cut mid-word, clipped — no x-scroll); archive gets a sticky year rail + `content-visibility` (the page holds 3 000 rows); swipe / ←→ leaf between quintes; finger-sized tap targets via padding+negative-margin | The ragged right margin made the wall look composed *for* the screen; bleeding it makes the mass feel like it continues beyond. Archive lede now says "archivées de 2009 à 2026" (the practice is *depuis 2006*, the dated holdings start 2009). |
| 2026-07-04 | **True Fraunces italic imported** (`wght-italic.css` + preload) — every italic had been a synthesized slant. Wall bleed fixed to exceed the widest title (`clamp(-280px,-17vw,-170px)`): smaller bleeds leave lines ending short of the edge because an unfitting title wraps whole. | AWWWards pass, part 1: typographic truth first. |
| 2026-07-04 | Search results re-set in the archive's language: default PagefindUI dropped for a custom renderer on the Pagefind JS API — whole row clickable, serif title (qtitle morph), italic excerpt with ocre-washed `<mark>`, mono `year · numéro` column (`data-pagefind-meta="r:…"`), French count/zero states ("rien pour « x » — tenter une rencontre au hasard ↻"), `?q=` deep links, « voir plus » pagination. Breadcrumb is `data-pagefind-ignore`d and quinte lines emit a separator space, so excerpts stopped reading "« Séances… » · séance de p(au)se" and "bleue,à". | A search hit is an archive entry that happens to match — it must look like one. |
| 2026-07-04 | One transition language site-wide: a clicked title (wall, archive, collection) is named `qtitle` just-in-time and **travels** to the destination page's h1; browser Back reverses it. Direct arrivals (shared links) get a per-line ink-in entrance instead — never both. Also: designed 404 in the quintesse status vocabulary ("dérobée… troquée, suspendue, détruite pour de bon"), print stylesheet (a printed quinte page = a museum label: text + colophon), « qu'est-ce qu'une quintesse ? » footnote → `/projet#quintesse`, ☾/☀︎ theme glyph names the destination, 3px hover nudge on list entries, hover-prefetch, skip link + ocre `:focus-visible` everywhere. | Mass↔one is the site's only motion metaphor — page transitions must speak it too, not stack a second vocabulary (no slides, no custom cursors). Entrance and morph are mutually exclusive so nothing animates twice. |
