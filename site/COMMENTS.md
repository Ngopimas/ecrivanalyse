# Réponses (comments) — how it works & how to deploy

> **Statut (juillet 2026) : pas encore en service.** Le site est hébergé sur
> GitHub Pages, qui ne peut pas exécuter `functions/api/`. Les deux endpoints
> (code Cloudflare Pages Functions, inchangé) doivent être hébergés sur un
> Worker Cloudflare, et l'`action` des formulaires pointée vers lui. Le flux
> décrit ci-dessous reste exact ; la checklist Cloudflare vaut pour le Worker.

Comments (« réponses ») are plain JSON files in `src/content/comments/`, one per
comment, rendered statically on each quinte page. Nothing dynamic is served.

**Flow for a new comment** — pre-moderation by email, one click:

1. A reader submits the form under a quinte → `POST /api/comment`
   (`functions/api/comment.js`, a Cloudflare Pages Function).
2. The function publishes nothing. It signs the payload (HMAC-SHA256) and
   emails Ivan the message with a single **« Publier cette réponse »** link.
   Ignoring the email = rejection; nothing is stored anywhere.
3. Clicking the link hits `GET /api/approve` (`functions/api/approve.js`),
   which verifies the signature and commits
   `site/src/content/comments/<quinte>-<timestamp>.json` to `main` via the
   GitHub API. The push triggers the normal build; the comment is live minutes
   later. The link is idempotent (second click → « Déjà publié »).

To **unpublish**, delete the JSON file (GitHub web UI works) — next build
removes it.

## The 10 archived SPIP comments

Imported by `scripts/import-comments.py` from
`ecrivanalyse-backup/data/comments.json` (all 10 comments the site ever
received, 2011–2018; capture verified complete against SPIP's own counts).
Re-running the script is safe (it overwrites the same files).

## Deploy checklist (Cloudflare Pages)

- Project root `site/`, build command `npm run build`, output `dist/`.
  The `functions/` directory is picked up automatically.
- Environment variables (Settings → Environment variables, all encrypted):
  - `COMMENT_SECRET` — long random string: `openssl rand -hex 32`
  - `RESEND_API_KEY` — resend.com key; verify the sending domain there
  - `MODERATOR_EMAIL` — Ivan's address
  - `FROM_EMAIL` — e.g. `Écrivanalyse <site@ecrivanalyse.net>`
  - `GITHUB_TOKEN` — fine-grained PAT, **this repo only**, permission
    **Contents: read & write**, nothing else
  - `GITHUB_REPO` — `owner/repo`
  - `GITHUB_BRANCH` (optional, default `main`),
    `COMMENTS_DIR` (optional, default `site/src/content/comments`)

Notes:

- In `npm run dev` the form 404s — functions only run on Pages (or via
  `wrangler pages dev`). The archived comments render everywhere.
- Spam posture: offscreen honeypot field + length caps; anything that gets
  through only reaches the inbox, never the site. If inbox spam ever becomes
  annoying, add Cloudflare Turnstile to the form and verify it in
  `comment.js`.
- No commenter emails are collected (GDPR-minimal). Unpublished comments
  never enter git history.
