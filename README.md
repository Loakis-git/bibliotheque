# La Bibliothèque

Une usine à la Factorio qui fabrique des œuvres, une brique par heure.

1. **Gisements** (`gisements/`) : de vrais mangas, avec leur fiche et leur résumé. Objectif : 500.
2. **Pièces brutes** (`tas/`) : chaque gisement est extrait en 5 pièces (monde, héros, mécanique, conflit, ton). On ne crée rien : on prélève ce qui est déjà dans l'œuvre.
3. **Assemblages** (`assemblages/`) : des œuvres originales de niveau 2, fabriquées à partir de 3 pièces de 3 gisements différents. Les pièces utilisées sont consommées.

À chaque passage, `scripts/usine.py` tire au sort la brique suivante selon les besoins de l'usine. Il réclame de la prospection quand il ne reste plus de gisements vierges, et de l'extraction quand les tas se vident. C'est le script qui choisit le gisement à extraire et les pièces à assembler : l'IA ne fait qu'écrire. Les règles de chaque passage sont dans [CLAUDE.md](CLAUDE.md).

Les essais de niveaux supérieurs (fusions, bible de l'univers) sont mis de côté dans `archives/`.

## Voir l'usine

Ouvre `docs/index.html` dans un navigateur, ou active GitHub Pages (Settings → Pages → branche `main`, dossier `/docs`).

## Influencer sans contrôler

Ajoute l'id d'un gisement que tu aimes dans `etoiles.txt` (un par ligne) : ses pièces seront tirées trois fois plus souvent.

## Commandes

```bash
python3 scripts/usine.py prochaine   # tire la prochaine brique
python3 scripts/usine.py build       # valide et régénère docs/data.js
python3 scripts/usine.py stats       # état de l'usine
python3 scripts/usine.py cherche "titre"
```
