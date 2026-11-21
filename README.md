# La Bibliothèque

Une bibliothèque qui s'agrandit toute seule, d'une brique par heure, comme une usine de Factorio.

- **Étage 1** : des résumés de vrais mangas, démontés en pièces (monde, héros, mécanique, conflit, ton).
- **Étage 2** : des pitchs de séries originales, assemblés à partir de pièces venues de trois œuvres différentes.
- **Étages 3 et plus** : des fusions de deux livres de l'étage du dessous, selon un mode tiré au sort (greffe, collision, transposition, lignée…).
- **Le canon** (`canon/bible.md`) : à partir de l'étage 4, les fusions ajoutent des lois, des lieux et des époques à un univers commun. Avec le temps, tout converge vers lui.

Chaque étage ne se débloque que si l'étage du dessous est assez fourni : il faut toujours au moins deux fois plus de livres en bas qu'en haut. Avec 500 mangas au rez-de-chaussée, la bibliothèque culmine vers l'étage 8 ou 9, où ne reste qu'un livre.

Le hasard est tiré par `scripts/usine.py`, pas par l'IA : c'est le script qui choisit les pièces, les parents et le mode. L'IA ne fait qu'écrire. Les règles de chaque passage sont dans [CLAUDE.md](CLAUDE.md).

## Voir la bibliothèque

Ouvre `docs/index.html` dans un navigateur, ou active GitHub Pages (Settings → Pages → branche `main`, dossier `/docs`).

## Influencer sans contrôler

Ajoute l'id d'un livre que tu aimes dans `etoiles.txt` (un par ligne) : il sera tiré trois fois plus souvent comme parent.

## Commandes

```bash
python3 scripts/usine.py prochaine   # tire la prochaine brique
python3 scripts/usine.py build       # valide et régénère docs/data.js
python3 scripts/usine.py stats       # état des étages
python3 scripts/usine.py cherche "titre"
```
