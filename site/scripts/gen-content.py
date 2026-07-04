#!/usr/bin/env python3
"""Generate the content collections from the backup (reproducible).

Reads ecrivanalyse-backup/data/quintesses.json + the raw article HTML, then
rewrites src/content/quintes/ and src/content/textes/ in full:

  quintes/<id>.yaml  every 5x5 quinte. When the original page set prose around
                     the quinte (e.g. 154 "La maison dans la maison"), it is
                     kept in `prose`. Séance records whose quinte was never
                     published online (quintesse bought by the p(au)seur, text
                     only in a print recueil) keep `lines: []` and render as a
                     ghost page.
  textes/<id>.yaml   the rest of the œuvre: prose narratives (La petite fille
                     à côté), verse texts, Fluides chapters. `text` holds
                     paragraphs (\n\n) with line breaks (\n) and light <i>/<b>.

SPIP plumbing rubriques (contact, lettre de diffusion, the old "qu'est-ce
que", ÉOK book blurbs) are covered by /projet and dropped.

Run from anywhere:  python3 site/scripts/gen-content.py
"""
import json
import os
import re
import sys

from bs4 import BeautifulSoup, NavigableString

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "ecrivanalyse-backup", "raw", "articles")
DATA = os.path.join(ROOT, "ecrivanalyse-backup", "data", "quintesses.json")
QUINTES = os.path.join(ROOT, "site", "src", "content", "quintes")
TEXTES = os.path.join(ROOT, "site", "src", "content", "textes")

# the one illustrated article of the corpus (checked by sweeping every content
# div for <img>): 190 lays its quinte beside a photograph. Only the 210x139
# SPIP thumbnail survived the crawl; the file is copied to site/public/media/.
IMAGES = {
    190: ("/media/mise-au-point-par-md.jpg",
          "Mise au Point par M. D. · Poseur : I. J."),
}

# rubriques that are site plumbing, not œuvre — their substance lives in /projet
PLUMBING = {
    "ÉOK",
    "Qu’est-ce que l’écrivanalyse ?",
    "Contact et lettre de diffusion",
    "a.- Des Éditions Omar Kaczmar d’hier...",
    "b.- ... aux Éditions Œuvres Komplètes d’aujourd’hui",
}

ROLE_RE = re.compile(
    r"(P\(au\)seuse|P\(au\)seur|Pauseuse|Pauseur|Analisante|Analisant)\s*:", re.I)
META_RE = re.compile(r"^Quinte(sse)?\b", re.I)
RECUEIL_LEAD = re.compile(r"recueil\s*:\s*$", re.I)  # title follows in its own <p>
BR = "\x00"  # <br> sentinel, distinct from source whitespace


def render_inline(node):
    """Tag/text -> string keeping only <i>/<b> semantics; <br> becomes BR."""
    if isinstance(node, NavigableString):
        return str(node)
    if node.name == "br":
        return BR
    inner = "".join(render_inline(c) for c in node.children)
    if node.name in ("i", "em"):
        return f"<i>{inner}</i>" if inner.strip() else inner
    if node.name in ("b", "strong"):
        return f"<b>{inner}</b>" if inner.strip() else inner
    if node.name == "span" and "italic" in (node.get("style") or ""):
        return f"<i>{inner}</i>" if inner.strip() else inner
    return inner  # unwrap everything else (a, span, stray body…)


def to_lines(html_str):
    """Rendered inline string -> clean text lines (split on <br> only).

    U+00A0 (the no-break space SPIP sets before !?;:) is preserved - the
    whitespace collapse would swallow it, so shield it first.
    """
    text = html_str.replace("\xa0", "\x01")
    text = re.sub(r"\s+", " ", text).replace("\x01", "\xa0")
    return [seg.strip(" ") for seg in text.split(BR) if seg.strip()]


def blocks(path):
    """Content blocks of an article page, in document order.

    Returns a list of ('p'|'run', [lines]) — 'p' is a real paragraph,
    'run' is loose <br>-separated text directly in the content div
    (that is where the quinte itself lives on hybrid pages).
    """
    soup = BeautifulSoup(open(path, "rb").read().decode("iso-8859-1", "replace"), "lxml")
    col = soup.find("div", class_="column1-unit")
    if not col:
        return []
    for s in col.find_all(["h1", "h3"]):
        s.decompose()
    for s in col.find_all("p", class_="details"):
        s.decompose()
    out = []
    skip_next_p = False

    def walk(d):
        nonlocal skip_next_p
        run = []

        def flush():
            if run:
                lines = to_lines("".join(run))
                if lines:
                    out.append(("run", lines))
                run.clear()

        for child in d.children:
            name = getattr(child, "name", None)
            if name == "p":
                flush()
                lines = to_lines(render_inline(child))
                if not lines:
                    continue
                flat = re.sub(r"<[^>]+>", "", " ".join(lines))
                if skip_next_p:  # recueil title after "…recueil :"
                    skip_next_p = False
                    continue
                # participant / quintesse-status paragraphs are metadata,
                # already carried by the structured fields
                if ROLE_RE.search(flat) or META_RE.search(flat) or RECUEIL_LEAD.search(flat):
                    skip_next_p = bool(RECUEIL_LEAD.search(flat))
                    continue
                out.append(("p", lines))
            elif name == "div":
                flush()
                if not child.get("class"):  # e.g. the centered refrain divs of 158
                    walk(child)
            elif name == "small":
                flush()  # metadata block
            else:
                run.append(render_inline(child) if name else str(child))
        flush()

    for d in col.find_all("div"):
        if d.get("class"):
            continue
        # only start from top-level unclassed divs: walk() reaches the
        # nested ones in document order
        anc = d.parent
        while anc is not None and anc is not col:
            if anc.name == "div" and not anc.get("class"):
                break
            anc = anc.parent
        if anc is col:
            walk(d)
    return out


def yq(s):
    return '"' + (s or "").replace("\\", "\\\\").replace('"', '\\"') + '"'


def yblock(key, text):
    body = "\n".join(
        ("  " + ln if ln else "") for ln in text.split("\n"))
    return f"{key}: |-\n{body}\n"


def quinte_yaml(q, prose):
    y = [f"id: {q['id']}",
         f"title: {yq(q['title'])}",
         f"soustitre: {yq(q['soustitre'])}"]
    if q["lines"]:
        y.append("lines:")
        y += [f"  - {yq(l)}" for l in q["lines"]]
    else:
        y.append("lines: []")
    y += [f"is_5x5: {'true' if q['is_5x5'] else 'false'}",
          f"mode: {yq(q['mode'])}",
          f"participant_role: {yq(q['participant_role'])}",
          f"participant_name: {yq(q['participant_name'])}",
          f"quintesse_num: {yq(q['quintesse_num'])}",
          f"status: {yq(q['status'])}",
          f"collection: {yq(q['collection'])}",
          f"recueil: {yq(q['recueil'])}",
          f"date: {yq(q['date'])}",
          f"author: {yq(q['author'])}"]
    out = "\n".join(y) + "\n"
    img = IMAGES.get(q["id"])
    if img:
        out += f"image: {yq(img[0])}\nimage_caption: {yq(img[1])}\n"
    if prose:
        out += yblock("prose", prose)
    return out


def texte_yaml(q, text):
    y = [f"id: {q['id']}",
         f"title: {yq(q['title'])}",
         f"soustitre: {yq(q['soustitre'])}",
         f"mode: {yq(q['mode'])}",
         f"participant_role: {yq(q['participant_role'])}",
         f"participant_name: {yq(q['participant_name'])}",
         f"quintesse_num: {yq(q['quintesse_num'])}",
         f"status: {yq(q['status'])}",
         f"collection: {yq(q['collection'])}",
         f"recueil: {yq(q['recueil'])}",
         f"date: {yq(q['date'])}",
         f"author: {yq(q['author'])}"]
    return "\n".join(y) + "\n" + yblock("text", text)


def norm(s):
    return re.sub(r"[\W_]+", "", re.sub(r"<[^>]+>", "", s)).lower()


def main():
    quints = json.load(open(DATA))
    for q in quints:  # '' instead of None, like the site schema
        for k in ("soustitre", "mode", "participant_role", "participant_name",
                  "quintesse_num", "status", "collection", "recueil", "date", "author"):
            q[k] = q[k] or ""

    files_q, files_t = {}, {}
    stats = {"quinte": 0, "hybride": 0, "ghost": 0, "texte": 0, "plumbing": 0, "vide": 0}

    for q in quints:
        if q["collection"].replace("\xa0", " ") in PLUMBING:
            stats["plumbing"] += 1
            continue
        raw = os.path.join(RAW, f"article{q['id']}.html")
        bl = blocks(raw)
        # a séance's product is a quinte even when it takes liberties with
        # the 5×5 (e.g. 1024, six lines) — is_5x5 stays the strict flag
        is_quinte = q["is_5x5"] or bool(
            q["lines"] and (q["participant_role"] or q["status"]))
        quinte_key = norm(" ".join(q["lines"]))
        col_key = norm(q["collection"])

        def is_series_header(lines):
            # "Des figures féminines de moi - IV": the rubrique name + a
            # series numeral, repeated atop the page — metadata, not prose
            k = norm(" ".join(lines))
            return bool(col_key) and k.startswith(col_key) and \
                re.fullmatch(r"(partie)?[ivxlcdm0-9]{0,10}", k[len(col_key):]) is not None

        # keep document order; where the quinte itself sat, leave a <quinte>
        # marker so the page can seat it inside the prose (154: the quinte
        # completes the story's last sentence - it is not a separate block)
        paras = []
        for kind, lines in bl:
            if is_series_header(lines):
                continue
            if is_quinte and (kind == "run" or norm(" ".join(lines)) == quinte_key):
                if "<quinte>" not in paras:
                    paras.append("<quinte>")
                continue
            paras.append("\n".join(lines))
        text = "\n\n".join(p for p in paras if p)
        if text == "<quinte>":  # no prose at all: nothing to keep
            text = ""

        if is_quinte:
            files_q[q["id"]] = quinte_yaml(q, text)
            stats["hybride" if text else "quinte"] += 1
            if text:
                print(f"  hybride {q['id']}: {q['title']} ({len(text)} chars de prose)")
        elif not q["lines"] and q["participant_role"]:
            files_q[q["id"]] = quinte_yaml(q, "")
            stats["ghost"] += 1
        else:
            if not q["lines"] and not text:
                stats["vide"] += 1
                print(f"  ! vide, ignoré {q['id']}: {q['title']} ({q['collection']})")
                continue
            if not text:  # content lived in a run only (verse via <br>)
                text = "\n\n".join("\n".join(lines) for _, lines in bl)
            files_t[q["id"]] = texte_yaml(q, text)
            stats["texte"] += 1

    os.makedirs(TEXTES, exist_ok=True)
    for d, files in ((QUINTES, files_q), (TEXTES, files_t)):
        kept = {f"{i}.yaml" for i in files}
        for f in os.listdir(d):
            if f.endswith(".yaml") and f not in kept:
                os.remove(os.path.join(d, f))
                print(f"  - {os.path.relpath(os.path.join(d, f), ROOT)}")
        for i, content in files.items():
            p = os.path.join(d, f"{i}.yaml")
            old = open(p).read() if os.path.exists(p) else None
            if old != content:
                open(p, "w").write(content)

    print({k: v for k, v in stats.items()})
    print(f"quintes: {len(files_q)}  textes: {len(files_t)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
