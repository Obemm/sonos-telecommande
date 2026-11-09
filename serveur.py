"""Télécommande Sonos simplifiée : petit serveur web local (US-01).

Pilote les enceintes Sonos (S1 ou S2) par leur API locale UPnP, via SoCo.
Sert une page mobile (web/) et une API JSON. Aucun compte, aucun cloud.

Lancer :  python serveur.py              (config.json à côté)
          python serveur.py --port 8080
          python serveur.py --demo       (enceintes imaginaires : essayer l'interface sans bruit)
          python serveur.py --demo --port 8081 --web <dossier>   (retravailler une copie de la page)
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
import warnings
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ICI = Path(__file__).resolve().parent
VERROU = threading.Lock()  # SoCo n'aime pas les ordres simultanés sur un même groupe


def secondes(texte: str | None) -> int:
    """« 0:03:25 » → 205 ; 0 pour une radio ou une valeur absente (« NOT_IMPLEMENTED »)."""
    m = re.fullmatch(r"(\d+):(\d{1,2}):(\d{1,2})", texte or "")
    return int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) if m else 0


def hms(s: int) -> str:
    return f"{s // 3600}:{s // 60 % 60:02}:{s % 60:02}"


def art(z, url: str | None) -> str | None:
    """Adresse de pochette pour la page : image d'enceinte via notre relais, image publique telle quelle."""
    if not url or url.endswith("unknown"):  # Sonos écrit « unknown » quand il n'a pas d'image
        return None
    if url.startswith("/"):
        url = f"http://{z.ip_address}:1400{url}"
    if urllib.parse.urlparse(url).port != 1400:  # image publique (YouTube Music…) : le navigateur la charge
        return url
    return "/api/pochette?u=" + urllib.parse.quote(url, safe="")


# ---------------------------------------------------------------- enceintes

class Systeme:
    """Les vraies enceintes : adresses fixes de config.json, sinon découverte réseau."""

    def __init__(self, ips: list[str], volume_max: int = 60):
        warnings.filterwarnings("ignore")  # avertissements requests/urllib3 sans intérêt ici
        import soco  # importé ici : le mode démo et les tests s'en passent
        soco.config.REQUEST_TIMEOUT = 5  # une enceinte débranchée ne doit pas figer la page 20 s
        self.soco = soco
        self.ips = ips
        self.volume_max = volume_max
        self._zones: dict = {}
        self._favoris: list = []
        self._favoris_date = 0.0

    def zones(self) -> dict:
        """Pièces visibles, par nom (le Sub et les enceintes appairées sont invisibles)."""
        if not self._zones:
            trouvees = [self.soco.SoCo(ip) for ip in self.ips] if self.ips else list(self.soco.discover(timeout=3) or [])
            for z in trouvees:
                try:
                    if z.is_visible:
                        self._zones[z.player_name] = z
                except Exception:  # enceinte débranchée : on l'ignore
                    pass
        return self._zones

    def zone(self, nom: str):
        z = self.zones().get(nom)
        if z is None:
            raise LookupError(f"Pièce inconnue : {nom}")
        return z

    def _chef(self, piece: str):
        """Le coordinateur du groupe dont fait partie la pièce : c'est lui qui reçoit les ordres."""
        return self.zone(piece).group.coordinator

    def une_zone(self):
        return next(iter(self.zones().values()))

    def ips_connues(self) -> set[str]:
        return set(self.ips) | {z.ip_address for z in self.zones().values()}

    # -------- état

    def etat(self) -> dict:
        groupes = []
        for g in sorted(self.une_zone().all_groups, key=lambda g: g.coordinator.player_name):
            c = g.coordinator
            membres = [m for m in g.members if m.is_visible]
            if not membres:
                continue
            transport = c.get_current_transport_info().get("current_transport_state", "")
            piste = c.get_current_track_info()
            titre = piste.get("title") or ""
            if not titre:  # radio : le titre est souvent dans les métadonnées du flux
                titre = c.get_current_media_info().get("channel") or ""
            groupes.append({
                "id": c.player_name,
                "pieces": sorted(m.player_name for m in membres),
                "lecture": transport == "PLAYING",
                "etat": transport,
                "titre": titre,
                "artiste": piste.get("artist") or "",
                "album": piste.get("album") or "",
                "pochette": art(c, piste.get("album_art")),
                "position": secondes(piste.get("position")),
                "duree": secondes(piste.get("duration")),
                "volume": g.volume,
                "muet": g.mute,
                "volumes": {m.player_name: m.volume for m in membres},
            })
        return {"groupes": groupes, "pieces": sorted(self.zones()), "volume_max": self.volume_max}

    # -------- commandes

    def lecture(self, groupe: str):
        c = self._chef(groupe)
        if c.get_current_transport_info().get("current_transport_state") == "PLAYING":
            c.pause()
        else:
            c.play()

    def suivant(self, groupe: str):
        self._chef(groupe).next()

    def precedent(self, groupe: str):
        self._chef(groupe).previous()

    def volume(self, groupe: str, valeur, piece: str | None = None):
        """Volume de tout le groupe, ou d'une seule pièce ; borné par volume_max (config.json)."""
        v = max(0, min(self.volume_max, int(valeur)))
        if piece:
            self.zone(piece).volume = v
        else:
            self._chef(groupe).group.volume = v

    def muet(self, groupe: str):
        g = self._chef(groupe).group
        g.mute = not g.mute

    def position(self, groupe: str, valeur):
        self._chef(groupe).seek(hms(max(0, int(valeur))))

    def tout_pause(self):
        for g in self.une_zone().all_groups:
            c = g.coordinator
            if c.get_current_transport_info().get("current_transport_state") == "PLAYING":
                c.pause()

    # -------- favoris et listes

    def _liste(self, rafraichir=False) -> list:
        if rafraichir or time.time() - self._favoris_date > 300:
            z = self.une_zone()
            liste = []
            for f in z.music_library.get_sonos_favorites(full_album_art_uri=True):
                liste.append({"type": "favori", "titre": f.title, "objet": f,
                              "pochette": art(z, getattr(f, "album_art_uri", None))})
            for p in z.get_sonos_playlists():
                liste.append({"type": "liste", "titre": p.title, "objet": p, "pochette": None})
            self._favoris, self._favoris_date = liste, time.time()
        return self._favoris

    def favoris(self, rafraichir=False) -> list[dict]:
        return [{"i": i, "type": f["type"], "titre": f["titre"], "pochette": f["pochette"]}
                for i, f in enumerate(self._liste(rafraichir))]

    def jouer(self, groupe: str, index: int):
        f = self._liste()[index]
        c = self._chef(groupe)
        objet = f["objet"]
        if f["type"] == "liste":
            c.clear_queue(); c.add_to_queue(objet); c.play_from_queue(0)
            return
        ref = objet.reference
        uri = ref.get_uri() if ref.resources else ""
        # Radios et flux : lecture directe. Titres, albums, listes : via la file d'attente.
        if uri.startswith(("x-sonosapi-stream:", "x-sonosapi-radio:", "x-rincon-mp3radio:", "aac:", "hls-radio:")):
            c.play_uri(uri, meta=objet.resource_meta_data, title=f["titre"])
        else:
            c.clear_queue(); c.add_to_queue(ref); c.play_from_queue(0)

    # -------- regroupement

    def regrouper(self, groupe: str, pieces: list[str]):
        """Fait jouer exactement `pieces` avec le groupe de `groupe` (son coordinateur reste le chef)."""
        chef = self._chef(groupe)
        voulues = set(pieces) | {chef.player_name}
        for p in voulues:
            self.zone(p)  # pièce inconnue : erreur claire avant de toucher aux groupes
        for nom, z in self.zones().items():
            dans = z.group.coordinator.uid == chef.uid
            if nom in voulues and not dans:
                z.join(chef)
            elif nom not in voulues and dans and z.uid != chef.uid:
                z.unjoin()


# ---------------------------------------------------------------- HTTP

ACTIONS = {
    "lecture": lambda s, d: s.lecture(d["groupe"]),
    "suivant": lambda s, d: s.suivant(d["groupe"]),
    "precedent": lambda s, d: s.precedent(d["groupe"]),
    "volume": lambda s, d: s.volume(d["groupe"], d["valeur"], d.get("piece")),
    "muet": lambda s, d: s.muet(d["groupe"]),
    "position": lambda s, d: s.position(d["groupe"], d["secondes"]),
    "jouer": lambda s, d: s.jouer(d["groupe"], int(d["index"])),
    "pieces": lambda s, d: s.regrouper(d["groupe"], list(d["pieces"])),
    "pause-tout": lambda s, d: s.tout_pause(),
}


class Gestion(BaseHTTPRequestHandler):
    systeme = None
    web = ICI / "web"

    def log_message(self, fmt, *args):  # journal discret : seulement les ordres et les erreurs
        ligne = fmt % args
        if not any(x in ligne for x in ("/api/etat", "/api/favoris", "/api/pochette", "GET / ", ".svg", ".json")):
            sys.stderr.write("%s %s\n" % (time.strftime("%H:%M:%S"), ligne))

    def _json(self, code: int, data):
        corps = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corps)

    def _erreur(self, e: Exception):
        if isinstance(e, ConnectionError):  # navigateur parti en cours de route (écran verrouillé) : personne à qui répondre
            return None
        if isinstance(e, KeyError):
            return self._json(400, {"erreur": f"Champ manquant : {e.args[0]}"})
        if isinstance(e, IndexError):
            return self._json(400, {"erreur": "Favori introuvable : rechargez la liste"})
        if isinstance(e, LookupError):
            return self._json(404, {"erreur": str(e)})
        if isinstance(e, (ValueError, TypeError)):
            return self._json(400, {"erreur": f"Requête invalide : {e}"})
        if type(e).__name__ in ("SoCoUPnPException", "Refus"):  # les enceintes ont répondu « non »
            return self._json(409, {"erreur": "Les enceintes refusent cette commande ici "
                                              "(par exemple « suivant » sur une radio)"})
        sys.stderr.write(f"{time.strftime('%H:%M:%S')} enceintes : {e!r}\n")
        return self._json(502, {"erreur": "Les enceintes n'ont pas répondu"})

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        try:
            if url.path == "/api/etat":
                with VERROU:
                    return self._json(200, self.systeme.etat())
            if url.path == "/api/favoris":
                frais = "frais" in urllib.parse.parse_qs(url.query, keep_blank_values=True)
                with VERROU:
                    return self._json(200, self.systeme.favoris(frais))
            if url.path == "/api/pochette":
                return self._pochette(urllib.parse.parse_qs(url.query).get("u", [""])[0])
            return self._fichier(url.path)
        except Exception as e:
            return self._erreur(e)

    def do_POST(self):
        faire = ACTIONS.get(urllib.parse.urlparse(self.path).path.removeprefix("/api/"))
        if faire is None:
            return self._json(404, {"erreur": "Action inconnue"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            d = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(d, dict):
                raise ValueError("objet JSON attendu")
            with VERROU:
                faire(self.systeme, d)
            return self._json(200, {"ok": True})
        except Exception as e:
            return self._erreur(e)

    def _pochette(self, u: str):
        hote = urllib.parse.urlparse(u).hostname
        if hote not in self.systeme.ips_connues():  # relais réservé aux enceintes
            return self._json(403, {"erreur": "hôte refusé"})
        try:
            with urllib.request.urlopen(u, timeout=5) as r:
                corps, typ = r.read(), r.headers.get("Content-Type", "image/jpeg")
        except (OSError, ValueError):
            self.send_response(404); self.end_headers(); return
        self.send_response(200)
        self.send_header("Content-Type", typ)
        self.send_header("Cache-Control", "max-age=86400")
        self.end_headers()
        self.wfile.write(corps)

    def _fichier(self, chemin: str):
        f = (self.web / urllib.parse.unquote(chemin).lstrip("/")).resolve()
        if self.web not in f.parents or not f.is_file():  # hors de web/ ou absent : page d'accueil
            f = self.web / "index.html"
        typ = mimetypes.guess_type(f.name)[0] or "text/plain"
        if f.suffix == ".json":
            typ = "application/manifest+json" if f.name == "manifest.json" else typ
        self.send_response(200)
        self.send_header("Content-Type", typ + "; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(f.read_bytes())


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--config", default=ICI / "config.json", type=Path)
    p.add_argument("--port", type=int)
    p.add_argument("--web", type=Path, default=ICI / "web", help="dossier de la page (web/ par défaut)")
    p.add_argument("--demo", action="store_true", help="enceintes imaginaires, aucun son")
    p.add_argument("--hote", default="0.0.0.0",
                   help="adresse d'écoute ; 127.0.0.1 = cet appareil seulement (téléphone avec Termux)")
    a = p.parse_args()
    conf = json.loads(a.config.read_text(encoding="utf-8")) if a.config.is_file() else {}
    if a.demo:
        from demo import SystemeDemo
        systeme = SystemeDemo()
        print("Mode démo : enceintes imaginaires, aucun son")
    else:
        systeme = Systeme(conf.get("enceintes", []), conf.get("volume_max", 60))
        print("Pièces :", ", ".join(sorted(systeme.zones())) or "aucune trouvée")
    Gestion.systeme, Gestion.web = systeme, a.web.resolve()
    port = a.port or conf.get("port", 8080)
    ou = "localhost" if a.hote == "127.0.0.1" else "<adresse-de-cette-machine>"
    print(f"Télécommande sur http://{ou}:{port}/", flush=True)
    ThreadingHTTPServer((a.hote, port), Gestion).serve_forever()


if __name__ == "__main__":
    main()
