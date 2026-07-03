#!/usr/bin/env python3
"""Écrivanalyse.net full backup crawler.

Public crawl of a SPIP 3.2.8 site served as ISO-8859-1.
Strategy: capture raw bytes first (time-critical), extract structure later.

Subcommands:
    frontier   Build the master URL list into state.sqlite
    capture    Download raw bytes for every pending URL (resumable, polite)
    extract    Parse local raw HTML -> structured JSON/CSV
    verify     Cross-check coverage, checksum media, write reports

Safe to re-run any phase: capture skips already-fetched URLs.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

BASE = "https://ecrivanalyse.net/"
HOST = "ecrivanalyse.net"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "ecrivanalyse-backup")
DB_PATH = os.path.join(OUT, "state.sqlite")
RAW = os.path.join(OUT, "raw")
MEDIA = os.path.join(OUT, "media")
DATA = os.path.join(OUT, "data")
LOGS = os.path.join(OUT, "logs")
ENC = "iso-8859-1"
UA = ("EcrivanalyseBackup/1.0 (personal archival backup before planned site "
      "deletion; contact romain@omaha-insights.com)")

MEDIA_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico",
             ".pdf", ".doc", ".docx", ".odt", ".rtf", ".ppt", ".pptx", ".xls",
             ".xlsx", ".ods", ".mp3", ".ogg", ".wav", ".mp4", ".webm", ".mov",
             ".zip", ".epub", ".txt")

FR_MONTHS = {"janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
             "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
             "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
             "decembre": 12}

_print_lock = threading.Lock()


def log(msg):
    line = f"{datetime.now().strftime('%H:%M:%S')} {msg}"
    with _print_lock:
        print(line, flush=True)
    os.makedirs(LOGS, exist_ok=True)
    with open(os.path.join(LOGS, "crawl.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ------------------------------------------------------------------ DB
def db():
    conn = sqlite3.connect(DB_PATH, timeout=120)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS urls(
        url TEXT PRIMARY KEY,
        kind TEXT,
        status TEXT DEFAULT 'pending',
        http_code INTEGER,
        local_path TEXT,
        bytes INTEGER,
        sha256 TEXT,
        content_type TEXT,
        fetched_at TEXT,
        error TEXT,
        referer TEXT)""")
    conn.commit()
    return conn


def enqueue(conn, url, kind, referer=None):
    conn.execute("INSERT OR IGNORE INTO urls(url,kind,referer) VALUES(?,?,?)",
                 (url, kind, referer))


def counts(conn):
    rows = conn.execute("SELECT kind,status,COUNT(*) FROM urls "
                        "GROUP BY kind,status").fetchall()
    return rows


# ------------------------------------------------------------------ helpers
def norm(url):
    """Absolute-ize and drop fragments."""
    url = urljoin(BASE, url.strip())
    url, _, _ = url.partition("#")
    return url


def is_internal(url):
    return urlparse(url).netloc in ("", HOST)


def id_of(url, kind):
    m = re.search(rf"[?&]{kind}(\d+)", url)
    return int(m.group(1)) if m else None


def local_path_for(url, kind):
    p = urlparse(url)
    if kind in ("article", "rubrique", "auteur"):
        i = id_of(url, kind)
        if "debut_forum" in url:  # extra comment page
            deb = re.search(r"debut_forums?=(\d+)", url)
            suffix = f"_f{deb.group(1)}" if deb else "_extra"
            return os.path.join(RAW, kind + "s", f"{kind}{i}{suffix}.html")
        return os.path.join(RAW, kind + "s", f"{kind}{i}.html")
    if kind == "feed":
        name = re.sub(r"[^A-Za-z0-9]+", "_", (p.query or "backend")).strip("_")
        return os.path.join(RAW, "feeds", name + ".xml")
    if kind == "media":
        rel = p.path.lstrip("/")
        if not rel:
            rel = re.sub(r"[^A-Za-z0-9]+", "_", p.query)
        if p.query:  # keep query-distinguished assets unique
            rel += "__" + hashlib.sha1(p.query.encode()).hexdigest()[:8]
        return os.path.join(MEDIA, rel)
    # misc
    key = (p.query or p.path).strip("/")
    name = re.sub(r"[^A-Za-z0-9]+", "_", key).strip("_") or "index"
    return os.path.join(RAW, "misc", name[:120] + ".html")


def discover_from_html(text, base_url):
    """Return list of (url, kind) discovered in an HTML page."""
    found = []
    soup = BeautifulSoup(text, "lxml")
    for tag in soup.find_all(["a", "img", "link", "source", "embed", "object"]):
        for attr in ("href", "src", "data"):
            v = tag.get(attr)
            if not v:
                continue
            u = norm(v)
            if not is_internal(u):
                continue
            path = urlparse(u).path.lower()
            q = urlparse(u).query
            if any(path.endswith(e) for e in MEDIA_EXT):
                if not path.endswith("favicon.ico"):
                    found.append((u, "media"))
            elif "/IMG/" in u or u.rstrip("/").endswith("/IMG") or "/local/" in path:
                found.append((u, "media"))
            elif "debut_forum" in q:  # paginated comments
                found.append((u, "article"))
            elif re.search(r"[?&]auteur\d+", q):  # author byline -> author page
                found.append((norm(f"spip.php?auteur{id_of(u,'auteur')}"), "auteur"))
    return found


# ------------------------------------------------------------------ frontier
def cmd_frontier(args):
    os.makedirs(OUT, exist_ok=True)
    conn = db()
    sess = make_session()

    seeds = {
        norm("spip.php?page=plan"): "misc",
        BASE: "misc",
        norm("spip.php?page=backend"): "feed",
    }
    for u, k in seeds.items():
        enqueue(conn, u, k)
    conn.commit()

    # Fetch the plan (authoritative index) + homepage to harvest IDs.
    ids = {"article": set(), "rubrique": set(), "auteur": set()}
    for page in ("spip.php?page=plan", ""):
        u = norm(page or BASE)
        try:
            r = sess.get(u, timeout=40)
            html = r.content.decode(ENC, "replace")
        except Exception as e:
            log(f"frontier: failed {u}: {e}")
            continue
        for kind in ids:
            for m in re.finditer(rf"spip\.php\?{kind}(\d+)", html):
                ids[kind].add(int(m.group(1)))

    maxes = {k: (max(v) if v else 0) for k, v in ids.items()}
    log(f"frontier: harvested from plan -> "
        f"articles<= {maxes['article']} ({len(ids['article'])} linked), "
        f"rubriques<= {maxes['rubrique']} ({len(ids['rubrique'])} linked), "
        f"auteurs<= {maxes['auteur']} ({len(ids['auteur'])} linked)")

    # Brute ranges as insurance (404 = doesn't exist, cheap).
    pad_article = maxes["article"] + args.pad
    pad_rubrique = maxes["rubrique"] + 10
    pad_auteur = maxes["auteur"] + 10
    for i in range(1, pad_article + 1):
        enqueue(conn, norm(f"spip.php?article{i}"), "article")
    for i in range(1, pad_rubrique + 1):
        enqueue(conn, norm(f"spip.php?rubrique{i}"), "rubrique")
    for i in range(1, pad_auteur + 1):
        enqueue(conn, norm(f"spip.php?auteur{i}"), "auteur")
    # Per-rubrique RSS feeds (exact ISO dates for recent items).
    for i in range(1, pad_rubrique + 1):
        enqueue(conn, norm(f"spip.php?page=backend&id_rubrique={i}"), "feed")
    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM urls").fetchone()[0]
    log(f"frontier: {total} URLs queued "
        f"(articles 1..{pad_article}, rubriques 1..{pad_rubrique}, "
        f"auteurs 1..{pad_auteur}, + feeds)")


# ------------------------------------------------------------------ capture
def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA,
                      "Accept-Language": "fr,fr-FR;q=0.9"})
    return s


def fetch_one(sess, url, kind, delay, jitter):
    """Network only. Returns dict; no DB/disk side effects."""
    import random
    time.sleep(delay + random.random() * jitter)
    for attempt in range(3):
        try:
            r = sess.get(url, timeout=45, allow_redirects=True)
            code = r.status_code
            if code >= 500:
                raise requests.RequestException(f"HTTP {code}")
            discovered = []
            content = r.content
            ctype = r.headers.get("Content-Type", "")
            if code == 200 and ("html" in ctype or kind in
                                ("article", "rubrique", "auteur", "misc")):
                try:
                    text = content.decode(ENC, "replace")
                    discovered = discover_from_html(text, url)
                except Exception:
                    pass
            return {"url": url, "kind": kind, "code": code,
                    "content": content if code == 200 else None,
                    "ctype": ctype, "discovered": discovered, "error": None}
        except Exception as e:
            if attempt == 2:
                return {"url": url, "kind": kind, "code": None,
                        "content": None, "ctype": None,
                        "discovered": [], "error": str(e)}
            time.sleep(1.5 * (attempt + 1))


def save_result(conn, res):
    url, kind = res["url"], res["kind"]
    now = datetime.now(timezone.utc).isoformat()
    if res["error"]:
        conn.execute("UPDATE urls SET status='failed',error=?,fetched_at=? "
                     "WHERE url=?", (res["error"], now, url))
        return "failed"
    code = res["code"]
    if code == 404:
        conn.execute("UPDATE urls SET status='404',http_code=404,fetched_at=? "
                     "WHERE url=?", (now, url))
        return "404"
    if code != 200 or res["content"] is None:
        conn.execute("UPDATE urls SET status='failed',http_code=?,"
                     "error='non-200',fetched_at=? WHERE url=?",
                     (code, now, url))
        return "failed"
    path = local_path_for(url, kind)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(res["content"])
    sha = hashlib.sha256(res["content"]).hexdigest()
    conn.execute("""UPDATE urls SET status='done',http_code=200,local_path=?,
                    bytes=?,sha256=?,content_type=?,fetched_at=? WHERE url=?""",
                 (os.path.relpath(path, OUT), len(res["content"]), sha,
                  res["ctype"], now, url))
    for u, k in res["discovered"]:
        enqueue(conn, u, k, referer=url)
    return "done"


def cmd_capture(args):
    conn = db()
    sess = make_session()
    done = failed = notfound = 0
    wave = 0
    while True:
        pending = conn.execute(
            "SELECT url,kind FROM urls WHERE status='pending' "
            "ORDER BY (kind='media'), url LIMIT ?", (args.batch,)).fetchall()
        if not pending:
            break
        wave += 1
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(fetch_one, sess, u, k, args.delay, args.jitter)
                    for u, k in pending]
            n = 0
            for fut in as_completed(futs):
                res = fut.result()
                status = save_result(conn, res)
                n += 1
                if status == "done":
                    done += 1
                elif status == "404":
                    notfound += 1
                else:
                    failed += 1
                    log(f"  ! {res['kind']} {res['url']} -> {res['error']}")
                if n % 50 == 0:
                    conn.commit()
                    remaining = conn.execute(
                        "SELECT COUNT(*) FROM urls WHERE status='pending'"
                    ).fetchone()[0]
                    log(f"  progress: done={done} 404={notfound} "
                        f"failed={failed} pending={remaining}")
        conn.commit()
    log(f"capture COMPLETE: done={done} 404={notfound} failed={failed}")
    for kind, status, c in counts(conn):
        log(f"    {kind:10} {status:8} {c}")


# ------------------------------------------------------------------ extract
def fr_date_to_iso(s):
    """'Mercredi 2 novembre 2011' or '5 mars 2018 00:33' -> ISO string."""
    s = s.strip()
    # day may carry the French ordinal "1er" (only the 1st does).
    m = re.search(r"(\d{1,2})(?:\s*er)?\s+([A-Za-zûéèêôàçé]+)\s+(\d{4})"
                  r"(?:[,\s]+(\d{1,2})[:hH](\d{2}))?", s, re.I)
    if not m:
        return None
    day, month_name, year = int(m.group(1)), m.group(2).lower(), int(m.group(3))
    month = FR_MONTHS.get(month_name)
    if not month:
        return None
    hh = int(m.group(4)) if m.group(4) else 0
    mm = int(m.group(5)) if m.group(5) else 0
    try:
        return datetime(year, month, day, hh, mm).isoformat()
    except ValueError:
        return None


def text_of(node):
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip() if node else ""


def parse_comments(soup, article_id):
    """Extract SPIP forum messages with author/date/text and threading depth."""
    out = []
    for anchor in soup.find_all("a", id=re.compile(r"^forum\d+$")):
        fid = int(re.search(r"\d+", anchor["id"]).group())
        # The comment container is the nearest ancestor holding a forum-texte.
        container = anchor.find_parent(
            lambda t: t.name in ("div", "li") and t.find(
                "div", class_="forum-texte", recursive=True))
        title = text_of(anchor).lstrip("> ").strip()
        author, date_iso, date_raw, body_html, body_text = None, None, None, "", ""
        depth = 0
        if container:
            small = container.find("small")
            if small:
                date_raw = text_of(small)
                sp = small.find("span")
                if sp:
                    author = text_of(sp)
                    date_raw2 = date_raw.split(", par")[0]
                    date_iso = fr_date_to_iso(date_raw2)
                else:
                    date_iso = fr_date_to_iso(date_raw)
            texte = container.find("div", class_="forum-texte")
            if texte:
                body_html = texte.decode_contents().strip()
                body_text = text_of(texte)
            # crude threading: count forum-message ancestors
            depth = len(anchor.find_parents("div", class_="forum-message")) - 1
        out.append({"id_forum": fid, "article_id": article_id,
                    "depth": max(depth, 0), "title": title, "author": author,
                    "date": date_iso, "date_raw": date_raw,
                    "text_html": body_html, "text_plain": body_text})
    return out


def parse_article(path, article_id):
    with open(path, "rb") as f:
        soup = BeautifulSoup(f.read().decode(ENC, "replace"), "lxml")
    content = soup.find("div", class_="main-content") or soup
    title_node = content.find("h1", class_="titre")
    if not title_node:
        return None  # not a real article page
    soustitre = content.find("h3", class_="soustitre")
    details = content.find("p", class_="details")
    details_txt = text_of(details)
    date_iso = fr_date_to_iso(details_txt) if details_txt else None
    authors = []
    if details:
        for a in details.find_all("a", class_=re.compile("fn")):
            authors.append(text_of(a))
        if not authors:
            m = re.search(r",\s*par\s+(.+)$", details_txt)
            if m:
                authors = [x.strip() for x in re.split(r"\s+et\s+|,", m.group(1)) if x.strip()]
    # body = text of the first column1-unit, minus title/soustitre/details/comments
    body_node = content.find("div", class_="column1-unit") or content
    for junk in body_node.find_all(["h1", "h3", "form"], class_=re.compile("titre|soustitre|forum")):
        pass
    decompte = soup.find(["h2"], class_="forum-decompte")
    decompte_txt = text_of(decompte)
    dm = re.search(r"(\d+)", decompte_txt)
    reported_comments = int(dm.group(1)) if dm else None
    comments = parse_comments(soup, article_id)
    # attached docs / media referenced
    media = sorted({norm(t.get("href") or t.get("src"))
                    for t in body_node.find_all(["a", "img"])
                    if (t.get("href") or t.get("src"))
                    and ("/IMG/" in (t.get("href") or t.get("src") or "")
                         or "/local/" in (t.get("href") or t.get("src") or ""))})
    return {
        "id": article_id,
        "url": norm(f"spip.php?article{article_id}"),
        "title": text_of(title_node),
        "soustitre": text_of(soustitre),
        "authors": authors,
        "date": date_iso,
        "date_raw": details_txt,
        "text_html": (body_node.decode_contents().strip() if body_node else ""),
        "text_plain": text_of(body_node),
        "media": media,
        "reported_comment_count": reported_comments,
        "captured_comment_count": len(comments),
        "raw_html_path": os.path.relpath(path, OUT),
    }, comments


def parse_rubrique(path, rid):
    with open(path, "rb") as f:
        soup = BeautifulSoup(f.read().decode(ENC, "replace"), "lxml")
    content = soup.find("div", class_="main-content") or soup
    title = content.find(["h1"], class_="titre") or content.find("h1")
    art_ids = sorted({int(m.group(1)) for m in
                      re.finditer(r"spip\.php\?article(\d+)", str(content))})
    return {"id": rid, "url": norm(f"spip.php?rubrique{rid}"),
            "title": text_of(title), "article_ids": art_ids}


def parse_auteur(path, aid):
    with open(path, "rb") as f:
        soup = BeautifulSoup(f.read().decode(ENC, "replace"), "lxml")
    content = soup.find("div", class_="main-content") or soup
    title = content.find("h1")
    art_ids = sorted({int(m.group(1)) for m in
                      re.finditer(r"spip\.php\?article(\d+)", str(content))})
    return {"id": aid, "url": norm(f"spip.php?auteur{aid}"),
            "name": text_of(title), "bio": text_of(content)[:4000],
            "article_ids": art_ids}


def write_json(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def write_csv(name, rows, fields):
    with open(os.path.join(DATA, name), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            row = dict(r)
            for k, v in row.items():
                if isinstance(v, list):
                    row[k] = " | ".join(map(str, v))
            w.writerow(row)


def cmd_extract(args):
    os.makedirs(DATA, exist_ok=True)
    conn = db()
    articles, comments, rubriques, auteurs = [], [], [], []

    rows = conn.execute("SELECT url,kind,local_path FROM urls "
                        "WHERE status='done' AND local_path IS NOT NULL").fetchall()
    for url, kind, rel in rows:
        path = os.path.join(OUT, rel)
        if not os.path.exists(path):
            continue
        try:
            if kind == "article" and "debut_forum" not in url:
                res = parse_article(path, id_of(url, "article"))
                if res:
                    art, cms = res
                    articles.append(art)
                    comments.extend(cms)
            elif kind == "rubrique":
                rubriques.append(parse_rubrique(path, id_of(url, "rubrique")))
            elif kind == "auteur":
                a = parse_auteur(path, id_of(url, "auteur"))
                if a["name"]:
                    auteurs.append(a)
        except Exception as e:
            log(f"extract: error {url}: {e}")

    # Merge comments from paginated comment pages into their article.
    for url, kind, rel in rows:
        if kind == "article" and "debut_forum" in url:
            path = os.path.join(OUT, rel)
            try:
                with open(path, "rb") as f:
                    soup = BeautifulSoup(f.read().decode(ENC, "replace"), "lxml")
                aid = id_of(url, "article")
                seen = {(c["id_forum"]) for c in comments if c["article_id"] == aid}
                for c in parse_comments(soup, aid):
                    if c["id_forum"] not in seen:
                        comments.append(c)
            except Exception as e:
                log(f"extract: pagination error {url}: {e}")

    articles.sort(key=lambda a: a["id"])
    comments.sort(key=lambda c: (c["article_id"], c["id_forum"]))
    rubriques.sort(key=lambda r: r["id"])
    auteurs.sort(key=lambda a: a["id"])

    write_json("articles.json", articles)
    write_json("comments.json", comments)
    write_json("rubriques.json", rubriques)
    write_json("authors.json", auteurs)
    write_csv("articles.csv", articles,
              ["id", "url", "title", "soustitre", "authors", "date", "date_raw",
               "reported_comment_count", "captured_comment_count", "raw_html_path"])
    write_csv("comments.csv", comments,
              ["id_forum", "article_id", "depth", "title", "author", "date",
               "date_raw", "text_plain"])
    write_csv("rubriques.csv", rubriques, ["id", "url", "title", "article_ids"])
    write_csv("authors.csv", auteurs, ["id", "url", "name", "article_ids"])

    log(f"extract: {len(articles)} articles, {len(comments)} comments, "
        f"{len(rubriques)} rubriques, {len(auteurs)} authors")


# ------------------------------------------------------------------ verify
def cmd_verify(args):
    conn = db()
    os.makedirs(DATA, exist_ok=True)
    lines = ["# Écrivanalyse backup — coverage report",
             f"\nGenerated: {datetime.now(timezone.utc).isoformat()}\n"]

    def q(sql, *a):
        return conn.execute(sql, a).fetchone()[0]

    lines.append("## URL frontier status\n")
    lines.append("| kind | status | count |\n|---|---|---|")
    for kind, status, c in sorted(counts(conn)):
        lines.append(f"| {kind} | {status} | {c} |")

    # Media checksums / integrity
    media_rows = conn.execute(
        "SELECT url,local_path,bytes,sha256 FROM urls "
        "WHERE kind='media' AND status='done'").fetchall()
    missing, zero = 0, 0
    with open(os.path.join(DATA, "media-manifest.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source_url", "local_path", "bytes", "sha256"])
        for url, rel, b, sha in media_rows:
            p = os.path.join(OUT, rel) if rel else None
            if not p or not os.path.exists(p):
                missing += 1
            elif os.path.getsize(p) == 0:
                zero += 1
            w.writerow([url, rel, b, sha])

    failed = conn.execute("SELECT url,kind,error FROM urls "
                          "WHERE status='failed'").fetchall()
    lines.append(f"\n## Media\n- files: {len(media_rows)}\n"
                 f"- missing on disk: {missing}\n- zero-byte: {zero}\n")
    lines.append(f"## Failures ({len(failed)})\n")
    for url, kind, err in failed[:200]:
        lines.append(f"- [{kind}] {url} — {err}")

    # Data-level checks
    for name in ("articles", "comments", "rubriques", "authors"):
        p = os.path.join(DATA, f"{name}.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            lines.append(f"\n## {name}: {len(data)} records")
            if name == "articles":
                no_date = sum(1 for a in data if not a.get("date"))
                no_body = sum(1 for a in data if not a.get("text_plain"))
                mismatch = [a["id"] for a in data
                            if a.get("reported_comment_count") is not None
                            and a["reported_comment_count"] > a.get("captured_comment_count", 0)]
                lines.append(f"- missing date: {no_date}")
                lines.append(f"- empty body: {no_body}")
                lines.append(f"- comment-count mismatch (possible pagination gap): "
                             f"{len(mismatch)} {mismatch[:30]}")

    report = "\n".join(lines) + "\n"
    with open(os.path.join(LOGS, "coverage-report.md"), "w", encoding="utf-8") as f:
        f.write(report)

    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE,
        "cms": "SPIP 3.2.8", "encoding": ENC,
        "counts": {f"{k}/{s}": c for k, s, c in counts(conn)},
        "media_files": len(media_rows),
        "media_missing": missing, "media_zero_byte": zero,
        "failures": len(failed),
    }
    with open(os.path.join(OUT, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    log("verify: wrote logs/coverage-report.md, data/media-manifest.csv, "
        "MANIFEST.json")
    print("\n" + report[:2000])


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("frontier")
    f.add_argument("--pad", type=int, default=25,
                   help="extra article IDs past max as insurance")
    f.set_defaults(func=cmd_frontier)

    c = sub.add_parser("capture")
    c.add_argument("--workers", type=int, default=4)
    c.add_argument("--delay", type=float, default=0.3, help="base delay per req (s)")
    c.add_argument("--jitter", type=float, default=0.4, help="random extra delay (s)")
    c.add_argument("--batch", type=int, default=400, help="pending fetched per wave")
    c.set_defaults(func=cmd_capture)

    e = sub.add_parser("extract")
    e.set_defaults(func=cmd_extract)

    v = sub.add_parser("verify")
    v.set_defaults(func=cmd_verify)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
