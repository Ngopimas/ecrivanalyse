// Open Graph card renderer — the quinte set in Spectral on paper, 1200×630.
// Pure module (no Astro imports) so scripts/preview-og.mjs can use it too.
// Fonts are the static instances produced by scripts/gen-fonts.py; opentype.js
// measures line advances so the longest line exactly fits the column width
// (same intent as the fit script on the quinte page).

import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import opentype from 'opentype.js';
import { Resvg } from '@resvg/resvg-js';

const DIR = join(process.cwd(), 'src/assets/og');
const REGULAR_PATH = join(DIR, 'spectral-regular.ttf');
const ITALIC_PATH = join(DIR, 'spectral-italic.ttf');

const toAB = (buf) => buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
const regular = opentype.parse(toAB(readFileSync(REGULAR_PATH)));
const italic = opentype.parse(toAB(readFileSync(ITALIC_PATH)));

const W = 1200, H = 630, MARGIN = 96, BUDGET = W - MARGIN * 2;
const PAPER = '#F6F1E7', INK = '#17130F', MUTED = '#6B635A', OCRE = '#B0472C';

const esc = (s) => String(s).replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

/** Largest font size (capped) at which every line fits the column. */
function fitSize(font, lines, max, min) {
  let widest = 0;
  for (const l of lines) widest = Math.max(widest, font.getAdvanceWidth(l, 100));
  if (!widest) return max;
  return Math.max(min, Math.min(max, (100 * BUDGET) / widest));
}

function render(svg) {
  const r = new Resvg(svg, {
    font: { fontFiles: [REGULAR_PATH, ITALIC_PATH], loadSystemFonts: false, defaultFontFamily: 'Spectral' },
  });
  return r.render().asPng();
}

function frame(inner) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="${PAPER}"/>
  ${inner}
</svg>`;
}

export function quinteCard({ title, lines, date }) {
  // Cap by width (longest line) AND by height (any line count fits between
  // the header and the footer with air on both sides).
  const maxByHeight = 330 / (1.62 * Math.max(1, lines.length - 1));
  const size = fitSize(regular, lines, Math.min(52, maxByHeight), 20);
  const lineHeight = size * 1.62;
  const first = 306 - (lineHeight * (lines.length - 1)) / 2 + size * 0.35;
  const body = lines.map((l, i) =>
    `<text x="${MARGIN}" y="${(first + i * lineHeight).toFixed(1)}" font-family="Spectral" font-size="${size.toFixed(1)}" fill="${INK}">${esc(l)}</text>`
  ).join('\n  ');

  const year = (date || '').slice(0, 4);
  const footer = `« ${title} »${year ? ` · ${year}` : ''}`;
  const footerSize = fitSize(italic, [footer], 27, 16);

  return render(frame(`<text x="${MARGIN}" y="104" font-family="Spectral" font-style="italic" font-size="27" fill="${OCRE}">écrivanalyse</text>
  ${body}
  <text x="${MARGIN}" y="${H - 72}" font-family="Spectral" font-style="italic" font-size="${footerSize.toFixed(1)}" fill="${MUTED}">${esc(footer)}</text>`));
}

export function defaultCard() {
  const tagline = 'cinq lignes, cinq mots par ligne, cinq signes de ponctuation.';
  return render(frame(`<text x="${MARGIN}" y="316" font-family="Spectral" font-style="italic" font-size="96" fill="${INK}">écrivanalyse</text>
  <text x="${MARGIN}" y="384" font-family="Spectral" font-size="30" fill="${MUTED}">${esc(tagline)}</text>
  <text x="${MARGIN}" y="${H - 72}" font-family="Spectral" font-style="italic" font-size="27" fill="${OCRE}">Ivan Joseph</text>`));
}
