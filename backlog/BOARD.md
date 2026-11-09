# Tableau de bord — télécommande Sonos

Mis à jour : 2026-11-09 (dépôt autonome sans donnée personnelle, sorti de ProjetMaison : US-03 à valider ;
US-02 en cours, installation sur place en attente ; le 08 : US-01 prototype terminé et validé, design refait).

## Objectif
L'utilisateur n'est pas satisfait de l'app Sonos. Lui donner une télécommande simple sur son
téléphone pour ses 5 pièces. On saura que c'est atteint quand il l'utilise au quotidien à la place de l'app.

## Périmètre
- Dedans : télécommande web locale (S1) ; hébergement sur place (essai : le téléphone Android de l'utilisateur
  avec Termux, sinon un Raspberry Pi) ; réservation des IP dans la box.
- Dehors : migration vers S2 ou achat d'enceintes.

## Risques / dépendances
- Système S1 (Play:5 gen 1) : pas d'AirPlay, pas de nouvelle app ; l'app S1 peut disparaître un jour des
  magasins d'applications.
- Il faut une machine allumée en permanence sur place (aucune trouvée sur le réseau le 2026-11-08) :
  d'où l'essai sur le téléphone de l'utilisateur, qu'Android peut endormir.

## Stories

### En cours
| Story | Titre |
|---|---|
| [US-02](stories/US-02-installer-telecommande-sur-place.md) | Télécommande sur le téléphone Android de l'utilisateur (Termux) : paquet prêt et testé sur le PC, installation sur place à faire |

### À valider (par le propriétaire)
| Story | Titre |
|---|---|
| [US-03](stories/US-03-depot-autonome.md) | Dépôt autonome, sorti de ProjetMaison (GitHub privé, sans donnée personnelle) |

### À faire
_(aucune)_

### Terminé
| Story | Titre | Date |
|---|---|---|
| [US-01](stories/US-01-prototype-telecommande-sonos.md) | Prototype de télécommande web, design refait (lecture, muet, volume essayés ; favori et regroupement → US-02) | 2026-11-08 |

## Prochaines étapes
1. Choisir comment installer : à distance (paquet envoyé, ou Raspberry Pi prêt à brancher) ou sur place (US-02).
2. Rendre le serveur tolérant à une enceinte injoignable (US-02).
3. Réserver les IP des enceintes dans la box (US-02).

## Notes
- Cartographie du réseau le 2026-11-08 : 6 Sonos, détail dans `README.md` § Configurer.
- Pistes notées : tablette Galaxy Tab A9 en télécommande murale, cartes NFC, Sonora en solution toute faite.
- Origine : EPIC-12 de ProjetMaison (US-034 → US-01, US-035 → US-02), sorti le 2026-11-09 (ADR-008 de ProjetMaison).

---
Prochain identifiant libre : **US-04**.
