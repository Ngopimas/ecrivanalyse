#!/usr/bin/env python3
"""Enrich the backup into quintesses.json with Ivan Joseph's real fields.

Reads raw article HTML + data/articles.json, writes data/quintesses.json (+ .csv):
  id, url, title, soustitre, lines[], is_5x5, mode, participant_role,
  participant_name, quintesse_num, status, collection, recueil, date, author.

`status` is the full original phrase ("achetée par l'analisante",
"suspendue pour la p(au)seuse", "autorisée à la vente"), not a normalized word.

The corpus has two participant-block formats:
  - 2011+ : a <small> block — "P(au)seuse : anonyme / Quintesse suspendue …"
  - ~2010 : a P.-S. paragraph — "Pauseuse : Morgane Rossi (Quintesse autorisée à la vente)"
and two quinte-line formats: <br>-separated text directly in a <div> (2011+),
or plain newlines inside a <p> (~2010).
"""
import glob, json, os, re, csv
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "ecrivanalyse-backup")
RAW = os.path.join(OUT, "raw", "articles")
DATA = os.path.join(OUT, "data")
ENC = "iso-8859-1"

FR_MONTHS = {"janvier":1,"février":2,"fevrier":2,"mars":3,"avril":4,"mai":5,"juin":6,
             "juillet":7,"août":8,"aout":8,"septembre":9,"octobre":10,"novembre":11,
             "décembre":12,"decembre":12}
# longer alternatives first (Analisante before Analisant)
ROLE_RE = re.compile(
    r"(P\(au\)seuse|P\(au\)seur|Pauseuse|Pauseur|Analisante|Analisant)\s*:\s*(.*)$", re.I)
QUINTESSE_RE = re.compile(r"Quintesse\s+(?:([IVXLC]+)\s+)?(.+)$")

# a word must contain a letter or digit: standalone dashes ("- possible mais
# inimaginable -") are punctuation, not words. œ/æ sit outside À-ÿ (U+0153 vs
# U+00C0-U+00FF) and would otherwise split "l'œil" in two. Dotted acronyms
# ("O.R.L.") count as one word, not one per letter.
W = r"[0-9A-Za-zÀ-ÿœŒæÆ]"
def wc(l): return len(re.findall(rf"(?:{W}\.){{2,}}|[’'-]*{W}[0-9A-Za-zÀ-ÿœŒæÆ’'-]*", l))

def fr_iso(s):
    m = re.search(r"(\d{1,2})(?:\s*er)?\s+([A-Za-zûéèêôàçé]+)\s+(\d{4})", s, re.I)
    if not m: return None
    mo = FR_MONTHS.get(m.group(2).lower())
    if not mo: return None
    try: return f"{int(m.group(3)):04d}-{mo:02d}-{int(m.group(1)):02d}"
    except ValueError: return None

def detypo(s):
    # get_text(" ") puts a space after elisions split across tags: "l’ analisante"
    return re.sub(r"([’'])\s+", r"\1", s) if s else s

def flat(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).replace("\xa0", " ").strip()

def split_lines(html, sep):
    parts = [re.sub("<[^>]+>", "", x).replace("\xa0", " ").strip()
             for x in re.split(sep, html)]
    return [re.sub(r"\s+", " ", x) for x in parts if x.strip()]

# incl. <br style="…"> (553); a table cell boundary is a line boundary too (190)
def br_lines(html): return split_lines(html, r"<br[^>]*>|</td>")
def nl_lines(html): return split_lines(html, r"\n")

def parse_meta(texts):
    """Extract role/name/num/status/recueil from the metadata block texts."""
    role = name = num = status = recueil = None
    for t in texts:
        mr = ROLE_RE.search(t)
        if mr and role is None:
            # normalize p(au)seur/euse -> pauseur/euse for the data key
            role = mr.group(1).lower().replace("(au)", "au")
            name = detypo(re.split(r"\s*\(?\s*Quintesse", mr.group(2))[0].strip(" (—–-,;:")) or None
        mq = QUINTESSE_RE.search(t)
        if mq and status is None:
            if mq.group(1): num = mq.group(1)
            p = mq.group(2)
            rc = re.search(r"recueil\s*:\s*(.+)$", p, re.I)
            if rc: recueil = re.sub(r"\s*Répondre.*$", "", rc.group(1)).strip() or None
            p = re.split(r"\s*[—–|,;]?\s*recueil\b.*$", p, flags=re.I)[0]
            p = re.sub(r"\s*Répondre.*$", "", p)
            while p.endswith(")") and p.count(")") > p.count("("):
                p = p[:-1].rstrip()
            status = detypo(p.strip().rstrip(".").strip()) or None
        if recueil is None:
            rc = re.search(r"recueil\s*:\s*(.+)$", t, re.I)
            if rc: recueil = re.sub(r"\s*Répondre.*$", "", rc.group(1)).strip() or None
    return role, name, num, status, detypo(recueil)

def parse(path):
    soup = BeautifulSoup(open(path,"rb").read().decode(ENC,"replace"),"lxml")
    col = soup.find("div", class_="column1-unit")
    if not col: return None
    title = col.find("h1", class_="titre")
    if not title: return None
    title = title.get_text(" ",strip=True)
    sous = col.find("h3", class_="soustitre")
    sous = sous.get_text(" ",strip=True) if sous else ""
    det = col.find("p", class_="details")
    det_txt = det.get_text(" ",strip=True) if det else ""
    # the SPIP rubrique id from the breadcrumb link: the only reliable
    # id -> collection mapping (data/rubriques.json is another taxonomy)
    rub = det.find("a", href=re.compile(r"rubrique(\d+)")) if det else None
    rub_id = int(re.search(r"rubrique(\d+)", rub["href"]).group(1)) if rub else None
    author, collection, date = "", "", det_txt
    m = re.match(r"(.*?),\s*par\s*(.*?)\s*//\s*(.*)$", det_txt)
    if m: date, author, collection = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    date_iso = fr_iso(date)
    # metadata blocks + lines
    for s in col.find_all(["h1","h3"]): s.decompose()
    for s in col.find_all("p", class_="details"): s.decompose()
    meta_texts = []; lines = None; nl_fallback = None; recueil_pending = False
    for d in col.find_all("div"):
        if d.get("class"): continue  # class="" is [], falsy: the P.-S. div stays in
        for sm in d.find_all("small"):
            meta_texts.append(flat(sm))
        for p in d.find_all("p"):
            t = flat(p)
            if ROLE_RE.search(t):
                meta_texts.append(t)  # P.-S.-era participant paragraph
                continue
            if recueil_pending:  # title paragraph after "…recueil :"
                meta_texts.append("recueil : " + t)
                recueil_pending = False
                continue
            if re.search(r"recueil\s*:\s*$", t, re.I):
                # ~2010 pages split it: "Quinte publiée dans le recueil :"
                # then the linked title in its own paragraph
                recueil_pending = True
                continue
            # ~2010 quintes: real line breaks are plain newlines inside a <p>.
            # Long prose is also hard-wrapped with newlines, so gate hard:
            # a handful of short lines, or it's not a quinte.
            parts = nl_lines(p.decode_contents())
            if 3 <= len(parts) <= 7 and all(len(x) <= 75 for x in parts) \
               and (nl_fallback is None or len(parts) > len(nl_fallback)): nl_fallback = parts
        for t in d.find_all(["small","p"]): t.extract()
        parts = br_lines(d.decode_contents())  # 2011+: <br>-separated, direct in div
        if len(parts) >= 3 and (lines is None or len(parts) > len(lines)): lines = parts
    role, name, num, status, recueil = parse_meta(meta_texts)
    # <br>-based lines always win; the newline fallback needs a participant
    # (real ~2010 quintes carry a P.-S. block — contact/prose pages don't)
    if lines is None and role: lines = nl_fallback
    aid = int(re.search(r"article(\d+)", path).group(1))
    # 190 lays the quinte out in a table beside a photograph ("Mise au Point
    # par M. D."): the caption cell merges into the line split — the quinte
    # is the first five lines (the left cell)
    if aid == 190 and lines: lines = lines[:5]
    is_5x5 = bool(lines and len(lines)==5 and all(4<=wc(l)<=6 for l in lines))
    mode = "pause" if role in ("pauseur","pauseuse") else ("ecrivanalyse" if role in ("analisant","analisante") else None)
    return dict(id=aid, url=f"https://ecrivanalyse.net/spip.php?article{aid}", title=title,
                soustitre=sous, lines=lines or [], is_5x5=is_5x5, mode=mode,
                participant_role=role, participant_name=name, quintesse_num=num,
                status=status, collection=collection, rubrique_id=rub_id,
                recueil=recueil, date=date_iso, author=author or "Ivan Joseph")

def main():
    files=[f for f in glob.glob(os.path.join(RAW,"article*.html")) if "_" not in os.path.basename(f)]
    out=[]
    for f in files:
        try:
            r=parse(f)
            if r: out.append(r)
        except Exception as e:
            print("err", f, e)
    out.sort(key=lambda x:x["id"])
    json.dump(out, open(os.path.join(DATA,"quintesses.json"),"w"), ensure_ascii=False, indent=1)
    with open(os.path.join(DATA,"quintesses.csv"),"w",newline="") as fh:
        w=csv.writer(fh); w.writerow(["id","date","title","mode","participant_role","participant_name","quintesse_num","status","collection","is_5x5"])
        for r in out:
            w.writerow([r["id"],r["date"],r["title"],r["mode"],r["participant_role"],r["participant_name"],r["quintesse_num"],r["status"],r["collection"],r["is_5x5"]])
    # stats
    from collections import Counter
    print(f"quintesses: {len(out)}")
    print("is_5x5:", sum(1 for r in out if r['is_5x5']))
    print("with lines:", sum(1 for r in out if r['lines']))
    print("mode:", Counter(r['mode'] for r in out))
    print("role:", Counter(r['participant_role'] for r in out))
    print("status (first word):", Counter((r['status'] or '').split(' ')[0] or None for r in out))
    print("with quintesse_num:", sum(1 for r in out if r['quintesse_num']))
    return out

if __name__ == "__main__":
    main()
