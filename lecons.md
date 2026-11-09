# Leçons — sonos-telecommande

- 2026-11-08 : le système est en **S1** (11.16.1). Les deux Play:5 de 1re génération (modèle `S5`)
  bloquent la migration vers S2, donc la nouvelle app Sonos ne peut pas les gérer. Ce n'est pas un défaut de réglage.
- 2026-11-08 : la découverte SSDP de SoCo ne trouve rien depuis le PC Windows (pare-feu) : utiliser les IP
  de `config.json`. Le modèle se lit sans SoCo : `http://<ip>:1400/xml/device_description.xml`.
- 2026-11-08 : les favoris Sonos renvoient souvent la pochette `…:1400unknown` (pas d'image) ; les pochettes
  YouTube Music sont des URL publiques (googleusercontent), parfois expirées : garder la note ♪ en repli.
- 2026-11-08 : ne jamais lancer de lecture pour tester chez quelqu'un : tester les commandes silencieuses
  (volume à sa valeur actuelle, muet aller-retour sur une pièce à l'arrêt) et laisser les essais sonores à l'utilisateur.
- 2026-11-08 : pour tout cliquer sans bruit, utiliser `--demo` (enceintes imaginaires, même API que les vraies).
  Pour refaire la page pendant que la vraie sert, travailler sur une copie servie avec `--demo --web <copie>`.
- 2026-11-08 : un serveur lancé garde l'ancien code Python : redémarrer après une modification de `serveur.py`.
  Les fichiers de `web/` sont relus à chaque chargement.
- 2026-11-08 : `parse_qs` ignore un paramètre sans valeur (`?frais`) sans `keep_blank_values=True`.
- 2026-11-08 : vérifier l'affichage à 360×640, 390×844, 820×1180, 1000×600 et 1280×800 : chaque taille a révélé
  un défaut différent. Exemple : des pastilles passées sur trois lignes sortaient le lecteur de l'écran sur ordinateur.
- 2026-11-08 : un élément fixe centré par `left:50%` + `translateX(-50%)` n'a que la moitié de l'écran pour son texte
  (bandeau sur 3 lignes). Centrer avec `left` et `right`, `width:fit-content` et `margin-inline:auto`.
- 2026-11-08 : une PWA seule ne peut pas piloter les Sonos. Le port 1400 n'envoie aucun en-tête CORS (préflight
  OPTIONS → erreur 500) et une page en HTTPS ne peut pas appeler `http://`. Vérifié depuis le navigateur : lecture de
  la fiche et du volume bloquées (« Failed to fetch »). Il faut un intermédiaire : notre serveur (PC, Raspberry Pi,
  Termux sur Android) ou une app native.
- 2026-11-08 : SoCo exige `lxml`, une bibliothèque compilée. Sous Termux, la prendre déjà compilée
  (`pkg install python-lxml`) et créer l'environnement Python avec `--system-site-packages` ; le reste est en pur Python.
  Le script Termux doit être en fins de ligne Unix, et se télécharger puis se lancer (pas `curl | bash` : pkg lit le
  clavier). À confirmer au premier essai sur le téléphone.
- 2026-11-08 : un téléphone qui se verrouille coupe la requête en cours (`ConnectionAbortedError`) : ne rien répondre,
  sinon le serveur écrit une trace d'erreur.
- 2026-11-09 : le dépôt reste **sans donnée personnelle** (demande du propriétaire) : ni lien de parenté, ni prénom,
  ni date de passage sur place, ni équipement de la maison hors sujet ; commits sous l'adresse e-mail masquée de GitHub.
  Le contrôle bloquant ne voit pas ces mots-là : relire le diff. Corrigé après coup, cela a coûté une réécriture
  de l'historique et un push forcé.
