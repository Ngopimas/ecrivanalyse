// GET /api/approve?d=<payload>&s=<signature> — the « Publier » link from the
// moderation email. Verifies the HMAC signature, then commits the comment as
// a JSON file via the GitHub contents API; the push triggers the normal
// Cloudflare Pages build and the comment appears on the site.
//
// Env vars (in addition to COMMENT_SECRET from comment.js):
//   GITHUB_TOKEN   fine-grained PAT, single repo, Contents read/write only
//   GITHUB_REPO    e.g. "romain/ecrivanalyse"
//   GITHUB_BRANCH  optional, default "main"
//   COMMENTS_DIR   optional, default "site/src/content/comments" (repo-relative)

import { fromB64url, verify, utf8ToB64, escapeHtml, page } from './_lib.js';

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const data = url.searchParams.get('d') ?? '';
  const okSig = data && (await verify(env.COMMENT_SECRET, data, url.searchParams.get('s') ?? ''));
  if (!okSig) {
    return page(403, 'Lien invalide', '<p>Ce lien de publication n’est pas valide.</p>');
  }

  let payload;
  try {
    payload = JSON.parse(new TextDecoder().decode(fromB64url(data)));
  } catch {
    return page(400, 'Lien illisible', '<p>Le contenu du lien n’a pas pu être décodé.</p>');
  }

  const { quinte, author, text, date } = payload;
  const entry = { quinte, title: '', author, date, text };
  const dir = env.COMMENTS_DIR || 'site/src/content/comments';
  const path = `${dir}/${quinte}-${date.replace(/\D/g, '')}.json`;

  const res = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/contents/${path}`, {
    method: 'PUT',
    headers: {
      authorization: `Bearer ${env.GITHUB_TOKEN}`,
      accept: 'application/vnd.github+json',
      'content-type': 'application/json',
      'user-agent': 'ecrivanalyse-comments',
    },
    body: JSON.stringify({
      message: `réponse de ${author || 'anonyme'} sur la quinte ${quinte}`,
      content: utf8ToB64(JSON.stringify(entry, null, 2) + '\n'),
      branch: env.GITHUB_BRANCH || 'main',
    }),
  });

  const who = escapeHtml(author) || 'anonyme';
  const quinteUrl = `${url.origin}/quinte/${quinte}`;

  // 422 = the file already exists: this link was already clicked.
  if (res.status === 422) {
    return page(200, 'Déjà publié',
      `<p>Cette réponse de ${who} est déjà publiée
       — <a href="${quinteUrl}">voir la quinte</a>.</p>`);
  }
  if (!res.ok) {
    return page(502, 'Publication impossible',
      `<p>GitHub a répondu ${res.status}. Réessayez ce lien dans quelques minutes&nbsp;;
       si cela persiste, vérifiez le jeton d’accès.</p>`);
  }
  return page(200, 'Publié',
    `<p>La réponse de ${who} est acceptée. Elle apparaîtra
     <a href="${quinteUrl}">sur la quinte</a> d’ici quelques minutes,
     le temps que le site se reconstruise.</p>`);
}
