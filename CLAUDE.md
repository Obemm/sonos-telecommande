# sonos-telecommande

Lu automatiquement par Claude Code au début de chaque session.

## Le projet
- Télécommande web qui remplace l'app Sonos S1 dans une maison de 5 pièces (deux Play:5 de
  1re génération bloquent le passage en S2). Serveur Python (SoCo) et page `web/`. Détail : `README.md`.
- Vocabulaire : « le propriétaire » possède ce dépôt et mène le projet ; « l'utilisateur » se sert de la
  télécommande chez lui, « sur place ».
- Projet autonome depuis le 2026-11-09 : sorti de ProjetMaison (ex-EPIC-12, ADR-008 de ProjetMaison).
  Aucune dépendance vers ProjetMaison.
- Suivi : `backlog/BOARD.md` (objectif, stories par statut, prochaines étapes), une story par fichier
  dans `backlog/stories/` (modèle : `backlog/templates/story.md`).
- Leçons : `lecons.md`. Les lire avant toute tâche ; y écrire tout de suite, datée, chaque correction
  du propriétaire ou chose apprise.

## Conventions
- Français, réponses concises, options toujours numérotées : le propriétaire répond par numéro.
- Rien hors d'une story. Avant de coder, relire la story et ses critères au propriétaire. Après : tests
  exécutés et consignés dans la story, statut « À valider », le propriétaire valide.
- Début de session : lire `backlog/BOARD.md` et `lecons.md`, `git status`, dire en trois lignes où on en est.
- Python : `C:\Users\obemm\AppData\Local\Programs\Python\Python312\python.exe` (le `python` du PATH est
  un venv cassé). Tests : `python -m unittest discover tests`, sans enceinte.
- Essayer l'interface en mode démo (`--demo --port 8081`, configuration « sonos-demo » de
  `.claude/launch.json`) : enceintes imaginaires, aucun son.
- Sur les vraies enceintes, chez l'utilisateur : **jamais de lecture lancée pour tester**, seulement des
  commandes silencieuses (volume à sa valeur, muet aller-retour sur une pièce à l'arrêt). Les essais
  sonores sont faits par le propriétaire.
- Le serveur est sans mot de passe, donc réservé au réseau local : ne jamais ouvrir son port sur Internet.
- `termux/installer.sh` reste en fins de ligne Unix (règle dans `.gitattributes`, vérifiée par les tests).

## Git
- Dépôt privé GitHub `Obemm/sonos-telecommande`, branche `main`. Les IP locales des enceintes
  (`config.json`, README) y sont acceptées parce que le dépôt est privé (choix du propriétaire, 2026-11-09).
- **Aucune donnée personnelle**, ni dans les fichiers ni dans les commits (choix du propriétaire, 2026-11-09) :
  ni lien de parenté, ni prénom, ni date de passage sur place, ni équipement de la maison sans rapport
  avec Sonos. Les commits portent l'adresse e-mail masquée de GitHub (noreply), réglée dans la
  configuration Git de ce dépôt (`git config user.email`) : ne pas la changer.
- Commit et push seulement à la demande du propriétaire. Avant chaque commit, contrôle **bloquant** des
  données personnelles et des secrets sur le diff indexé (une ligne trouvée = la commande échoue ;
  les crochets de `salai[r]e` et `private[ ]key` évitent que le motif se trouve lui-même) :
  ```bash
  ! git diff --cached | grep -nEi '(\+33 ?|\b0)[1-9]([ .-]?[0-9]{2}){4}\b|[a-z0-9._%+-]+@[a-z0-9-]+\.[a-z.]{2,}|salai[r]e|pr(é|e)avis|(password|passwd|secret|token|api[_-]?key)[^a-z]{0,4}[:=][^a-z0-9]{0,3}[a-z0-9/+_-]{8,}|mot de passe *[:=] *[^ ]{6,}|private[ ]key|([0-9a-f]{2}[:-]){5}[0-9a-f]{2}'
  ```
  Ce contrôle ne voit ni les prénoms ni les liens de parenté : relire aussi le diff.
