#!/usr/bin/env python3
"""Generate one Markdown file per quinte for Astro + Keystatic.

Reads ecrivanalyse-backup/data/quintesses.json, writes
site/src/content/quintes/<id>.md — YAML frontmatter (metadata + the five lines)
plus a human-readable body. Regenerable; safe to re-run.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'ecrivanalyse-backup', 'data', 'quintesses.json')
OUT = os.path.join(ROOT, 'site', 'src', 'content', 'quintes')
os.makedirs(OUT, exist_ok=True)


def yq(s):
    """YAML double-quoted scalar (or null)."""
    if s is None:
        return 'null'
    s = str(s).replace('\\', '\\\\').replace('"', '\\"')
    return '"' + s + '"'


def main():
    data = json.load(open(SRC, encoding='utf-8'))
    n = 0
    for q in data:
        lines = q.get('lines') or []
        if not lines:
            continue
        fm = [
            f"id: {q['id']}",
            f"url: {yq(q.get('url'))}",
            f"title: {yq(q.get('title'))}",
            f"soustitre: {yq(q.get('soustitre') or '')}",
            "lines:",
            *[f"  - {yq(l)}" for l in lines],
            f"is_5x5: {'true' if q.get('is_5x5') else 'false'}",
            f"mode: {yq(q.get('mode'))}",
            f"participant_role: {yq(q.get('participant_role'))}",
            f"participant_name: {yq(q.get('participant_name'))}",
            f"quintesse_num: {yq(q.get('quintesse_num'))}",
            f"status: {yq(q.get('status'))}",
            f"collection: {yq(q.get('collection') or '')}",
            f"recueil: {yq(q.get('recueil'))}",
            f"date: {yq(q.get('date'))}",
            f"author: {yq(q.get('author') or 'Ivan Joseph')}",
        ]
        body = "\n".join(lines)
        doc = "---\n" + "\n".join(fm) + "\n---\n\n" + body + "\n"
        with open(os.path.join(OUT, f"{q['id']}.md"), 'w', encoding='utf-8') as f:
            f.write(doc)
        n += 1
    print(f"wrote {n} quinte markdown files to {OUT}")


if __name__ == '__main__':
    main()
