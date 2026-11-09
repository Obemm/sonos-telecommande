"""Tests sans enceinte : pochettes, temps, erreurs et serveur HTTP branché sur les enceintes imaginaires.

Lancer : python -m unittest discover tests
"""
import io
import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import demo  # noqa: E402
import serveur  # noqa: E402

Z = SimpleNamespace(ip_address="192.168.1.12")


class Pochettes(unittest.TestCase):
    def test_sans_image(self):
        self.assertIsNone(serveur.art(Z, None))
        self.assertIsNone(serveur.art(Z, "http://192.168.1.12:1400unknown"))

    def test_image_enceinte_passe_par_le_relais(self):
        u = serveur.art(Z, "/getaa?s=1&u=x")
        self.assertTrue(u.startswith("/api/pochette?u=http%3A%2F%2F192.168.1.12%3A1400%2Fgetaa"))

    def test_image_publique_directe(self):
        u = "https://lh3.googleusercontent.com/abc=w544"
        self.assertEqual(serveur.art(Z, u), u)


class Temps(unittest.TestCase):
    def test_secondes(self):
        self.assertEqual(serveur.secondes("0:03:25"), 205)
        self.assertEqual(serveur.secondes("1:00:00"), 3600)
        for vide in ("NOT_IMPLEMENTED", "", None):  # radio, valeur absente
            self.assertEqual(serveur.secondes(vide), 0)

    def test_hms_aller_retour(self):
        self.assertEqual(serveur.hms(205), "0:03:25")
        for s in (0, 59, 61, 3599, 3725):
            self.assertEqual(serveur.secondes(serveur.hms(s)), s)


class Erreurs(unittest.TestCase):
    def code(self, e):
        recu = []
        faux = SimpleNamespace(_json=lambda code, data: recu.append((code, data)))
        with redirect_stderr(io.StringIO()):
            serveur.Gestion._erreur(faux, e)
        return recu[0] if recu else None

    def test_codes(self):
        self.assertEqual(self.code(KeyError("valeur"))[0], 400)
        self.assertEqual(self.code(IndexError())[0], 400)
        self.assertEqual(self.code(LookupError("Pièce inconnue : Garage")), (404, {"erreur": "Pièce inconnue : Garage"}))
        self.assertEqual(self.code(ValueError("x"))[0], 400)
        self.assertEqual(self.code(demo.Refus("radio"))[0], 409)
        self.assertEqual(self.code(TimeoutError())[0], 502)

    def test_navigateur_parti_rien_a_repondre(self):
        for e in (ConnectionAbortedError(), ConnectionResetError(), BrokenPipeError()):
            self.assertIsNone(self.code(e))


class Http(unittest.TestCase):
    """Le vrai serveur, sur un port libre, avec les enceintes imaginaires du mode démo."""

    @classmethod
    def setUpClass(cls):
        serveur.Gestion.web = serveur.ICI / "web"
        cls.srv = serveur.ThreadingHTTPServer(("127.0.0.1", 0), serveur.Gestion)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def setUp(self):
        serveur.Gestion.systeme = demo.SystemeDemo()  # état neuf à chaque test

    def appel(self, chemin, corps=None):
        if isinstance(corps, dict):
            corps = json.dumps(corps).encode()
        req = urllib.request.Request(self.base + chemin, data=corps, method="GET" if corps is None else "POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, r.headers, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers, e.read()

    def erreur(self, chemin, corps):
        code, _, brut = self.appel(chemin, corps)
        return code, json.loads(brut)["erreur"]

    def test_etat(self):
        code, h, brut = self.appel("/api/etat")
        self.assertEqual(code, 200)
        self.assertEqual(h["Cache-Control"], "no-store")
        e = json.loads(brut)
        self.assertTrue(e["demo"])
        self.assertEqual(len(e["pieces"]), 5)
        self.assertEqual([len(g["pieces"]) for g in e["groupes"]], [4, 1])

    def test_favoris(self):
        for chemin in ("/api/favoris", "/api/favoris?frais"):
            code, _, brut = self.appel(chemin)
            self.assertEqual(code, 200)
            self.assertEqual(len(json.loads(brut)), 12)

    def test_commande_et_volume_borne(self):
        code, _, _ = self.appel("/api/volume", {"groupe": "Salle de bain Rdc", "valeur": 99})
        self.assertEqual(code, 200)
        e = json.loads(self.appel("/api/etat")[2])
        self.assertEqual(e["groupes"][1]["volume"], 60)

    def test_pause_partout(self):
        self.assertEqual(self.appel("/api/pause-tout", {})[0], 200)
        e = json.loads(self.appel("/api/etat")[2])
        self.assertFalse(any(g["lecture"] for g in e["groupes"]))

    def test_erreurs_lisibles(self):
        self.assertEqual(self.erreur("/api/danser", {}), (404, "Action inconnue"))
        self.assertEqual(self.erreur("/api/lecture", {"groupe": "Garage"}), (404, "Pièce inconnue : Garage"))
        self.assertEqual(self.erreur("/api/volume", {"groupe": "Salon Rdc"}), (400, "Champ manquant : valeur"))
        self.assertEqual(self.erreur("/api/lecture", b"{pas du json")[0], 400)
        self.assertEqual(self.erreur("/api/lecture", b"[1, 2]")[0], 400)
        self.assertEqual(self.erreur("/api/jouer", {"groupe": "Salon Rdc", "index": 99}),
                         (400, "Favori introuvable : rechargez la liste"))

    def test_refus_des_enceintes(self):
        self.assertEqual(self.appel("/api/jouer", {"groupe": "Salle de bain Rdc", "index": 9})[0], 200)  # la radio
        code, message = self.erreur("/api/suivant", {"groupe": "Salle de bain Rdc"})
        self.assertEqual(code, 409)
        self.assertIn("radio", message)

    def test_fichiers(self):
        code, h, brut = self.appel("/")
        self.assertEqual(code, 200)
        self.assertTrue(h["Content-Type"].startswith("text/html"))
        self.assertTrue(self.appel("/manifest.json")[1]["Content-Type"].startswith("application/manifest+json"))
        self.assertTrue(self.appel("/icone.svg")[1]["Content-Type"].startswith("image/svg+xml"))
        for chemin in ("/%2e%2e/serveur.py", "/..%2fconfig.json", "/..%5Cserveur.py", "/absent.html"):
            code, _, brut = self.appel(chemin)  # hors de web/ ou absent : page d'accueil, jamais le fichier
            self.assertEqual(code, 200, chemin)
            self.assertIn(b"<!doctype html>", brut.lower(), chemin)

    def test_relais_reserve_aux_enceintes(self):
        for u in ("http://example.com/a.jpg", ""):
            self.assertEqual(self.appel("/api/pochette?u=" + u)[0], 403)


if __name__ == "__main__":
    unittest.main()
