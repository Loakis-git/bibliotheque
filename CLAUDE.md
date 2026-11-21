# La Bibliothèque — règles de l'usine

Ce dépôt est une usine à la Factorio. Elle grandit d'**une brique par passage** (un passage par heure, lancé par une tâche planifiée). Tu es l'ouvrier d'un passage. Tu n'as aucune mémoire des passages précédents : tout l'état est dans ce dépôt.

## La chaîne de production

| Maillon | Dossier | Équivalent Factorio | Ce que c'est |
|---|---|---|---|
| Gisement | `gisements/` | Le gisement de minerai sur la carte | Un **vrai** manga : sa fiche et son résumé. Objectif : 500 gisements. |
| Pièces brutes | `tas/` | Le minerai qui sort de l'extracteur | Les 5 pièces extraites d'un gisement : `monde`, `heros`, `mecanique`, `conflit`, `ton`. **Rien de nouveau** : on prélève seulement ce qui est dans l'œuvre. |
| Assemblage | `assemblages/` | Le produit qui sort de l'assembleur | Une **œuvre originale de niveau 2**, fabriquée à partir de 3 pièces venant de 3 gisements différents. |

Chaque gisement est extrait une seule fois et donne ses 5 pièces. **Une pièce reste disponible après avoir servi** : plusieurs œuvres peuvent utiliser la même. Le script tire de préférence les pièces encore peu utilisées.

Il n'existe pas encore de niveau au-dessus des assemblages. Les essais de niveaux 3 et 4 sont rangés dans `archives/`. Ne les utilise pas et n'y touche pas.

## Déroulé d'un passage : une seule brique, toujours

1. `python3 scripts/usine.py prochaine` : le script tire au sort l'action selon les besoins de l'usine. Il impose le gisement à extraire, ou les 3 pièces à assembler. **Tu ne choisis jamais toi-même le gisement à extraire ni les pièces à assembler.** C'est ce qui empêche l'usine de tourner autour des mêmes goûts.
2. Lis les fichiers que le script te désigne.
3. Écris **un seul** nouveau fichier, au format décrit plus bas.
4. `python3 scripts/usine.py build` : il valide l'usine et régénère `docs/index.html` (la visualisation, données intégrées). S'il signale une erreur, corrige ton fichier et relance.
5. Ajoute une ligne en bas de `journal.md` : `- AAAA-MM-JJ HH:MM · action · id · titre`.
6. Commit et push sur `main` :
   - message : `Prospection · Akira (akira)`, `Extraction · Akira (akira)` ou `Assemblage · Le Joueur de brume (n2-0004)` ;
   - si le push est rejeté : `git pull --rebase origin main`, relance `build`, puis push.

Ne modifie **jamais** un fichier existant de `gisements/`, `tas/` ou `assemblages/` (sauf pour réparer une erreur de format signalée par `build`). L'usine ne fait que grandir.

## Les trois actions

### `prospecter` : découvrir un gisement

- Le script te donne une **cible** : un genre ou une décennie sous-représentés. Choisis un vrai manga publié qui correspond à la cible et qui n'est pas encore un gisement. Vérifie avec `python3 scripts/usine.py cherche "titre"`.
- Varie les gisements : mangas connus et confidentiels, toutes époques, tous publics (shōnen, seinen, shōjo, josei, kodomo), auteurs différents.
- Vérifie les faits (auteurs, année de début, prémisse) par une recherche web, et mets 1 à 3 URL dans `sources`.
- Écris un résumé de 150 à 250 mots **avec tes propres mots** : la prémisse, les grandes lignes, ce qui rend l'œuvre singulière. Aucun dialogue recopié, aucune image.
- Pas de pièces dans ce passage : l'extraction est une autre brique.

### `extraire` : sortir les pièces brutes d'un gisement

- Le script désigne le gisement. Lis son résumé, et fais une recherche web si tu as besoin de préciser un élément.
- Écris ses 5 pièces. Chacune décrit fidèlement un élément **présent dans l'œuvre**. Tu n'inventes rien, tu n'interprètes pas, tu ne combines pas.
  - `monde` : le cadre, l'univers, la société.
  - `heros` : la figure du protagoniste.
  - `mecanique` : le moteur du récit, ce qui se répète de chapitre en chapitre.
  - `conflit` : l'opposition centrale.
  - `ton` : l'atmosphère, le registre.
- Chaque pièce fait une phrase courte (15 mots maximum), **sans nom propre**, pour pouvoir être reprise ailleurs comme matière première.

### `assembler` : fabriquer une œuvre de niveau 2

- Le script impose 3 pièces de 3 types différents, venant de 3 gisements différents.
- Écris le pitch d'une série **originale** de 250 à 400 mots :
  - une accroche d'une phrase en italique ;
  - le pitch ;
  - 2 à 4 personnages inventés ;
  - ce qui rend la série unique.
- Les 3 pièces sont la matière première : chacune doit être reconnaissable dans le pitch, mais transformée. Pour les types qui ne sont pas fournis, invente librement.
- Ne reprends aucun nom de personnage, de lieu ou de terme propre aux œuvres d'origine.

## Principes d'écriture (contre la moyenne)

- **Pas de jury, pas d'autocensure du « déjà vu »** : le hasard a choisi, ton travail est d'écrire le mieux possible ce qu'il a choisi.
- Pas de résolution heureuse par défaut. L'ambiguïté, l'échec et les fins ouvertes sont permis.
- Évite les noms de fantasy génériques (Elara, Kael, Lyra, Aiden, Seraphina…). Tire les noms des cultures, langues et époques réelles qui correspondent au monde de l'histoire.
- Ne fais pas la morale. Un personnage peut avoir tort jusqu'au bout.
- Garde la voix concrète : des lieux, des objets, des gestes, plutôt que des abstractions.

## Formats

**Gisement** : `gisements/<slug>.md` (le slug est tiré du titre : minuscules, tirets, sans accents)
```yaml
---
id: death-note
titre: Death Note
auteurs: [Tsugumi Ohba, Takeshi Obata]
annee: 2003               # année de début de publication
genres: [thriller, surnaturel]
sources: [https://...]
ajoute: 2026-11-21T11:00
---
Résumé…
```

**Pièces brutes** : `tas/<slug>.yaml` (même slug que le gisement)
```yaml
gisement: death-note
extrait: '2026-11-21T12:00'
pieces:
  monde: ...
  heros: ...
  mecanique: ...
  conflit: ...
  ton: ...
```

**Assemblage** : `assemblages/<id>.md` (l'id est donné par le script)
```yaml
---
id: n2-0004
titre: ...
recette:                  # type de pièce → gisement d'où elle vient
  monde: mushishi
  heros: hikaru-no-go
  mecanique: kaiji
ajoute: 2026-11-21T13:00
---
*Accroche.*

Pitch…
```

## Ce que tu ne touches pas

- `etoiles.txt` : le propriétaire y met les gisements qu'il aime. Leurs pièces sont alors tirées plus souvent.
- `archives/`, les scripts et le modèle de la visualisation (`scripts/`, `docs/modele.html`), sauf si le propriétaire le demande. `docs/index.html` est régénéré par `build` : ne l'édite pas à la main.
