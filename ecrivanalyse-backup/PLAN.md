# Écrivanalyse.net — Full Backup Plan (public crawl)

> **Statut : exécuté (juillet 2026).** La sauvegarde est complète ; ce document
> reste comme trace de la méthode de capture. Les données sont dans `data/`.

**Goal:** Capture everything on https://ecrivanalyse.net/ before the site is deleted —
articles, sections, authors, dates, names, comments, and all media — as durable,
structured, re-usable data.

**Access level:** Public only (no server, DB, or admin login).
**Deliverables prioritized:** Structured data (JSON/CSV) · Media & attachments · Comments in full.
(Raw HTML is kept as the parse source + provenance, not as the primary deliverable.)

---

## What we learned about the site (recon)

| Fact | Value | Why it matters |
|---|---|---|
| CMS | **SPIP 3.2.8** | Predictable URL scheme & structure; comments render inline on article pages |
| Server | Apache 2.4 / PHP 7.3 (Debian) | Shared PHP host — crawl politely, it can be knocked over |
| Encoding | **ISO-8859-1 (Latin-1)** | Must decode as latin-1 → store as UTF-8, or accented French text (é è à ç œ) is corrupted |
| Article URLs | `spip.php?article{N}`, N up to ~3518 | Enumerable by ID |
| Section URLs | `spip.php?rubrique{N}`, N up to ~182 | Enumerable by ID |
| Author URLs | `spip.php?auteur{N}` | Author display names + bios + their article lists |
| Site plan | `spip.php?page=plan` (263 KB) | **Authoritative tree** of every section & article — the master index |
| RSS backend | `spip.php?page=backend[&id_rubrique=N]` | **Exact ISO publish dates** + author + title (recent items per section) |
| robots.txt | none (404) | Nothing disallowed |

**Comments:** SPIP stores them as *forum* messages rendered **inline under each article**.
So crawling every article page captures its visible/approved comments. Heavily-commented
articles may paginate (`?debut_forums=…`) — we follow that.

---

## Guiding principle: capture first, parse later

The race against deletion is only about **Phase 1** (getting bytes off the server).
Phases 2–3 run entirely against the local copy and can be repeated/fixed forever.
So we do a fast, complete raw grab first, *then* extract structure at leisure.

---

## Output layout (in this repo)

```
ecrivanalyse-backup/
  raw/                      # exact HTTP responses, original latin-1 bytes (provenance)
    articles/article{N}.html
    rubriques/rubrique{N}.html
    auteurs/auteur{N}.html
    misc/plan.html, feeds/*.xml
  media/                    # every downloaded asset, original server paths preserved
    IMG/... local/... etc.
  data/                     # structured extraction (UTF-8)
    articles.json / .csv
    comments.json / .csv
    authors.json
    rubriques.json
    media-manifest.csv      # source_url, local_path, sha256, bytes, content_type
  logs/
    crawl.log
    coverage-report.md      # got / 404 / gaps, with counts
  state.sqlite              # URL frontier + status → enables RESUME after interruption
  MANIFEST.json             # run metadata, totals, checksums
```

---

## Phase 0 — Build the URL frontier (the master list of everything)

1. Fetch `spip.php?page=plan` → parse out **every** `article{N}`, `rubrique{N}`, `auteur{N}`.
2. Fetch RSS: site backend + `?page=backend&id_rubrique={N}` for each section → collect
   exact ISO dates, authors, titles (used later to enrich/verify dates).
3. **Belt-and-suspenders sweep:** also enqueue article IDs `1..MAX` and rubrique IDs `1..MAX`
   by brute range (MAX discovered from the plan, padded). Non-existent IDs just 404 — cheap
   insurance against anything missing from the plan.
4. Write the full frontier into `state.sqlite` with status `pending`.

## Phase 1 — Raw capture (the time-critical part) ⏱️

- Download every URL in the frontier, saving **exact response bytes** to `raw/`.
- **Follow comment pagination** on each article (`?debut_forums=…`) until exhausted.
- **Extract & enqueue media**: every `IMG/…`, `local/…`, and attached-document link found
  in article HTML → download to `media/` preserving path. Also probe `IMG/` for open
  directory listing (SPIP often exposes it) to catch unlinked files.
- **Politeness / robustness:**
  - Concurrency 3–4 workers, ~0.3–0.5 s jitter between requests (tunable).
  - Descriptive User-Agent identifying this as an archival backup.
  - Exponential backoff + retry on 5xx / timeouts; hard-fail logged, never silently dropped.
  - Idempotent + resumable: already-fetched URLs are skipped, so re-runs only fill gaps.
- Estimated volume: ~4–5k page requests + media. At this pace, tens of minutes for pages.

## Phase 2 — Structured extraction (offline, from `raw/`, re-runnable)

Parse the saved HTML (latin-1 → UTF-8) with BeautifulSoup/lxml into:

- **articles.json** — `id, url, title, surtitre/soustitre, rubrique_id, rubrique_path,
  authors[], date_published (ISO), date_modified, chapo (intro), text_html, text_plain,
  keywords/mots[], attached_documents[], comment_count, raw_html_path, fetched_at`
  - Dates: prefer exact ISO from RSS; else parse the French date on the page
    ("le 12 mars 2019") → normalize to ISO.
- **comments.json** — `id (id_forum if present), article_id, parent_id (threading),
  author_name, author_link/email if shown, date (ISO), title, body_html, body_text`
- **authors.json** — `id, name, bio, email_if_public, url, article_ids[]`
- **rubriques.json** — `id, title, parent_id, description, url, article_ids[]`
- Mirror each to CSV for spreadsheet/grep use.

## Phase 3 — Verify completeness & report

- Cross-check: articles discovered (plan + brute range) vs. successfully archived; list every gap.
- Assert each article record has title + date + body; flag anomalies.
- Verify every media entry: file exists, non-zero, sha256 recorded in `media-manifest.csv`.
- Write `coverage-report.md`: totals (articles, comments, authors, sections, media MB),
  404s, retries, and any URL we failed to capture — so "did we get everything?" is answerable.
- Write `MANIFEST.json` with run metadata and top-level checksums.

## Phase 4 (optional, parallel) — Independent public archive

- Submit the homepage + key pages to the Internet Archive "Save Page Now" so a
  second, independent copy exists off our machine. Cheap insurance for a deletion race.

---

## Tooling

Python 3 + `requests` + `beautifulsoup4` + `lxml`, with a SQLite frontier for resume.
One script, four sub-commands (`frontier`, `capture`, `extract`, `verify`) so each phase
runs independently and Phase 1 can be launched the instant we're ready.

## Risks & mitigations

- **Encoding corruption** → always decode latin-1 explicitly; keep raw bytes as ground truth.
- **Server overload / getting blocked** → low concurrency, jitter, backoff; can throttle further.
- **Site deleted mid-run** → Phase 1 first + resumable state means whatever we grabbed is safe.
- **Hidden/unlinked media** → brute IMG/ probe + directory-listing check.
- **Comment pagination missed** → explicitly follow `debut_forums` until empty.
```
