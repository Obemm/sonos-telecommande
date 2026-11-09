# US-02 — Installer la télécommande Sonos sur place

Statut : En cours · Créé le 2026-11-08 · Terminé le — · Ex-US-035 de ProjetMaison

## Histoire
En tant qu'utilisateur, je veux que la télécommande marche tous les jours sur mon téléphone,
sans le PC du propriétaire, afin de laisser tomber l'app Sonos S1.

## Critères d'acceptation
- [ ] Étant donné un redémarrage du téléphone (ou de la machine qui sert la page), quand il est fini,
      alors la télécommande remarche toute seule (démarrage automatique du serveur).
- [ ] Une enceinte débranchée ou injoignable ne bloque pas les autres pièces. Constat du 2026-11-08 :
      la salle de bain n'a pas répondu de 14 h 08 à 14 h 09 et toute la page était en erreur, car le
      serveur interroge toujours la même enceinte.
- [ ] Les IP des enceintes et du serveur sont réservées dans la box.
- [ ] La page est sur l'écran d'accueil du téléphone de l'utilisateur.
- [ ] Favori et regroupement essayés sur les vraies enceintes (repris d'US-01).
- [ ] L'utilisateur trouve ça plus simple que l'app (repris d'US-01).

## Tâches
- [x] Choisir où tourne le serveur. Essai retenu : le téléphone Android de l'utilisateur avec Termux
      (choix du propriétaire : « Android », 2026-11-08) ; Raspberry Pi si l'essai ne tient pas. Une PWA seule
      est impossible : les enceintes refusent les requêtes d'une page web (vérifié le 2026-11-08, voir `lecons.md`).
- [x] Paquet Termux : `termux/installer.sh`, `termux/servir.py`, option `--hote 127.0.0.1`, section du README.
- [ ] Installer sur le téléphone de l'utilisateur (le propriétaire, avec le PC sur le même Wi-Fi). Pas encore
      fait : sur place, ou à distance si on prépare une autre voie.
- [ ] Serveur tolérant à une enceinte injoignable : interroger une autre enceinte, garder les autres pièces.
- [ ] Réserver les IP dans la box.

## Tests
| # | Test | Comment | Résultat |
|---|---|---|---|
| 1 | Tests unitaires | 29 tests, dont le contenu de l'archive et le script Termux (adresse, fins de ligne Unix) | OK (2026-11-08) |
| 2 | Paquet servi par le Wi-Fi puis lancé comme sur le téléphone | téléchargé depuis 192.168.1.35:8090, décompressé, `serveur.py --demo --hote 127.0.0.1` : état et page OK, connexion refusée depuis le Wi-Fi, syntaxe bash OK, aucune fin de ligne Windows | OK (2026-11-08) |
| 3 | Installation dans Termux sur le téléphone de l'utilisateur | `installer.sh` jamais exécuté sous Android | À faire par le propriétaire |

## Validation du propriétaire
Date : — · Verdict : — · Remarques : —

## Rétro éclair
- Ce qui a surpris :
- Ce qu'on retient (→ `lecons.md` si durable) :
