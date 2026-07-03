#!/usr/bin/env python3
"""One-time import of the SPIP forum comments captured in the backup.

Reads ecrivanalyse-backup/data/comments.json and writes one JSON file per
comment into site/src/content/comments/<article_id>-<id_forum>.json, matching
the `comments` collection schema in src/content.config.ts.

Line breaks inside a SPIP paragraph (some replies are poems) become \n;
paragraph boundaries become \n\n. The trailing "repondre message" link block
is dropped. Idempotent: re-running overwrites the same files.

Usage: python3 scripts/import-comments.py
"""

import html
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
BACKUP = SITE.parent / "ecrivanalyse-backup" / "data" / "comments.json"
OUT = SITE / "src" / "content" / "comments"

P_BLOCK = re.compile(r"<p(?:\s[^>]*)?>(.*?)</p>", re.DOTALL)
P_REPONDRE = re.compile(r'<p\s+class="forum-repondre-message".*?</p>', re.DOTALL)
TAG = re.compile(r"<[^>]+>")


def html_to_text(text_html: str) -> str:
    body = P_REPONDRE.sub("", text_html)
    paragraphs = []
    for inner in P_BLOCK.findall(body):
        lines = [
            re.sub(r"[ \t]+", " ", html.unescape(TAG.sub("", line))).strip()
            for line in inner.split("\n")
        ]
        para = "\n".join(l for l in lines if l)
        if para:
            paragraphs.append(para)
    return "\n\n".join(paragraphs)


def main() -> None:
    comments = json.loads(BACKUP.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    for c in comments:
        entry = {
            "quinte": str(c["article_id"]),
            "title": c.get("title") or "",
            "author": c.get("author") or "",
            "date": c["date"],
            "text": html_to_text(c["text_html"]),
            "legacy_id": c["id_forum"],
        }
        path = OUT / f"{c['article_id']}-{c['id_forum']}.json"
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n")
        print(f"{path.name}: {entry['author'] or 'anonyme'} — {len(entry['text'])} chars")
    print(f"\n{len(comments)} comments -> {OUT.relative_to(SITE)}")


if __name__ == "__main__":
    main()
