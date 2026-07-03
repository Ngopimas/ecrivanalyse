#!/usr/bin/env python3
"""Generate font assets from the Fontsource Fraunces variable woff2s.

Outputs (all committed):
  src/assets/og/fraunces-regular.ttf  static instance for the OG-image renderer
  src/assets/og/fraunces-italic.ttf   idem, italic (titles)
  public/favicon.svg                  Fraunces italic "é" traced to a path
                                      (favicons can't load webfonts), light/dark
                                      via prefers-color-scheme

Run from site/: ../.venv/bin/python3 scripts/gen-fonts.py
Requires: fonttools, brotli (installed in the repo venv).
"""

from pathlib import Path

from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

SITE = Path(__file__).resolve().parent.parent
FILES = SITE / "node_modules" / "@fontsource-variable" / "fraunces" / "files"
OG = SITE / "src" / "assets" / "og"

# Paper / ink palette from DESIGN.md
LIGHT_BG, LIGHT_INK = "#F6F1E7", "#17130F"
DARK_BG, DARK_INK = "#1E1A16", "#EDE6D8"


def instance(src: Path, axes: dict) -> TTFont:
    font = TTFont(src)
    present = {a.axisTag for a in font["fvar"].axes}
    instantiateVariableFont(font, {k: v for k, v in axes.items() if k in present}, inplace=True)
    font.flavor = None  # decompress woff2 -> plain ttf
    return font


def main() -> None:
    OG.mkdir(parents=True, exist_ok=True)

    # Text sizes in the OG card: body ~text opsz, a touch under 400 like the site.
    regular = instance(FILES / "fraunces-latin-wght-normal.woff2",
                       {"wght": 380, "opsz": 40, "SOFT": 0, "WONK": 0})
    regular.save(OG / "fraunces-regular.ttf")
    italic = instance(FILES / "fraunces-latin-wght-italic.woff2",
                      {"wght": 400, "opsz": 20, "SOFT": 0, "WONK": 0})
    italic.save(OG / "fraunces-italic.ttf")

    # Favicon glyph: display cut, semibold so it holds at 16 px.
    fav = instance(FILES / "fraunces-latin-wght-italic.woff2",
                   {"wght": 600, "opsz": 144, "SOFT": 0, "WONK": 0})
    glyph_name = fav.getBestCmap()[ord("é")]
    glyphs = fav.getGlyphSet()
    glyph = glyphs[glyph_name]

    bounds = BoundsPen(glyphs)
    glyph.draw(bounds)
    xmin, ymin, xmax, ymax = bounds.bounds

    # Fit the glyph into a 64-box, centered, ~62% tall.
    box, target = 64.0, 46.0
    s = target / (ymax - ymin)
    tx = (box - (xmax - xmin) * s) / 2 - xmin * s
    ty = (box - target) / 2 + ymax * s  # y flips: top of glyph -> top margin
    pen = SVGPathPen(glyphs, ntos=lambda f: f"{f:.1f}")
    glyph.draw(TransformPen(pen, Transform(s, 0, 0, -s, tx, ty)))
    d = pen.getCommands()

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <style>
    .bg {{ fill: {LIGHT_BG}; }} .ink {{ fill: {LIGHT_INK}; }}
    @media (prefers-color-scheme: dark) {{
      .bg {{ fill: {DARK_BG}; }} .ink {{ fill: {DARK_INK}; }}
    }}
  </style>
  <rect class="bg" width="64" height="64" rx="9"/>
  <path class="ink" d="{d}"/>
</svg>
"""
    (SITE / "public" / "favicon.svg").write_text(svg)
    for f in (OG / "fraunces-regular.ttf", OG / "fraunces-italic.ttf", SITE / "public" / "favicon.svg"):
        print(f"{f.relative_to(SITE)}  {f.stat().st_size / 1024:.1f}K")


if __name__ == "__main__":
    main()
