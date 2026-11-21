# La Bibliothèque — règles de l'usine

Ce dépôt est une bibliothèque qui grandit d'**une brique par passage** (un passage par heure, lancé par une tâche planifiée). Elle part de vrais mangas et, de fusion en fusion, converge lentement vers un seul univers.

Tu es l'ouvrier d'un passage. Tu n'as aucune mémoire des passages précédents : tout l'état est dans ce dépôt.

## Les étages

| Étage | Dossier | Ce que c'est | Fabriqué à partir de |
|---|---|---|---|
| 1 | `livres/n1/` | Résumé d'un **vrai** manga + son démontage en 5 pièces | Le monde réel (recherche web) |
| 2 | `livres/n2/` | **Pitch** d'une série originale | 3 pièces venant de 3 mangas différents de l'étage 1 |
| 3, 4, 5… | `livres/nK/` | **Fusion** de deux livres de l'étage du dessous | 2 livres de l'étage K-1 + un mode de fusion |

**Règle de déblocage (le ratio Factorio)** : on ne peut écrire un nouveau livre à l'étage K+1 que si l'étage K contient au moins `2 × (livres à l'étage K+1 + 1)` livres. Plus on monte, plus c'est rare. Le script applique cette règle pour toi.

## Déroulé d'un passage — une seule brique, toujours

1. `python3 scripts/usine.py prochaine` — le script tire au sort l'action et impose l'identifiant, les parents, les pièces et le mode de fusion. **Tu ne choisis jamais toi-même les parents, les pièces ou le mode** : le hasard vient du script, pas de toi. C'est ce qui empêche la bibliothèque de tourner autour des mêmes goûts.
2. Lis les fichiers que le script te désigne (les parents, et `canon/bible.md` à partir de l'étage 4).
3. Écris **un seul** nouveau fichier, au format décrit plus bas (ou, pour l'action `inventer-mode`, ajoute un mode dans `recettes/modes-de-fusion.md`).
4. `python3 scripts/usine.py build` — valide toute la bibliothèque et régénère `docs/data.js` (la visualisation). S'il signale une erreur, corrige ton fichier et relance.
5. Ajoute une ligne en bas de `journal.md` : `- AAAA-MM-JJ HH:MM · action · id · titre`.
6. Commit et push sur `main` :
   - message : `N2 · Le Joueur de brume (n2-0001)` (étage, titre, id) ;
   - si le push est rejeté : `git pull --rebase origin main`, relance `build`, puis push.

Ne modifie **jamais** un livre existant (sauf pour réparer une erreur de format signalée par `build`). La bibliothèque ne fait que grandir.

## Les actions

### `recenser` — étage 1

- Le script te donne une **cible** (un genre ou une décennie sous-représentés). Choisis un vrai manga publié qui correspond à la cible et qui n'est pas déjà en rayon : vérifie avec `python3 scripts/usine.py cherche "titre"`.
- Varie : mangas connus et confidentiels, toutes époques, tous publics (shōnen, seinen, shōjo, josei, kodomo), auteurs différents.
- Vérifie les faits (auteurs, année de début, prémisse) par une recherche web et mets 1 à 3 URL dans `sources`.
- Résumé de 150 à 250 mots, **écrit avec tes propres mots** : la prémisse, les grandes lignes, ce qui rend l'œuvre singulière. Aucun dialogue recopié, aucune image.
- Démontage en 5 pièces : `monde`, `heros`, `mecanique`, `conflit`, `ton`. Chaque pièce fait une phrase courte (15 mots maximum), **sans nom propre**, assez générique pour pouvoir être greffée dans une autre histoire.

### `assembler` — étage 2

- Le script impose 3 pièces venant de 3 mangas différents (toujours un `monde` + deux autres types).
- Écris le pitch d'une série **originale** de 250 à 400 mots : une accroche d'une phrase en italique, le pitch, 2 à 4 personnages inventés, et ce qui rend la série unique.
- Les pièces sont de la matière première à transformer, pas à recopier : aucun nom de personnage, de lieu inventé ou de terme propre aux œuvres sources.

### `fusionner` — étages 3 et plus

- Le script impose 2 parents de l'étage du dessous et un mode de fusion (défini dans `recettes/modes-de-fusion.md`).
- **Une colonne vertébrale** : choisis lequel des deux parents porte l'histoire (champ `colonne`) ; l'autre vient la transformer. Mélanger à parts égales donne une moyenne fade.
- **Une émergence obligatoire** : la fusion doit contenir au moins une idée qui n'existait dans aucun des deux parents. Résume-la en une phrase dans le champ `emergence`. C'est le signe que l'étage a produit quelque chose de neuf.
- Longueur : 400 à 600 mots à l'étage 3, 600 à 900 à l'étage 4, 800 à 1 200 au-delà.
- **À partir de l'étage 4** : lis `canon/bible.md`. Respecte ses lois, ou, si tu en contredis une, fais-le explicitement dans l'histoire et explique-le. Ajoute 1 à 3 entrées à la bible (loi, lieu, époque ou entité), chacune suivie de `(source : <id>)`, et liste-les dans le champ `canon` du livre. C'est comme ça que l'univers commun se construit.

### `inventer-mode`

- Ajoute un nouveau mode de fusion à `recettes/modes-de-fusion.md` : un titre `## nom-du-mode` (en minuscules, avec des tirets), une définition en une phrase, et un exemple en deux phrases. Il doit être vraiment différent des modes existants.
- Pas de nouveau livre pendant ce passage. Commit : `Mode · nom-du-mode`.

## Principes d'écriture (contre la moyenne)

- **Pas de jury, pas d'autocensure du « déjà vu »** : le hasard a choisi, ton travail est d'écrire le mieux possible ce qu'il a choisi.
- Pas de résolution heureuse par défaut. L'ambiguïté, l'échec et les fins ouvertes sont permis.
- Évite les noms de fantasy génériques (Elara, Kael, Lyra, Aiden, Seraphina…). Tire les noms des cultures, langues et époques réelles qui correspondent au monde de l'histoire.
- Ne fais pas la morale. Un personnage peut avoir tort jusqu'au bout.
- Garde la voix concrète : des lieux, des objets, des gestes, plutôt que des abstractions.

## Formats

Chaque livre est un fichier Markdown avec un en-tête YAML. Les ids sont donnés par le script.

**Étage 1** — `livres/n1/<slug>.md`
```yaml
---
id: death-note            # slug du titre
niveau: 1
titre: Death Note
auteurs: [Tsugumi Ohba, Takeshi Obata]
annee: 2003               # année de début de publication
genres: [thriller, surnaturel]
pieces:
  monde: ...
  heros: ...
  mecanique: ...
  conflit: ...
  ton: ...
sources: [https://...]
ajoute: 2026-11-21T11:00
---
Résumé…
```

**Étage 2** — `livres/n2/<id>.md`
```yaml
---
id: n2-0004
niveau: 2
titre: ...
recette:                  # type de pièce → id du livre d'étage 1 d'où elle vient
  monde: mushishi
  heros: hikaru-no-go
  mecanique: kaiji
ajoute: 2026-11-21T12:00
---
*Accroche.*

Pitch…
```

**Étages 3 et plus** — `livres/nK/<id>.md`
```yaml
---
id: n3-0004
niveau: 3
titre: ...
mode: greffe
parents: [n2-0001, n2-0003]
colonne: n2-0003
emergence: Une phrase sur l'idée nouvelle.
canon: []                 # entrées ajoutées à la bible (étage 4 et plus)
ajoute: 2026-11-21T13:00
---
Texte…
```

## Ce que tu ne touches pas

- `etoiles.txt` : c'est le propriétaire de la bibliothèque qui y met les ids des livres qu'il aime (le script les tire alors plus souvent comme parents).
- Les scripts et la visualisation (`scripts/`, `docs/index.html`), sauf si le propriétaire le demande.
