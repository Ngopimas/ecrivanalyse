// Rasterize public/favicon.svg (light variant) into the PNG icons:
//   public/favicon-96.png       96×96, for browsers that skip SVG favicons
//   public/apple-touch-icon.png 180×180, square corners (iOS masks its own)
// Run from site/: node scripts/gen-icons.mjs

import { readFileSync, writeFileSync } from 'node:fs';
import { Resvg } from '@resvg/resvg-js';

const svg = readFileSync('public/favicon.svg', 'utf8');

function png(source, width) {
  return new Resvg(source, { fitTo: { mode: 'width', value: width } }).render().asPng();
}

writeFileSync('public/favicon-96.png', png(svg, 96));
writeFileSync('public/apple-touch-icon.png', png(svg.replace('rx="9"', 'rx="0"'), 180));
console.log('favicon-96.png + apple-touch-icon.png written');
