"""Tests des enceintes imaginaires (--demo) : elles doivent se comporter comme les vraies.

Lancer : python -m unittest discover tests
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import demo  # noqa: E402

BIB, IMP, CUI, SDB, SAL = sorted(demo.VOLUMES)  # Bureau Bibliothèque, Bureau Imprimante, Cuisine, Salle de bain, Salon


class Demo(unittest.TestCase):
    def setUp(self):
        self.t = 1000.0  # horloge maîtrisée : le temps n'avance que quand le test le décide
        horloge = mock.patch.object(demo.time, "time", lambda: self.t)
        horloge.start()
        self.addCleanup(horloge.stop)
        self.s = demo.SystemeDemo()

    def groupe(self, chef):
        return next(g for g in self.s.etat()["groupes"] if g["id"] == chef)

    def test_etat_initial(self):
        e = self.s.etat()
        self.assertTrue(e["demo"])
        self.assertEqual(e["pieces"], [BIB, IMP, CUI, SDB, SAL])
        g = self.groupe(BIB)
        self.assertEqual((len(g["pieces"]), g["lecture"], g["position"], g["duree"]), (4, True, 42, 231))
        self.assertEqual(self.groupe(SDB)["etat"], "PAUSED_PLAYBACK")

    def test_le_temps_avance_seulement_en_lecture(self):
        self.t += 10
        self.assertEqual(self.groupe(BIB)["position"], 52)
        self.s.lecture(BIB)  # pause
        self.t += 100
        self.assertEqual(self.groupe(BIB)["position"], 52)

    def test_fin_de_morceau_passe_au_suivant(self):
        self.t += 231 - 42 + 5
        g = self.groupe(BIB)
        self.assertEqual((g["titre"], g["position"]), (demo.MORCEAUX[1][0], 5))

    def test_precedent_revient_au_debut_puis_recule(self):
        self.s.precedent(BIB)
        self.assertEqual((self.groupe(BIB)["titre"], self.groupe(BIB)["position"]), (demo.MORCEAUX[0][0], 0))
        self.s.precedent(BIB)  # au début du morceau : morceau d'avant, en sautant la radio
        self.assertEqual(self.groupe(BIB)["titre"], "Marée haute")

    def test_radio_refuse_suivant_et_position(self):
        self.s.jouer(SDB, 9)
        g = self.groupe(SDB)
        self.assertEqual((g["titre"], g["duree"], g["lecture"]), ("Radio Jazz du matin", 0, True))
        with self.assertRaises(demo.Refus):
            self.s.suivant(SDB)
        with self.assertRaises(demo.Refus):
            self.s.position(SDB, 30)

    def test_volume_borne_et_par_piece(self):
        self.s.volume(SDB, 99)
        self.assertEqual(self.groupe(SDB)["volume"], 60)
        self.s.volume(SDB, -5)
        self.assertEqual(self.groupe(SDB)["volume"], 0)
        self.s.volume(BIB, 30, piece=CUI)
        self.assertEqual(self.groupe(BIB)["volumes"][CUI], 30)

    def test_volume_du_groupe_garde_les_ecarts(self):
        avant = self.groupe(BIB)["volumes"]
        self.s.volume(BIB, 20)
        apres = self.groupe(BIB)
        self.assertEqual(apres["volume"], 20)
        self.assertGreater(apres["volumes"][SAL], apres["volumes"][IMP])  # le salon reste plus fort
        self.assertEqual(avant[SAL] - avant[IMP], apres["volumes"][SAL] - apres["volumes"][IMP])

    def test_piece_inconnue(self):
        with self.assertRaises(LookupError):
            self.s.lecture("Garage")
        with self.assertRaises(LookupError):
            self.s.regrouper(BIB, ["Garage"])

    def test_partout_puis_seulement_ici(self):
        self.s.regrouper(BIB, [BIB, IMP, CUI, SDB, SAL])
        self.assertEqual([len(g["pieces"]) for g in self.s.etat()["groupes"]], [5])
        self.s.regrouper(BIB, [])
        e = self.s.etat()
        self.assertEqual([len(g["pieces"]) for g in e["groupes"]], [1] * 5)
        self.assertTrue(self.groupe(BIB)["lecture"])  # la pièce principale garde la musique
        with self.assertRaises(demo.Refus):  # une pièce sortie n'a rien à lire
            self.s.lecture(CUI)

    def test_le_chef_part_la_musique_continue(self):
        self.s.regrouper(SDB, [BIB])  # la pièce principale du grand groupe rejoint la salle de bain
        reste = self.groupe(IMP)
        self.assertEqual((reste["pieces"], reste["lecture"]), ([IMP, CUI, SAL], True))
        self.assertEqual(self.groupe(SDB)["pieces"], [BIB, SDB])

    def test_pause_partout(self):
        self.s.tout_pause()
        self.assertFalse(any(g["lecture"] for g in self.s.etat()["groupes"]))

    def test_favoris_et_listes(self):
        f = self.s.favoris()
        self.assertEqual(len(f), 12)
        self.assertEqual(sum(x["type"] == "liste" for x in f), 2)
        self.assertIsNone(next(x for x in f if x["titre"] == "Night Drive")["pochette"])  # repli sans image
        self.s.jouer(SDB, 10)  # une liste, dans la salle de bain qui était en pause
        g = self.groupe(SDB)
        self.assertEqual((g["lecture"], g["position"]), (True, 0))


if __name__ == "__main__":
    unittest.main()
