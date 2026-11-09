# US-03 — Dépôt autonome, sorti de ProjetMaison

Statut : Terminé · Créé le 2026-11-09 · Terminé le 2026-11-10

## Histoire
En tant que propriétaire, je veux la télécommande dans son propre dépôt Git, avec son suivi, afin de la
faire vivre comme un projet autonome, à part de mon assistant personnel (ProjetMaison).

## Critères d'acceptation
- [x] Dépôt GitHub **privé** `Obemm/sonos-telecommande`, dossier local `C:\Users\obemm\Projets Dev\sonos-telecommande`
      (choix du propriétaire : « GitHub privé », 2026-11-09).
- [x] Code identique à celui de ProjetMaison, hors caches ; tests verts dans le nouveau dossier.
- [x] Le suivi part avec le code (choix du propriétaire : « Part avec le code ») : objectif, périmètre, risques et notes
      de l'épic dans `backlog/BOARD.md` ; stories renumérotées (US-034 → US-01, US-035 → US-02).
- [x] Rien de privé dans Git au-delà des IP locales des enceintes, acceptées puisque le dépôt est privé.
- [x] Aucune donnée personnelle, ni dans les fichiers ni dans l'historique : ni lien de parenté, ni prénom,
      ni date de passage sur place, ni équipement de la maison hors sujet ; adresse e-mail GitHub masquée
      dans les commits (demande du propriétaire, 2026-11-09 ; les IP restent, choix du même jour).
- [x] ProjetMaison ne contient plus l'outil ni ses stories ; il garde un renvoi (EPIC-12 « Déplacé », ADR-008)
      et son backlog reste cohérent.

## Tâches
- [x] Copier l'outil sans caches dans le nouveau dossier.
- [x] Suivi : `backlog/BOARD.md`, trois stories, modèle de story.
- [x] Chemins et numéros adaptés (README, docstrings, script Termux) ; `CLAUDE.md`, `.gitignore`, `.gitattributes`,
      `.claude/launch.json` (serveur réel et mode démo).
- [x] Premier commit, création du dépôt privé sur GitHub, push.
- [x] ProjetMaison : outil, stories et lancements retirés ; EPIC-12 « Déplacé » avec renvoi ; ADR-008 ; `check.py`.
      Commité là-bas le 2026-11-09 (094ada6), poussé le même soir.
- [x] Données personnelles retirées : textes reformulés (« le propriétaire », « l'utilisateur », « sur place »),
      US-02 renommée, adresse e-mail GitHub masquée dans la configuration Git du dépôt, règle et leçon écrites ;
      historique réécrit en un seul commit, puis push forcé.

## Tests
| # | Test | Comment | Résultat |
|---|---|---|---|
| 1 | Copie conforme | `diff -rq` entre l'outil de ProjetMaison et le nouveau dossier, hors caches | OK, aucune différence (2026-11-09) |
| 2 | Tests unitaires dans le nouveau dossier | `python -m unittest discover tests` | OK, 29 tests (2026-11-09) |
| 3 | Rien de privé dans le commit initial (avant réécriture) | contrôle bloquant de `CLAUDE.md` sur `git diff --cached` ; motif essayé d'abord sur 9 exemples à attraper (un par type de donnée cherché) et 3 lignes saines ; liste des fichiers indexés | OK : 0 ligne ; 9 exemples sur 9 attrapés, 0 fausse alerte ; 22 fichiers, ni cache ni journal. Premier passage bloqué par le motif lui-même dans `CLAUDE.md`, corrigé |
| 4 | Dépôt sur GitHub | `gh repo view` : privé ; le commit distant est le commit local | OK : PRIVATE, branche `main`, distant = local, 22 fichiers (2026-11-09) |
| 5 | ProjetMaison après retrait | avant : `diff -rq` entre l'outil et ce dépôt ; après : `python backlog/check.py` et recherche de « sonos » | OK : seuls les 4 fichiers adaptés différaient, aucun fichier absent d'ici ; « Backlog cohérent : 12 épics, 30 stories » ; « sonos » ne reste que dans le renvoi (BOARD, EPIC-12, ADR-008, `session-context.md`) |
| 6 | Aucune donnée personnelle | recherche dans tous les fichiers suivis (lien de parenté, prénom, ancienne adresse e-mail, marque de chaudière, nom de la box) ; identité Git du dépôt ; contrôle bloquant sur tout le contenu du commit réécrit ; tests | OK : 0 ligne trouvée ; adresse e-mail GitHub masquée ; contrôle bloquant OK ; 29 tests (2026-11-09) |
| 7 | Ce que sert GitHub après le push forcé | clone neuf du dépôt et API GitHub : commits, fichiers, recherche des mêmes données, e-mail affiché, visibilité | OK : 1 commit (3b6fa51), 22 fichiers, 0 ligne trouvée, adresse e-mail masquée, PRIVATE (2026-11-10) |

## Validation du propriétaire
Date : 2026-11-10 · Verdict : validée (« Oui, valide US-03 ») · Remarques : —

## Rétro éclair
- Ce qui a surpris : le contrôle bloquant a d'abord bloqué sur son propre motif, et il ne voit ni les prénoms
  ni les liens de parenté ; les retirer après coup a demandé une réécriture de l'historique et un push forcé.
- Ce qu'on retient : un dépôt autonome est anonyme dès le premier push (→ `lecons.md`, 2026-11-09).
