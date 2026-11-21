#!/usr/bin/env python3
"""L'usine de la Bibliothèque : gisements -> pièces brutes -> assemblages.

  python3 scripts/usine.py prochaine        tire au sort la prochaine brique
  python3 scripts/usine.py build            valide l'usine et régénère docs/index.html
  python3 scripts/usine.py stats            état de l'usine
  python3 scripts/usine.py cherche "titre"  ce titre est-il déjà un gisement ?

Le hasard vient d'ici, pas de l'IA : c'est ce script qui choisit le gisement
à extraire et les pièces à assembler.
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
OBJECTIF_GISEMENTS = 500
RESERVE_BASSE = 3       # en dessous, l'usine réclame de la prospection
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


def lire_md(chemin):
    with open(chemin, encoding="utf-8") as f:
        brut = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", brut, re.S)
    if not m:
        raise ValueError("en-tête YAML manquant (le fichier doit commencer par ---)")
    meta = yaml.safe_load(m.group(1)) or {}
    meta["texte"] = m.group(2).strip()
    return meta


def lire_yaml(chemin):
    with open(chemin, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def charger(erreurs=None):
    """Renvoie (gisements, tas, assemblages), chacun indexé par id."""
    res = []
    for dossier, lecteur, ext in (("gisements", lire_md, "md"), ("tas", lire_yaml, "yaml"),
                                  ("assemblages", lire_md, "md")):
        d = {}
        for chemin in sorted(glob.glob(os.path.join(ROOT, dossier, f"*.{ext}"))):
            nom = os.path.splitext(os.path.basename(chemin))[0]
            try:
                x = lecteur(chemin)
            except Exception as e:  # noqa: BLE001
                if erreurs is None:
                    raise
                erreurs.append(f"{dossier}/{nom}.{ext} : {e}")
                continue
            x["fichier"] = f"{dossier}/{nom}.{ext}"
            for champ in ("ajoute", "extrait"):
                if champ in x:
                    x[champ] = str(x[champ])
            d[nom] = x
        res.append(d)
    return tuple(res)


def etoiles():
    chemin = os.path.join(ROOT, "etoiles.txt")
    if not os.path.exists(chemin):
        return set()
    with open(chemin, encoding="utf-8") as f:
        return {l.strip() for l in f if l.strip() and not l.startswith("#")}


def usages(assemblages):
    """Pièce (gisement, type) -> liste des assemblages qui l'ont utilisée. Une pièce reste réutilisable."""
    u = collections.defaultdict(list)
    for aid, a in sorted(assemblages.items()):
        for t, g in (a.get("recette") or {}).items():
            u[(g, t)].append(aid)
    return u


def prochain_id(assemblages):
    nums = [int(m.group(1)) for a in assemblages if (m := re.match(r"^n2-(\d+)$", a))]
    return f"n2-{(max(nums) + 1 if nums else 1):04d}"


# ---------------------------------------------------------------- tirage

def tirer_prospecter(rng, gisements):
    genres = collections.Counter(norm(g) for x in gisements.values() for g in (x.get("genres") or []))
    decs = collections.Counter((int(x["annee"]) // 10) * 10 for x in gisements.values() if x.get("annee"))
    if rng.random() < 0.5:
        rares = sorted(GENRES_REFERENCE, key=lambda g: (genres[norm(g)], rng.random()))[:5]
        cible = f"un manga dont le genre principal est « {rng.choice(rares)} »"
    else:
        rares = sorted(DECENNIES, key=lambda d: (decs[d], rng.random()))[:3]
        cible = f"un manga dont la publication a commencé dans les années {rng.choice(rares)}"
    return {
        "action": "prospecter",
        "cible": cible,
        "fichier_a_creer": "gisements/<slug-du-titre>.md",
        "gisements_connus": len(gisements),
    }


def tirer_extraire(rng, gisements, tas):
    vierges = sorted(g for g in gisements if g not in tas)
    g = rng.choice(vierges)
    return {
        "action": "extraire",
        "gisement": g,
        "titre": gisements[g].get("titre"),
        "lire": [gisements[g]["fichier"]],
        "fichier_a_creer": f"tas/{g}.yaml",
    }


def tirer_assembler(rng, gisements, tas, assemblages, stars):
    extraits = sorted(tas)
    if len(extraits) < 3:
        return None
    u = usages(assemblages)
    existantes = {tuple(sorted((a.get("recette") or {}).items())) for a in assemblages.values()}
    for _ in range(100):
        types = rng.sample(TYPES, 3)
        recette, pris = {}, set()
        for t in types:
            cands = [g for g in extraits if g not in pris]
            # Les pièces peu utilisées et les gisements étoilés sont tirés plus souvent.
            poids = [(3.0 if g in stars else 1.0) / (1 + len(u[(g, t)])) for g in cands]
            g = rng.choices(cands, weights=poids)[0]
            recette[t] = g
            pris.add(g)
        recette = {t: recette[t] for t in TYPES if t in recette}
        if tuple(sorted(recette.items())) not in existantes:
            aid = prochain_id(assemblages)
            return {
                "action": "assembler",
                "id": aid,
                "recette": recette,
                "pieces": {t: tas[g]["pieces"][t] for t, g in recette.items()},
                "origine": {t: gisements.get(g, {}).get("titre", g) for t, g in recette.items()},
                "fichier_a_creer": f"assemblages/{aid}.md",
            }
    return None


def cmd_prochaine():
    graine = int.from_bytes(os.urandom(4), "big")
    rng = random.Random(graine)
    gisements, tas, assemblages = charger()
    stars = etoiles()
    vierges = [g for g in gisements if g not in tas]

    actions = []
    if len(gisements) < OBJECTIF_GISEMENTS:
        actions.append(("prospecter", 3.0 if len(vierges) < RESERVE_BASSE else 1.0))
    if vierges:
        actions.append(("extraire", 2.0 if len(vierges) > RESERVE_BASSE else 1.0))
    if len(tas) >= 3:
        actions.append(("assembler", 2.0))

    resultat = None
    while actions and resultat is None:
        i = rng.choices(range(len(actions)), weights=[a[1] for a in actions])[0]
        nom, _ = actions.pop(i)
        if nom == "prospecter":
            resultat = tirer_prospecter(rng, gisements)
        elif nom == "extraire":
            resultat = tirer_extraire(rng, gisements, tas)
        else:
            resultat = tirer_assembler(rng, gisements, tas, assemblages, stars)
    if resultat is None:
        print("L'usine est à l'arrêt : plus rien à prospecter, extraire ou assembler.")
        return
    resultat["graine"] = graine
    resultat["maintenant"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    print("PROCHAINE BRIQUE — suis exactement ce tirage (voir CLAUDE.md pour le format).\n")
    print(json.dumps(resultat, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- validation et build

def valider(gisements, tas, assemblages):
    erreurs, avert = [], []
    for gid, g in gisements.items():
        f = g["fichier"]
        if g.get("id") != gid:
            erreurs.append(f"{f} : l'id doit être le nom du fichier ({gid})")
        for champ in ("titre", "auteurs", "annee", "genres", "ajoute"):
            if not g.get(champ):
                erreurs.append(f"{f} : champ `{champ}` manquant")
        if len(g.get("texte", "")) < 300:
            erreurs.append(f"{f} : résumé trop court")
        if not g.get("sources") and g.get("generation") != 0:
            avert.append(f"{f} : aucune source")
    for tid, t in tas.items():
        f = t["fichier"]
        if t.get("gisement") != tid or tid not in gisements:
            erreurs.append(f"{f} : doit porter le nom d'un gisement existant (champ `gisement: {tid}`)")
        p = t.get("pieces") or {}
        manquantes = [x for x in TYPES if not p.get(x)]
        if manquantes:
            erreurs.append(f"{f} : pièces manquantes {manquantes}")
        if set(p) - set(TYPES):
            erreurs.append(f"{f} : types de pièce inconnus {sorted(set(p) - set(TYPES))}")
        if not t.get("extrait"):
            erreurs.append(f"{f} : champ `extrait` manquant")
    for aid, a in assemblages.items():
        f = a["fichier"]
        if a.get("id") != aid:
            erreurs.append(f"{f} : l'id doit être le nom du fichier ({aid})")
        for champ in ("titre", "ajoute"):
            if not a.get(champ):
                erreurs.append(f"{f} : champ `{champ}` manquant")
        r = a.get("recette") or {}
        if len(r) != 3:
            erreurs.append(f"{f} : la recette doit utiliser exactement 3 pièces")
        if len(set(r.values())) != len(r):
            erreurs.append(f"{f} : les 3 pièces doivent venir de 3 gisements différents")
        for t, g in r.items():
            if t not in TYPES:
                erreurs.append(f"{f} : type de pièce inconnu `{t}`")
            elif g not in tas:
                erreurs.append(f"{f} : la pièce `{t}` de `{g}` n'a jamais été extraite")
        if len(a.get("texte", "")) < 300:
            erreurs.append(f"{f} : pitch trop court")
    return erreurs, avert


def cmd_build():
    erreurs = []
    gisements, tas, assemblages = charger(erreurs)
    e, a = valider(gisements, tas, assemblages)
    erreurs += e
    for x in a:
        print("avertissement :", x)
    if erreurs:
        for x in erreurs:
            print("ERREUR :", x)
        sys.exit(1)

    u = usages(assemblages)
    evenements = []
    for gid, g in gisements.items():
        evenements.append((g["ajoute"], 0, "gisement", gid))
    for tid, t in tas.items():
        evenements.append((t["extrait"], 1, "extraction", tid))
    for aid, x in assemblages.items():
        evenements.append((x["ajoute"], 2, "assemblage", aid))
    evenements.sort()
    ordre = {(e[2], e[3]): i for i, e in enumerate(evenements)}

    def propre(d):
        return {k: v for k, v in d.items() if k != "fichier"} | {"fichier": d["fichier"]}

    data = {
        "genere": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "objectif": OBJECTIF_GISEMENTS,
        "types": TYPES,
        "etoiles": sorted(etoiles()),
        "evenements": [{"type": e[2], "id": e[3], "date": e[0]} for e in evenements],
        "gisements": [propre(g) | {"ordre": ordre[("gisement", gid)]} for gid, g in sorted(gisements.items())],
        "tas": [propre(t) | {"ordre": ordre[("extraction", tid)],
                             "utilisations": {ty: u.get((tid, ty), []) for ty in TYPES}}
                for tid, t in sorted(tas.items())],
        "assemblages": [propre(x) | {"ordre": ordre[("assemblage", aid)]} for aid, x in sorted(assemblages.items())],
    }
    with open(os.path.join(ROOT, "docs", "modele.html"), encoding="utf-8") as f:
        modele = f.read()
    donnees = json.dumps(data, ensure_ascii=False, default=str).replace("</", "<\\/")
    with open(os.path.join(ROOT, "docs", "index.html"), "w", encoding="utf-8") as f:
        f.write(modele.replace("/*DONNEES*/null", donnees))
    print("OK : docs/index.html régénéré (données intégrées).")
    cmd_stats((gisements, tas, assemblages))


def cmd_stats(etat=None):
    gisements, tas, assemblages = etat or charger()
    print(f"  gisements    : {len(gisements)} / {OBJECTIF_GISEMENTS}  ({len(gisements) - len(tas)} encore vierges)")
    print(f"  pièces brutes: {len(tas) * len(TYPES)} extraites de {len(tas)} gisements")
    print(f"  assemblages  : {len(assemblages)}")


def cmd_cherche(requete):
    q = norm(requete)
    gisements, _, _ = charger()
    trouves = [g for g in gisements.values() if q in norm(g.get("titre", "")) or q in norm(g.get("id", ""))]
    if not trouves:
        print(f"Aucun gisement ne correspond à « {requete} » : la voie est libre.")
    for g in trouves:
        print(f"DÉJÀ CONNU : {g['id']} — {g['titre']} ({g.get('annee')})")


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
