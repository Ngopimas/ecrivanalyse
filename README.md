# Écrivanalyse

Le site d'[Ivan Joseph](https://ecrivanalyse.net), **écrivanalyste** : vingt ans de
**quintes**, de courts textes tenus par une même contrainte (cinq lignes, cinq mots
par ligne, cinq signes de ponctuation), écrits depuis 2006 en *séances de p(au)se*
avec des inconnus et en *écrivanalyses* au long cours. Chaque quinte est écrite sur
une **quintesse**, l'objet que l'on peut acquérir.

Ce dépôt contient la sauvegarde intégrale du site d'origine (SPIP, 2009-2026) et sa
reconstruction moderne.

**Site : https://ngopimas.github.io/ecrivanalyse/** (domaine définitif à venir)

## Le corpus

3 157 pages capturées, reclassées en :

- **3 047 quintes**, dont 39 « fantômes » (des séances de 2010 dont la quinte n'a
  jamais été mise en ligne : la quintesse a été achetée, le texte ne se lit que dans
  le recueil *Faire une quinte de tout*) et une page hybride (154, prose autour de
  la quinte) ;
- **97 textes** : les proses de *La petite fille à côté*, *La danseuse de vélo* et
  le feuilleton *Fluides ou Le singulier pluriel* ;
- 13 pages de plomberie SPIP, écartées (leur substance vit sur `/projet`).

## Structure du dépôt

| Chemin | Rôle |
|---|---|
| `site/` | Le site (Astro 5, statique : Pagefind pour la recherche, cartes OG générées au build) |
| `site/src/content/quintes/`, `textes/` | Le corpus, un YAML par entrée |
| `site/scripts/gen-content.py` | Régénère les deux collections depuis la sauvegarde |
| `enrich.py` | Extrait la structure des quintes de la sauvegarde -> `data/quintesses.json` |
| `ecrivanalyse-backup/` | Sauvegarde publique du site SPIP : HTML brut, médias, données JSON/CSV (méthode : `PLAN.md`) |
| `scrape.py` | Le crawler qui a réalisé la capture |
| `DESIGN.md` | Système de design, lexique contraignant, journal des décisions |

## Développement

```bash
cd site
npm install
npm run dev       # http://localhost:4321
npm run build     # dist/ (astro + pagefind)
```

Pour régénérer le corpus depuis la sauvegarde :

```bash
python3 enrich.py                      # backup -> data/quintesses.json
python3 site/scripts/gen-content.py    # -> src/content/quintes + textes
```

## Déploiement

Chaque push sur `main` construit et publie le site sur GitHub Pages
(`.github/workflows/deploy.yml`). Tant que le domaine définitif n'est pas attaché,
le workflow fixe `BASE_PATH=/ecrivanalyse/` ; le jour venu, supprimer ces deux
lignes d'environnement et renseigner le domaine dans les réglages Pages.

Les **réponses** (commentaires prémodérés par un lien « Publier » envoyé par
e-mail) sont décrites dans `site/COMMENTS.md` ; leurs deux endpoints restent à
héberger sur un Worker Cloudflare.

## Vocabulaire

Le lexique de `DESIGN.md` fait loi : une **quinte** est le texte, une **quintesse**
est l'objet. On n'écrit jamais « poème ».

## Droits

Les quintes, les textes et les images sont l'œuvre d'Ivan Joseph et restent sa
propriété (© Ivan Joseph, tous droits réservés). Le code du site peut être lu et
réutilisé librement.
