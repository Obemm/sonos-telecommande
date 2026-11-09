# US-01 — Prototype de télécommande web Sonos

Statut : Terminé · Créé le 2026-11-08 · Terminé le 2026-11-08 · Ex-US-034 de ProjetMaison

## Histoire
En tant qu'utilisateur, je veux piloter mes Sonos depuis une page simple sur mon téléphone,
afin de ne plus dépendre de l'app Sonos S1 qui ne me convient pas.

## Critères d'acceptation
- [x] Étant donné le réseau de la maison, quand j'ouvre la page, alors je vois ses 5 pièces et ce qui joue dans chacune.
- [x] Lecture/pause, précédent/suivant, volume du groupe et par pièce, coupure du son.
- [x] Choisir les pièces qui jouent ensemble, avec « Partout » et « Seulement ici ».
- [x] Lancer un favori ou une liste Sonos depuis une grille avec recherche.
- [x] Lisible sur téléphone (390 px), thème clair et sombre, ajout à l'écran d'accueil.
- [x] Pas de défaut d'affichage du petit téléphone (360 px) à l'ordinateur, design au goût du jour
      (refonte demandée par le propriétaire le 2026-11-08).
- [x] Essais sonores de base faits par le propriétaire : lecture/pause, muet, volume (journal du serveur, 12 h 49 – 12 h 51).
- [ ] Reporté dans US-02 : favori et regroupement sur les vraies enceintes (pas vus dans le journal).
- [ ] Reporté dans US-02 : l'utilisateur trouve ça plus simple que l'app (il n'a pas encore pu essayer).

## Tâches
- [x] Serveur Python (SoCo) + page web, README, leçons, tests (alors dans `tools/sonos-telecommande` de ProjetMaison).
- [x] Refonte de la page, mode `--demo` (enceintes imaginaires), 27 tests (2026-11-08).
- [ ] Reporté dans US-02 : réserver les IP des Sonos dans la box.
- [x] Hébergement durable sur place : story ouverte, US-02.

## Refonte de l'affichage (2026-11-08)
Demande du propriétaire : « il y a des défauts d'affichage, fais une vérification et améliore le design ».

Défauts relevés sur la première version :
1. Rangée des pièces coupée sans indice de défilement ; contour orange inexpliqué sur les pièces groupées.
2. Volumes par pièce sur deux lignes, curseurs décalés ; curseurs natifs trop petits pour le doigt.
3. « Seulement Bureau Bibliothèque », « Joue dans » et les puces « Où ça joue » passent à la ligne n'importe comment.
4. 23 favoris sur 37 sans image : un mur de ♪ gris ; pochette du lecteur vide quand l'image échoue.
5. Favoris loin en bas de page, pas de mini-lecteur, ni progression ni temps du morceau.
6. Chargements en texte brut, émojis au lieu d'icônes, colonne étroite (560 px) sur tablette.

Nouvelle page :
- trois onglets : Lecture, Favoris, Maison ;
- pochette en grand sur fond flouté, couleur d'accent tirée de la pochette ;
- barre de progression déplaçable (« En direct » pour une radio) et mini-lecteur ;
- feuille « Où ça joue » : Partout, Seulement ici, volume par pièce ; « Tout mettre en pause » ;
- pochettes générées (couleur + initiales) pour les favoris sans image, recherche sans accents ;
- thèmes clair et sombre ; lecteur et favoris côte à côte sur tablette et ordinateur.

## Tests
| # | Test | Comment | Résultat |
|---|---|---|---|
| 1 | Tests unitaires | `python -m unittest discover tests` | OK, 4 tests (2026-11-08) ; refonte : OK, 27 tests (mode démo + serveur HTTP) |
| 2 | `/api/etat` sur les vraies enceintes | 2 groupes, 5 pièces, morceau en pause, volumes | OK |
| 3 | `/api/favoris` | 37 favoris + 2 listes Sonos ; pochettes : 14 images, les autres en repli ♪ | OK |
| 4 | Relais d'images | image d'enceinte servie, hôte externe refusé (403) | OK |
| 5 | Volume (même valeur) et muet aller-retour, salle de bain à l'arrêt | aucun son, état revenu à l'identique | OK |
| 6 | Pièce inconnue, action inconnue | erreur claire (502/404) | OK |
| 7 | Affichage 390 px dans le navigateur | pas de défilement horizontal, console sans erreur | OK |
| 8 | Essais sonores sur les vraies enceintes, par le propriétaire | lecture/pause envoyée 4 fois depuis la page, avec muet et volume, réponses 200 (journal, 12 h 49 – 12 h 51) ; favori, regroupement, déplacement dans le morceau et pause partout pas vus dans le journal | OK pour lecture, muet, volume ; le reste → US-02 |
| 9 | Refonte en mode démo : lecture, suivant, favori, radio, regroupement, volume au doigt, recherche, déplacement dans le morceau | 360×640, 390×844, 600×960, 820×1180, 1000×600, 1280×800 ; clair et sombre ; console sans erreur | OK |
| 10 | Défauts trouvés pendant cette vérification | pastilles sur 3 lignes qui sortaient le lecteur de l'écran (1280×800), page trop haute de 25 px (360×640), bandeau « hors ligne » et messages sur 3 lignes, pochettes vides toutes roses | Corrigés, revérifiés |
| 11 | Bandeau hors ligne, fermeture de la feuille (Échap, clic à côté), focus clavier visible, erreur 409 lisible | coupure simulée dans la page | OK |
| 12 | Nouvelle page sur les vraies enceintes, en lecture seule | 2 groupes, morceau en pause à 0:53 sur 4:51, vraie pochette et couleur tirée d'elle, 39 favoris, aucune image cassée | OK |

## Validation du propriétaire
Date : 2026-11-08 · Verdict : validée (« Oui, valide US-034 », ancien numéro) · Remarques : favori et regroupement
pas vus dans le journal du serveur ; l'utilisateur n'a pas encore essayé, faute de serveur sur place : les deux sont
repris dans US-02.

## Rétro éclair
- Ce qui a surpris : le système est en S1 à cause de deux Play:5 de 1re génération ; la musique vient de YouTube Music.
  Pendant la refonte, chaque taille d'écran a révélé un défaut différent.
- Ce qu'on retient : voir `lecons.md`.
