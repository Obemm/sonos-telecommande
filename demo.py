"""Enceintes imaginaires pour l'option --demo : essayer l'interface sans enceinte et sans bruit.

Même interface que serveur.Systeme. L'état vit en mémoire et la lecture avance avec l'horloge.
Les titres et artistes sont inventés.
"""
from __future__ import annotations

import time
import urllib.parse

VOLUMES = {"Bureau Bibliothèque Rdc": 14, "Bureau Imprimante Rdc": 9, "Cuisine Rdc": 12,
           "Salle de bain Rdc": 13, "Salon Rdc": 18}

# titre, artiste, album, durée en s (0 = radio en direct), teinte de la pochette (None = sans image)
MORCEAUX = [
    ("Soleil de minuit", "Les Ondes Douces", "Rivages", 231, 24),
    ("Ligne 7", "Kora Express", "Correspondances", 204, 190),
    ("Racines", "Dub Atelier", "Basse fréquence", 365, 140),
    ("Le café du matin", "Juliette et les Nuages", "Petit déjeuner", 188, 45),
    ("Night Drive", "Neon Tapes", "Autoroute", 341, None),
    ("Pluie d'été", "Orchestre de Poche", "Saisons", 217, 205),
    ("Groove du dimanche", "The Lazy Horns", "Brunch", 250, 330),
    ("Lettre à un ami", "Clara Vent", "Correspondances", 213, None),
    ("Marée haute", "Atlantique Sud", "Littoral", 225, 175),
    ("Radio Jazz du matin", "En direct", "", 0, 265),
]
FAVORIS = [{"type": "favori", "titre": m[0], "piste": i} for i, m in enumerate(MORCEAUX)] + [
    {"type": "liste", "titre": "Mix Samedi pour la nuit", "piste": None},
    {"type": "liste", "titre": "Dimanche tranquille", "piste": None},
]


class Refus(Exception):
    """Commande que de vraies enceintes refuseraient aussi (ex. « suivant » sur une radio)."""


def pochette(teinte: int | None) -> str | None:
    """Pochette dessinée à la volée (SVG en data URI) : aucun fichier, aucun accès réseau."""
    if teinte is None:
        return None
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 300'>"
           f"<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
           f"<stop offset='0' stop-color='hsl({teinte},72%,58%)'/>"
           f"<stop offset='1' stop-color='hsl({(teinte + 40) % 360},70%,28%)'/></linearGradient></defs>"
           f"<rect width='300' height='300' fill='url(#g)'/>"
           f"<circle cx='215' cy='90' r='62' fill='hsl({(teinte + 25) % 360},90%,75%)' opacity='.6'/>"
           f"<circle cx='95' cy='225' r='105' fill='none' stroke='white' stroke-opacity='.3' stroke-width='16'/></svg>")
    return "data:image/svg+xml," + urllib.parse.quote(svg)


class SystemeDemo:
    volume_max = 60

    def __init__(self):
        self.volumes = dict(VOLUMES)
        self.groupes: dict[str, dict] = {}
        self._nouveau(["Bureau Bibliothèque Rdc", "Bureau Imprimante Rdc", "Cuisine Rdc", "Salon Rdc"],
                      piste=0, lecture=True, pos=42)
        self._nouveau(["Salle de bain Rdc"], piste=3, pos=65)

    def _nouveau(self, pieces, piste=None, lecture=False, pos=0):
        self.groupes[pieces[0]] = {"pieces": list(pieces), "piste": piste, "lecture": lecture,
                                   "pos": float(pos), "depuis": time.time(), "muet": False}

    # -------- temps qui passe

    @staticmethod
    def _duree(g) -> int:
        return MORCEAUX[g["piste"]][3] if g["piste"] is not None else 0

    @staticmethod
    def _position(g) -> float:
        return g["pos"] + (time.time() - g["depuis"] if g["lecture"] else 0)

    def _figer(self, g):
        g["pos"], g["depuis"] = self._position(g), time.time()

    @staticmethod
    def _apres(i: int, sens: int) -> int:
        i = (i + sens) % len(MORCEAUX)
        while MORCEAUX[i][3] == 0:  # on saute la radio
            i = (i + sens) % len(MORCEAUX)
        return i

    def _avancer(self, g):
        """Morceau fini : on passe au suivant, comme une file d'attente."""
        while self._duree(g) and self._position(g) >= self._duree(g):
            self._figer(g)
            g["pos"] -= self._duree(g)
            g["piste"] = self._apres(g["piste"], 1)

    def _trouver(self, piece: str):
        for chef, g in self.groupes.items():
            if piece in g["pieces"]:
                return chef, g
        raise LookupError(f"Pièce inconnue : {piece}")

    # -------- même interface que serveur.Systeme

    def zones(self) -> dict:
        return dict.fromkeys(self.volumes)

    def ips_connues(self) -> set[str]:
        return set()

    def etat(self) -> dict:
        groupes = []
        for chef in sorted(self.groupes):
            g = self.groupes[chef]
            self._avancer(g)
            titre, artiste, album, duree, teinte = MORCEAUX[g["piste"]] if g["piste"] is not None else ("", "", "", 0, None)
            vols = {p: self.volumes[p] for p in g["pieces"]}
            groupes.append({
                "id": chef, "pieces": sorted(g["pieces"]), "lecture": g["lecture"],
                "etat": "PLAYING" if g["lecture"] else ("PAUSED_PLAYBACK" if g["piste"] is not None else "STOPPED"),
                "titre": titre, "artiste": artiste, "album": album, "pochette": pochette(teinte),
                "position": int(self._position(g)), "duree": duree,
                "volume": round(sum(vols.values()) / len(vols)), "muet": g["muet"], "volumes": vols,
            })
        return {"groupes": groupes, "pieces": sorted(self.volumes), "volume_max": self.volume_max, "demo": True}

    def lecture(self, groupe: str):
        _, g = self._trouver(groupe)
        if g["piste"] is None:
            raise Refus("rien à lire")
        self._avancer(g)
        self._figer(g)
        g["lecture"] = not g["lecture"]

    def _sauter(self, groupe: str, sens: int):
        _, g = self._trouver(groupe)
        if not self._duree(g):
            raise Refus("pas de morceau suivant sur une radio")
        self._figer(g)
        if sens < 0 and g["pos"] > 3:  # comme Sonos : « précédent » revient d'abord au début
            g["pos"] = 0.0
            return
        g["piste"], g["pos"] = self._apres(g["piste"], sens), 0.0

    def suivant(self, groupe: str):
        self._sauter(groupe, 1)

    def precedent(self, groupe: str):
        self._sauter(groupe, -1)

    def volume(self, groupe: str, valeur, piece: str | None = None):
        v = max(0, min(self.volume_max, int(valeur)))
        if piece:
            self._trouver(piece)
            self.volumes[piece] = v
            return
        _, g = self._trouver(groupe)
        ecart = v - sum(self.volumes[p] for p in g["pieces"]) / len(g["pieces"])
        for p in g["pieces"]:
            self.volumes[p] = 0 if v == 0 else max(0, min(self.volume_max, round(self.volumes[p] + ecart)))

    def muet(self, groupe: str):
        _, g = self._trouver(groupe)
        g["muet"] = not g["muet"]

    def position(self, groupe: str, valeur):
        _, g = self._trouver(groupe)
        if not self._duree(g):
            raise Refus("pas de position sur une radio")
        self._figer(g)
        g["pos"] = float(max(0, min(self._duree(g) - 1, int(valeur))))

    def tout_pause(self):
        for g in self.groupes.values():
            self._figer(g)
            g["lecture"] = False

    def favoris(self, rafraichir=False) -> list[dict]:
        return [{"i": i, "type": f["type"], "titre": f["titre"],
                 "pochette": pochette(MORCEAUX[f["piste"]][4]) if f["piste"] is not None else None}
                for i, f in enumerate(FAVORIS)]

    def jouer(self, groupe: str, index: int):
        f = FAVORIS[index]
        _, g = self._trouver(groupe)
        g["piste"] = f["piste"] if f["piste"] is not None else self._apres(index % len(MORCEAUX), 1)
        g["pos"], g["depuis"], g["lecture"] = 0.0, time.time(), True

    def regrouper(self, groupe: str, pieces: list[str]):
        chef, g = self._trouver(groupe)
        voulues = set(pieces) | {chef}
        inconnues = voulues - set(self.volumes)
        if inconnues:
            raise LookupError(f"Pièce inconnue : {sorted(inconnues)[0]}")
        for p in sorted(self.volumes):
            if p in voulues and p not in g["pieces"]:
                self._retirer(p)
                g["pieces"].append(p)
            elif p not in voulues and p in g["pieces"] and p != chef:
                g["pieces"].remove(p)
                self._nouveau([p])

    def _retirer(self, piece: str):
        """Sort une pièce de son groupe ; si c'était le chef, la suivante reprend la musique."""
        chef, g = self._trouver(piece)
        g["pieces"].remove(piece)
        if chef == piece:
            del self.groupes[chef]
            if g["pieces"]:
                self.groupes[g["pieces"][0]] = g
