#!/usr/bin/env python3
"""Generate one Keystatic-native YAML file per quinte.

Writes site/src/content/quintes/<id>.yaml (empty strings for missing values so
Keystatic's select/text fields never choke on null). Regenerable; clears old
.md/.yaml first. Astro reads these via a glob('**/*.yaml') collection.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'ecrivanalyse-backup', 'data', 'quintesses.json')
OUT = os.path.join(ROOT, 'site', 'src', 'content', 'quintes')
os.makedirs(OUT, exist_ok=True)


def yq(s):
    if s is None:
        s = ''
    s = str(s).replace('\\', '\\\\').replace('"', '\\"')
    return '"' + s + '"'


def main():
    for f in os.listdir(OUT):
        if f.endswith('.md') or f.endswith('.yaml'):
            os.remove(os.path.join(OUT, f))
    data = json.load(open(SRC, encoding='utf-8'))
    n = 0
    for q in data:
        lines = q.get('lines') or []
        if not lines:
            continue
        rows = [
            f"id: {q['id']}",
            f"title: {yq(q.get('title'))}",
            f"soustitre: {yq(q.get('soustitre') or '')}",
            "lines:",
            *[f"  - {yq(l)}" for l in lines],
            f"is_5x5: {'true' if q.get('is_5x5') else 'false'}",
            f"mode: {yq(q.get('mode') or '')}",
            f"participant_role: {yq(q.get('participant_role') or '')}",
            f"participant_name: {yq(q.get('participant_name') or '')}",
            f"quintesse_num: {yq(q.get('quintesse_num') or '')}",
            f"status: {yq(q.get('status') or '')}",
            f"collection: {yq(q.get('collection') or '')}",
            f"recueil: {yq(q.get('recueil') or '')}",
            f"date: {yq(q.get('date') or '')}",
            f"author: {yq(q.get('author') or 'Ivan Joseph')}",
        ]
        with open(os.path.join(OUT, f"{q['id']}.yaml"), 'w', encoding='utf-8') as f:
            f.write("\n".join(rows) + "\n")
        n += 1
    print(f"wrote {n} quinte YAML files to {OUT}")


if __name__ == '__main__':
    main()
