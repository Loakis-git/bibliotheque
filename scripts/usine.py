#!/usr/bin/env python3
"""L'usine de la Bibliothèque.

  python3 scripts/usine.py prochaine        tire au sort la prochaine brique
  python3 scripts/usine.py build            valide la bibliothèque et régénère docs/data.js
  python3 scripts/usine.py stats            état des étages
  python3 scripts/usine.py cherche "titre"  cherche un titre déjà en rayon (étage 1)

Le hasard vient d'ici, pas de l'IA : c'est ce script qui choisit les pièces,
les parents et le mode de fusion.
"""
import collections
import datetime
import glob
import json
import os
import random
import re
import sys
import unicodedata

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = ["monde", "heros", "mecanique", "conflit", "ton"]
OBJECTIF_N1 = 500
MIN_N1_POUR_N2 = 8
GENRES_REFERENCE = [
    "action", "aventure", "comédie", "cuisine", "drame", "fantastique", "fantasy",
    "historique", "horreur", "jeu", "mecha", "musique", "mystère", "policier",
    "psychologique", "romance", "science-fiction", "sport", "surnaturel", "thriller",
    "tranche de vie", "post-apocalyptique", "école", "travail", "guerre", "contemplatif",
]
DECENNIES = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]


# ---------------------------------------------------------------- lecture

def norm(texte):
    t = unicodedata.normalize("NFKD", str(texte)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def lire_livre(chemin):
    with open(chemin, encoding="utf-8") as f:
        brut = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", brut, re.S)
    if not m:
        raise ValueError("en-tête YAML manquant (le fichier doit commencer par ---)")
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        raise ValueError("en-tête YAML invalide")
    meta["texte"] = m.group(2).strip()
    meta["fichier"] = os.path.relpath(chemin, ROOT)
    if "ajoute" in meta:
        meta["ajoute"] = str(meta["ajoute"])
    return meta


def charger(erreurs=None):
    livres = {}
    for chemin in sorted(glob.glob(os.path.join(ROOT, "livres", "n*", "*.md"))):
        try:
            livre = lire_livre(chemin)
        except Exception as e:  # noqa: BLE001
            if erreurs is not None:
                erreurs.append(f"{os.path.relpath(chemin, ROOT)} : {e}")
                continue
            raise
        lid = livre.get("id")
        if lid in livres and erreurs is not None:
            erreurs.append(f"id en double : {lid}")
        livres[lid] = livre
    return livres


def parents_de(livre):
    if livre.get("niveau") == 2:
        return list((livre.get("recette") or {}).values())
    return list(livre.get("parents") or [])


def etoiles():
    chemin = os.path.join(ROOT, "etoiles.txt")
    if not os.path.exists(chemin):
        return set()
    with open(chemin, encoding="utf-8") as f:
        return {l.strip() for l in f if l.strip() and not l.startswith("#")}


def modes():
    with open(os.path.join(ROOT, "recettes", "modes-de-fusion.md"), encoding="utf-8") as f:
        brut = f.read()
    res = {}
    for bloc in re.split(r"^## ", brut, flags=re.M)[1:]:
        nom, _, corps = bloc.partition("\n")
        res[nom.strip()] = corps.strip()
    return res


def comptes(livres):
    c = collections.Counter(l.get("niveau") for l in livres.values())
    return c


def niveau_max(c):
    return max([k for k in c if isinstance(k, int)] or [1])


def debloque(c, k):
    """Peut-on écrire un nouveau livre à l'étage k ?"""
    if k == 1:
        return c[1] < OBJECTIF_N1
    if k == 2 and c[1] < MIN_N1_POUR_N2:
        return False
    return c[k - 1] >= 2 * (c[k] + 1)


def racines(lid, livres, memo=None):
    memo = {} if memo is None else memo
    if lid in memo:
        return memo[lid]
    livre = livres.get(lid)
    if livre is None:
        return set()
    if livre.get("niveau") == 1:
        memo[lid] = {lid}
        return memo[lid]
    res = set()
    for p in parents_de(livre):
        res |= racines(p, livres, memo)
    memo[lid] = res
    return res


def usages(livres):
    u = collections.Counter()
    for l in livres.values():
        for p in parents_de(l):
            u[p] += 1
    return u


def prochain_id(livres, k):
    nums = [int(m.group(1)) for lid in livres
            if (m := re.match(rf"^n{k}-(\d+)$", str(lid)))]
    return f"n{k}-{(max(nums) + 1 if nums else 1):04d}"


# ---------------------------------------------------------------- tirage

def poids_livre(lid, stars, u):
    return (3.0 if lid in stars else 1.0) / (1 + u[lid])


def tirage_pondere(rng, elements, poids, n):
    """n éléments distincts, tirés au hasard selon leurs poids."""
    elements, poids = list(elements), list(poids)
    res = []
    for _ in range(min(n, len(elements))):
        i = rng.choices(range(len(elements)), weights=poids)[0]
        res.append(elements.pop(i))
        poids.pop(i)
    return res


def tirer_recenser(rng, livres):
    n1 = [l for l in livres.values() if l.get("niveau") == 1]
    genres = collections.Counter(norm(g) for l in n1 for g in (l.get("genres") or []))
    decs = collections.Counter((int(l["annee"]) // 10) * 10 for l in n1 if l.get("annee"))
    if rng.random() < 0.5:
        rares = sorted(GENRES_REFERENCE, key=lambda g: (genres[norm(g)], rng.random()))[:5]
        cible = f"un manga dont le genre principal est « {rng.choice(rares)} »"
    else:
        rares = sorted(DECENNIES, key=lambda d: (decs[d], rng.random()))[:3]
        cible = f"un manga dont la publication a commencé dans les années {rng.choice(rares)}"
    return {
        "action": "recenser",
        "niveau": 1,
        "cible": cible,
        "dossier": "livres/n1/",
        "consigne": "Choisis un vrai manga qui correspond à la cible et qui n'est pas déjà en rayon "
                    "(vérifie avec `usine.py cherche`). L'id est le slug du titre (minuscules, tirets).",
        "deja_en_rayon": len(n1),
    }


def tirer_assembler(rng, livres, stars, u):
    n1 = sorted(lid for lid, l in livres.items() if l.get("niveau") == 1)
    existantes = {tuple(sorted((l.get("recette") or {}).items()))
                  for l in livres.values() if l.get("niveau") == 2}
    for _ in range(50):
        types = ["monde"] + rng.sample(TYPES[1:], 2)
        sources = tirage_pondere(rng, n1, [poids_livre(x, stars, u) for x in n1], 3)
        recette = dict(zip(types, sources))
        if tuple(sorted(recette.items())) not in existantes:
            break
    return {
        "action": "assembler",
        "niveau": 2,
        "id": prochain_id(livres, 2),
        "recette": recette,
        "pieces": {t: livres[s]["pieces"][t] for t, s in recette.items()},
        "lire": [livres[s]["fichier"] for s in recette.values()],
        "dossier": "livres/n2/",
    }


def tirer_fusionner(rng, livres, k, stars, u, liste_modes):
    cands = sorted(lid for lid, l in livres.items() if l.get("niveau") == k - 1)
    if len(cands) < 2:
        return None
    deja = {frozenset(parents_de(l)) for l in livres.values() if l.get("niveau", 0) >= 3}
    poids = [poids_livre(x, stars, u) for x in cands]
    memo = {}
    paires = []
    for _ in range(40):
        a, b = tirage_pondere(rng, cands, poids, 2)
        if frozenset((a, b)) in deja:
            continue
        ra, rb = racines(a, livres, memo), racines(b, livres, memo)
        chevauchement = len(ra & rb) / max(1, len(ra | rb))
        paires.append((chevauchement, rng.random(), a, b))
    if not paires:
        return None
    if k >= 4:
        # Convergence lente : à haut niveau, on fusionne de préférence des branches éloignées.
        paires.sort()
    a, b = paires[0][2], paires[0][3]
    mode = rng.choice(sorted(liste_modes))
    lire = [livres[a]["fichier"], livres[b]["fichier"], "recettes/modes-de-fusion.md"]
    if k >= 4:
        lire.append("canon/bible.md")
    return {
        "action": "fusionner",
        "niveau": k,
        "id": prochain_id(livres, k),
        "parents": [a, b],
        "titres_parents": [livres[a].get("titre"), livres[b].get("titre")],
        "mode": mode,
        "definition_du_mode": liste_modes[mode].split("\n")[0],
        "lire": lire,
        "dossier": f"livres/n{k}/",
        "canon": "Ajoute 1 à 3 entrées à canon/bible.md et liste-les dans le champ `canon`." if k >= 4 else None,
    }


def cmd_prochaine():
    graine = int.from_bytes(os.urandom(4), "big")
    rng = random.Random(graine)
    livres = charger()
    c = comptes(livres)
    stars, u, liste_modes = etoiles(), usages(livres), modes()

    actions = []
    if debloque(c, 1):
        actions.append(("recenser", 1, 3.0))
    for k in range(2, niveau_max(c) + 2):
        if debloque(c, k):
            actions.append(("assembler" if k == 2 else "fusionner", k, 2.0))
    if len(liste_modes) < 15 and len(livres) >= 20:
        actions.append(("inventer-mode", None, 0.4))
    if not actions:
        print("La bibliothèque est complète : aucun étage ne peut plus grandir.")
        return

    resultat = None
    while actions and resultat is None:
        i = rng.choices(range(len(actions)), weights=[a[2] for a in actions])[0]
        nom, k, _ = actions.pop(i)
        if nom == "recenser":
            resultat = tirer_recenser(rng, livres)
        elif nom == "assembler":
            resultat = tirer_assembler(rng, livres, stars, u)
        elif nom == "fusionner":
            resultat = tirer_fusionner(rng, livres, k, stars, u, liste_modes)
        else:
            resultat = {"action": "inventer-mode", "modes_existants": sorted(liste_modes)}
    if resultat is None:
        resultat = tirer_recenser(rng, livres)

    resultat["graine"] = graine
    resultat["maintenant"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    print("PROCHAINE BRIQUE — suis exactement ce tirage (voir CLAUDE.md pour le format).\n")
    print(json.dumps(resultat, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- validation et build

def valider(livres, liste_modes):
    erreurs, avertissements = [], []
    for lid, l in livres.items():
        f = l.get("fichier", lid)
        k = l.get("niveau")
        dossier = os.path.basename(os.path.dirname(f))
        if not isinstance(k, int) or dossier != f"n{k}":
            erreurs.append(f"{f} : niveau {k!r} incohérent avec le dossier {dossier}")
            continue
        if os.path.splitext(os.path.basename(f))[0] != str(lid):
            erreurs.append(f"{f} : le nom du fichier doit être <id>.md (id = {lid})")
        for champ in ("id", "titre", "ajoute"):
            if not l.get(champ):
                erreurs.append(f"{f} : champ `{champ}` manquant")
        if len(l.get("texte", "")) < 200:
            erreurs.append(f"{f} : texte trop court")
        if k == 1:
            p = l.get("pieces") or {}
            manquantes = [t for t in TYPES if not p.get(t)]
            if manquantes:
                erreurs.append(f"{f} : pièces manquantes {manquantes}")
            for champ in ("auteurs", "annee", "genres"):
                if not l.get(champ):
                    erreurs.append(f"{f} : champ `{champ}` manquant")
            if not l.get("sources") and l.get("generation") != 0:
                avertissements.append(f"{f} : aucune source")
        elif k == 2:
            r = l.get("recette") or {}
            if "monde" not in r or len(r) != 3:
                erreurs.append(f"{f} : la recette doit avoir 3 pièces dont un `monde`")
            for t, s in r.items():
                if t not in TYPES:
                    erreurs.append(f"{f} : type de pièce inconnu `{t}`")
                if livres.get(s, {}).get("niveau") != 1:
                    erreurs.append(f"{f} : la pièce `{t}` vient de `{s}`, qui n'est pas un livre d'étage 1")
            if len(set(r.values())) != len(r):
                erreurs.append(f"{f} : les 3 pièces doivent venir de 3 mangas différents")
        else:
            ps = l.get("parents") or []
            if len(ps) != 2 or len(set(ps)) != 2:
                erreurs.append(f"{f} : il faut exactement 2 parents différents")
            for p in ps:
                if livres.get(p, {}).get("niveau") != k - 1:
                    erreurs.append(f"{f} : le parent `{p}` n'est pas un livre d'étage {k - 1}")
            if l.get("mode") not in liste_modes:
                erreurs.append(f"{f} : mode `{l.get('mode')}` absent de recettes/modes-de-fusion.md")
            if l.get("colonne") not in ps:
                erreurs.append(f"{f} : `colonne` doit être l'un des deux parents")
            if not l.get("emergence"):
                erreurs.append(f"{f} : champ `emergence` manquant")
            if k >= 4 and not l.get("canon"):
                avertissements.append(f"{f} : aucune entrée de canon")
    return erreurs, avertissements


def cle_ordre(l):
    return (str(l.get("ajoute", "")), l.get("niveau", 0), str(l.get("id")))


def cmd_build():
    erreurs = []
    livres = charger(erreurs)
    liste_modes = modes()
    e, a = valider(livres, liste_modes)
    erreurs += e
    for x in a:
        print("avertissement :", x)
    if erreurs:
        for x in erreurs:
            print("ERREUR :", x)
        sys.exit(1)

    c = comptes(livres)
    enfants = collections.defaultdict(list)
    for lid, l in livres.items():
        for p in parents_de(l):
            enfants[p].append(lid)
    memo = {}
    sortie = []
    for i, l in enumerate(sorted(livres.values(), key=cle_ordre)):
        lid = l["id"]
        d = {k: v for k, v in l.items() if k != "fichier"}
        d["parents"] = parents_de(l)
        d["enfants"] = sorted(enfants.get(lid, []))
        d["racines"] = sorted(racines(lid, livres, memo))
        d["ordre"] = i
        d["fichier"] = l["fichier"]
        sortie.append(d)

    etages = []
    for k in range(1, niveau_max(c) + 2):
        besoin = OBJECTIF_N1 if k == 1 else max(2 * (c[k] + 1), MIN_N1_POUR_N2 if k == 2 else 0)
        etages.append({"niveau": k, "livres": c[k], "debloque": debloque(c, k),
                       "dessous": c[k - 1] if k > 1 else None, "besoin": besoin})

    with open(os.path.join(ROOT, "canon", "bible.md"), encoding="utf-8") as f:
        bible = f.read()
    data = {
        "genere": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "etages": etages,
        "modes": liste_modes,
        "bible": bible,
        "etoiles": sorted(etoiles()),
        "livres": sortie,
    }
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "data.js"), "w", encoding="utf-8") as f:
        f.write("window.BIBLIO = ")
        json.dump(data, f, ensure_ascii=False, indent=1, default=str)
        f.write(";\n")
    print(f"OK : {len(livres)} livres, docs/data.js régénéré.")
    cmd_stats(livres)


def cmd_stats(livres=None):
    livres = livres or charger()
    c = comptes(livres)
    for k in range(1, niveau_max(c) + 2):
        etat = "débloqué" if debloque(c, k) else "verrouillé"
        print(f"  étage {k} : {c[k]:>4} livres  ({etat})")


def cmd_cherche(requete):
    q = norm(requete)
    trouves = [l for l in charger().values()
               if l.get("niveau") == 1 and (q in norm(l.get("titre", "")) or q in norm(l.get("id", "")))]
    if not trouves:
        print(f"Aucun livre d'étage 1 ne correspond à « {requete} » : la voie est libre.")
    for l in trouves:
        print(f"DÉJÀ EN RAYON : {l['id']} — {l['titre']} ({l.get('annee')})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "prochaine":
        cmd_prochaine()
    elif cmd == "build":
        cmd_build()
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "cherche" and len(sys.argv) > 2:
        cmd_cherche(" ".join(sys.argv[2:]))
    else:
        print(__doc__)
        sys.exit(1)
