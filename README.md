# sonos-telecommande

Type : service web (Python 3.12, SoCo)
Domaine : un système Sonos S1 de 5 pièces. Suivi : `backlog/BOARD.md`
Où il tourne : prototype sur le PC du propriétaire ; cible : le téléphone Android de l'utilisateur
(Termux), sinon un Raspberry Pi sur place
Dépôt autonome depuis le 2026-11-09 (auparavant `tools/sonos-telecommande` dans ProjetMaison)

## Ce qu'il fait
Une page web pour téléphone qui remplace l'app Sonos au quotidien, en trois onglets :
- **Lecture** : la pièce choisie, la pochette en grand, le morceau, la barre de progression
  (déplaçable ; « En direct » pour une radio), lecture et pause, précédent et suivant, volume,
  coupure du son, et « Joue dans » qui ouvre la feuille des pièces : « Partout », « Seulement ici »,
  cocher les pièces qui jouent ensemble, volume de chaque pièce ;
- **Favoris** : les listes de lecture Sonos puis les favoris (titres, albums, radios), avec
  recherche (accents ignorés) ; un favori sans image reçoit une pochette générée (couleur et initiales) ;
- **Maison** : une carte par groupe de pièces, avec lecture et volume, et « Tout mettre en pause ».

La couleur de la page vient de la pochette en cours. Thème clair ou sombre selon le téléphone.
Sur tablette en paysage ou sur ordinateur, le lecteur et les favoris sont côte à côte.
Un mini-lecteur reste en bas des onglets Favoris et Maison.

Il parle aux enceintes par leur API locale (port 1400). Il fonctionne donc avec ce **système S1**,
que la nouvelle app Sonos ne gère plus : deux Play:5 de 1re génération bloquent la
migration vers S2. Aucun compte et aucun cloud ne sont nécessaires.

## Installer (une fois)
```bash
python -m pip install soco
```

## Lancer
```bash
python serveur.py
```
Puis, sur un téléphone connecté au même Wi-Fi, ouvrir `http://<adresse de la machine>:8080`.
Pour l'installer comme une app : menu du navigateur → « Ajouter à l'écran d'accueil ».

**Mode démo** : enceintes imaginaires, aucun son, les morceaux avancent avec l'horloge. Pour
essayer ou retoucher l'interface sans déranger la maison (SoCo n'est même pas nécessaire) :
```bash
python serveur.py --demo --port 8081
```
`--web <dossier>` sert une autre copie de la page : on peut retravailler une copie pendant que
la vraie page sert.

## Sur un téléphone Android, sans autre machine (Termux)
Une PWA seule ne peut pas parler aux Sonos (voir `lecons.md`). Le serveur tourne alors sur le
téléphone lui-même, dans l'appli Termux, et n'écoute que lui (`--hote 127.0.0.1`).
1. Sur le téléphone : installer **Termux** et **Termux:Boot** depuis F-Droid (les deux de la même
   source), puis ouvrir Termux:Boot une fois.
2. Sur le PC, branché au même Wi-Fi, à la racine du dépôt : `python termux/servir.py`.
3. Dans Termux, taper la commande affichée par le PC :
   `curl -fsSLO http://<adresse du PC>:8090/installer.sh && bash installer.sh`.
   Le script met Termux à jour, installe Python et lxml, la télécommande, SoCo et le lancement automatique.
4. Dans Chrome : `http://localhost:8080`, puis menu ⋮ → « Ajouter à l'écran d'accueil ».
5. Réglages → Applications → Termux → Batterie → « Non restreinte », sinon Android endort le serveur.

Relancer à la main : commande `sonos` dans Termux. Journal : `~/sonos-telecommande/journal.txt`.
Mettre à jour : refaire les étapes 2 et 3. Limites : un seul téléphone en profite, et Android peut
quand même couper Termux.

Après une modification de `serveur.py` ou `demo.py`, **redémarrer** le serveur. Les fichiers de
`web/` sont relus à chaque chargement de page.

## Configurer
`config.json` :
- `port` : 8080 par défaut ;
- `volume_max` : plafond de volume (60 par défaut, sur 100) appliqué à tout ce qu'envoie la page ;
- `enceintes` : adresses IP des enceintes, une par pièce suffit (le Sub et les enceintes
  appairées sont trouvés tout seuls). Si la liste est vide, le serveur cherche les enceintes
  sur le réseau, mais la découverte échoue souvent sous Windows (pare-feu).
  → **Réserver ces adresses dans la box** (DHCP statique), sinon elles peuvent changer.

Relevé du 2026-11-08 : Salle de bain .12 (Play:3), Cuisine .14 (Play:1),
Bureau Imprimante .23 (Play:5 gen 1), Salon .26 (Play:5 gen 1) + .24 (Sub),
Bureau Bibliothèque .27 (Playbar). Toutes en S1 11.16.1. Service musical : YouTube Music.

## API
| Méthode | Chemin | Corps |
|---|---|---|
| GET | `/api/etat` | groupes : pièces, morceau, position et durée (s), volumes |
| GET | `/api/favoris[?frais]` | favoris et listes Sonos (cache 5 min, `frais` le vide) |
| GET | `/api/pochette?u=` | relais d'images, réservé aux adresses des enceintes |
| POST | `/api/lecture`, `/api/suivant`, `/api/precedent`, `/api/muet` | `{"groupe": "<pièce>"}` |
| POST | `/api/volume` | `{"groupe", "valeur", "piece"?}` |
| POST | `/api/position` | `{"groupe", "secondes"}` |
| POST | `/api/jouer` | `{"groupe", "index"}` |
| POST | `/api/pieces` | `{"groupe", "pieces": [...]}` |
| POST | `/api/pause-tout` | `{}` |

Erreurs, toujours `{"erreur": "<phrase lisible>"}` : 400 requête invalide ou champ manquant,
404 pièce ou action inconnue, 409 les enceintes refusent (« suivant » sur une radio),
502 les enceintes n'ont pas répondu.

## Tests
```bash
python -m unittest discover tests
```
29 tests sans enceinte : le mode démo, le vrai serveur HTTP branché sur le mode démo, et le paquet
Termux. Les essais sur les vraies enceintes sont consignés dans les stories (`backlog/stories/`).

## Sécurité
Pas de mot de passe : à réserver au réseau local, **ne jamais ouvrir le port sur Internet**.
Le relais d'images (`/api/pochette`) n'accepte que les adresses des enceintes.
