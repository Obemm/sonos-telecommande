"""Paquet pour téléphone Android (Termux) : contenu de l'archive et script d'installation.

Lancer : python -m unittest discover tests
"""
import io
import sys
import tarfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "termux"))
import servir  # noqa: E402


class Paquet(unittest.TestCase):
    def test_archive_complete_sans_tests_ni_caches(self):
        with tarfile.open(fileobj=io.BytesIO(servir.archive())) as tar:
            noms = tar.getnames()
        self.assertEqual(sorted(noms), sorted("sonos-telecommande/" + f for f in servir.FICHIERS))
        self.assertFalse(any("tests" in n or "__pycache__" in n for n in noms))

    def test_installeur_adresse_et_fins_de_ligne(self):
        texte = servir.installeur("http://192.168.1.35:8090").decode("utf-8")
        self.assertTrue(texte.startswith("#!/data/data/com.termux/files/usr/bin/bash\n"))
        self.assertIn('SOURCE="http://192.168.1.35:8090"', texte)
        self.assertNotIn("@SOURCE@", texte)
        self.assertNotIn("\r", texte)  # bash sous Android refuse les retours chariot
        self.assertIn("--hote 127.0.0.1", texte)  # sur le téléphone, le serveur n'écoute que lui-même


if __name__ == "__main__":
    unittest.main()
