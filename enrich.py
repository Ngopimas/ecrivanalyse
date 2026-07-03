#!/usr/bin/env python3
"""Enrich the backup into quintesses.json with Ivan Joseph's real fields.

Reads raw article HTML + data/articles.json, writes data/quintesses.json (+ .csv):
  id, url, title, soustitre, lines[], is_5x5, mode, participant_role,
  participant_name, quintesse_num, status, collection, recueil, date, author.
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
STATUS = [("achetée par","achetée"),("autorisée à la vente","autorisée à la vente"),
          ("détruite pour","détruite"),("détruite","détruite"),("achevable avec","achevable")]

def wc(l): return len(re.findall(r"[0-9A-Za-zÀ-ÿ’'-]+", l))

def fr_iso(s):
    m = re.search(r"(\d{1,2})(?:\s*er)?\s+([A-Za-zûéèêôàçé]+)\s+(\d{4})", s, re.I)
    if not m: return None
    mo = FR_MONTHS.get(m.group(2).lower())
    if not mo: return None
    try: return f"{int(m.group(3)):04d}-{mo:02d}-{int(m.group(1)):02d}"
    except ValueError: return None

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
    author, collection, date = "", "", det_txt
    m = re.match(r"(.*?),\s*par\s*(.*?)\s*//\s*(.*)$", det_txt)
    if m: date, author, collection = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    date_iso = fr_iso(date)
    # metadata small block + lines
    for s in col.find_all(["h1","h3"]): s.decompose()
    for s in col.find_all("p", class_="details"): s.decompose()
    role=name=num=status=recueil=None; lines=None
    for d in col.find_all("div"):
        if d.get("class"): continue
        sm = d.find("small")
        if sm:
            t = re.sub(r"\s+"," ", sm.get_text(" ",strip=True))
            mr = re.match(r"(Pauseuse|Pauseur|Analisante|Analisant)\s*:\s*(.*)", t, re.I)
            if mr and role is None:
                role = mr.group(1).lower(); rest = mr.group(2)
                qm = re.search(r"Quintesse\s+([IVXLC]+)", rest)
                if qm: num = qm.group(1)
                name = re.split(r"\s*Quintesse", rest)[0].strip().strip(":").strip() or None
                for needle,val in STATUS:
                    if needle in rest.lower(): status = val; break
                rc = re.search(r"recueil\s*:\s*(.+)$", rest, re.I)
                if rc: recueil = re.sub(r"\s*Répondre.*$","",rc.group(1)).strip()
        for t in d.find_all(["small","p"]): t.extract()
        parts = [re.sub("<[^>]+>","",x).replace("\xa0"," ").strip() for x in re.split(r"<br\s*/?>", d.decode_contents())]
        parts = [re.sub(r"\s+"," ",x) for x in parts if x.strip()]
        if len(parts) >= 3 and (lines is None or len(parts) > len(lines)): lines = parts
    is_5x5 = bool(lines and len(lines)==5 and all(4<=wc(l)<=6 for l in lines))
    mode = "pause" if role in ("pauseur","pauseuse") else ("ecrivanalyse" if role in ("analisant","analisante") else None)
    aid = int(re.search(r"article(\d+)", path).group(1))
    return dict(id=aid, url=f"https://ecrivanalyse.net/spip.php?article{aid}", title=title,
                soustitre=sous, lines=lines or [], is_5x5=is_5x5, mode=mode,
                participant_role=role, participant_name=name, quintesse_num=num,
                status=status, collection=collection, recueil=recueil,
                date=date_iso, author=author or "Ivan Joseph")

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
    print("mode:", Counter(r['mode'] for r in out))
    print("role:", Counter(r['participant_role'] for r in out))
    print("status:", Counter(r['status'] for r in out))
    print("with quintesse_num:", sum(1 for r in out if r['quintesse_num']))
    return out

if __name__ == "__main__":
    main()
