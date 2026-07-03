// POST /api/comment — receives the reply form under a quinte.
// Publishes NOTHING: it signs the payload and emails Ivan a « Publier » link
// (handled by approve.js). Ignoring the email is the rejection path, so there
// is no state to clean up and unpublished text never enters the repo.
//
// Env vars (Cloudflare Pages → Settings → Environment variables, encrypted):
//   COMMENT_SECRET   long random string used to sign approval links
//   RESEND_API_KEY   resend.com API key (email delivery)
//   MODERATOR_EMAIL  where approval emails go (Ivan)
//   FROM_EMAIL       verified sender, e.g. "Écrivanalyse <site@ecrivanalyse.net>"

import { toB64url, sign, escapeHtml, page } from './_lib.js';

export async function onRequestPost({ request, env }) {
  let form;
  try {
    form = await request.formData();
  } catch {
    return page(400, 'Requête invalide', '<p>Le formulaire n’a pas pu être lu.</p>');
  }

  const quinte = String(form.get('quinte') ?? '').trim();
  const qtitle = String(form.get('title') ?? '').trim().slice(0, 200);
  const author = String(form.get('author') ?? '').trim().slice(0, 80);
  const text = String(form.get('text') ?? '').replace(/\r\n/g, '\n').trim().slice(0, 2000);

  const origin = new URL(request.url).origin;
  const back = `${origin}/quinte/${quinte}/#merci`;

  // Filled honeypot: a bot. Pretend success, send nothing.
  if (form.get('website')) return Response.redirect(back, 303);

  if (!/^\d{1,8}$/.test(quinte) || !text) {
    return page(400, 'Message incomplet',
      '<p>Le message est vide ou la quinte est introuvable. <a href="javascript:history.back()">Revenir</a>.</p>');
  }

  const payload = { quinte, author, text, date: new Date().toISOString().slice(0, 19) };
  const data = toB64url(new TextEncoder().encode(JSON.stringify(payload)));
  const approveUrl = `${origin}/api/approve?d=${data}&s=${await sign(env.COMMENT_SECRET, data)}`;
  const quinteUrl = `${origin}/quinte/${quinte}`;

  const html = `
<div style="font-family: Georgia, serif; color: #17130F; max-width: 560px;">
  <p style="font-size:13px; color:#6B635A;">Réponse reçue sur
    <a href="${quinteUrl}" style="color:#B0472C;">«&#8239;${escapeHtml(qtitle) || `quinte ${quinte}`}&#8239;»</a>
    — ${escapeHtml(author) || 'anonyme'}</p>
  <blockquote style="margin:16px 0; padding:12px 16px; border-left:2px solid #E2DACA; font-size:16px; line-height:1.6;">
    ${escapeHtml(text).replace(/\n/g, '<br>')}
  </blockquote>
  <p style="margin:24px 0;">
    <a href="${approveUrl}"
       style="background:#B0472C; color:#FBF8F1; padding:12px 24px; text-decoration:none; border-radius:2px; font-size:15px;">
      Publier cette réponse</a>
  </p>
  <p style="font-size:13px; color:#6B635A;">Pour refuser, ignorez simplement ce message&nbsp;:
    rien ne sera publié et rien n’est conservé.</p>
</div>`;

  const sent = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      authorization: `Bearer ${env.RESEND_API_KEY}`,
      'content-type': 'application/json',
    },
    body: JSON.stringify({
      from: env.FROM_EMAIL,
      to: [env.MODERATOR_EMAIL],
      subject: `Réponse à « ${qtitle || `quinte ${quinte}`} » — ${author || 'anonyme'}`,
      html,
    }),
  });

  if (!sent.ok) {
    return page(502, 'Envoi impossible',
      `<p>Votre message n’a pas pu être transmis. Merci de réessayer plus tard.
       <a href="${quinteUrl}">Revenir à la quinte</a>.</p>`);
  }

  // Back to the quinte: #merci shows the confirmation and hides the form (CSS :target).
  return Response.redirect(back, 303);
}
