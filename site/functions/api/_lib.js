// Shared helpers for the comment endpoints (underscore prefix = not routed).
// Cloudflare Pages Functions runtime: Web Crypto, fetch, no Node APIs.

const enc = new TextEncoder();

export function toB64url(bytes) {
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export function fromB64url(str) {
  const b64 = str.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(str.length / 4) * 4, '=');
  return Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
}

/** Standard base64 of a UTF-8 string (GitHub contents API format). */
export function utf8ToB64(str) {
  let s = '';
  for (const b of enc.encode(str)) s += String.fromCharCode(b);
  return btoa(s);
}

function hmacKey(secret, usages) {
  return crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, usages);
}

export async function sign(secret, data) {
  const key = await hmacKey(secret, ['sign']);
  return toB64url(new Uint8Array(await crypto.subtle.sign('HMAC', key, enc.encode(data))));
}

/** Timing-safe verification via crypto.subtle.verify. */
export async function verify(secret, data, sigB64url) {
  let sig;
  try { sig = fromB64url(sigB64url); } catch { return false; }
  const key = await hmacKey(secret, ['verify']);
  return crypto.subtle.verify('HMAC', key, sig, enc.encode(data));
}

export function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
}

/** Minimal French response page in the site's paper palette (no assets). */
export function page(status, title, bodyHtml) {
  const html = `<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>${escapeHtml(title)} — Écrivanalyse</title>
<style>
  body { background: #F6F1E7; color: #17130F; font-family: Georgia, serif;
    display: grid; place-items: center; min-height: 100vh; margin: 0; padding: 24px; }
  main { max-width: 56ch; }
  h1 { font-weight: 400; font-size: 28px; margin: 0 0 16px; }
  p { font-size: 17px; line-height: 1.6; }
  a { color: #B0472C; }
  @media (prefers-color-scheme: dark) {
    body { background: #1E1A16; color: #EDE6D8; }
    a { color: #CE7659; }
  }
</style></head>
<body><main><h1>${escapeHtml(title)}</h1>${bodyHtml}</main></body></html>`;
  return new Response(html, { status, headers: { 'content-type': 'text/html; charset=utf-8' } });
}
