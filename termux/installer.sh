#!/data/data/com.termux/files/usr/bin/bash
# Installe ou met à jour la télécommande Sonos dans Termux, sur un téléphone Android (US-02).
# Servi par termux/servir.py, qui remplace l'adresse ci-dessous par celle du PC. Dans Termux :
#   curl -fsSLO http://<adresse du PC>:8090/installer.sh && bash installer.sh
# Télécharger puis lancer, pas « curl | bash » : pkg lit le clavier pendant l'installation.
set -eu
SOURCE="@SOURCE@"
DOSSIER="$HOME/sonos-telecommande"
LANCEUR="$HOME/.termux/boot/sonos-telecommande.sh"
TEMP="${TMPDIR:-$PREFIX/tmp}"

echo "== 1/5 Mise à jour de Termux (quelques minutes la première fois)"
yes | pkg upgrade

echo "== 2/5 Python et lxml, déjà compilés pour Android"
pkg install -y python python-lxml

echo "== 3/5 Télécommande, depuis $SOURCE"
curl -fsSL "$SOURCE/sonos-telecommande.tar.gz" -o "$TEMP/sonos-telecommande.tar.gz"
tar xzf "$TEMP/sonos-telecommande.tar.gz" -C "$HOME"
rm -f "$TEMP/sonos-telecommande.tar.gz"

echo "== 4/5 SoCo, la bibliothèque qui parle aux Sonos"
if [ ! -x "$DOSSIER/env/bin/python" ]; then
  python -m venv --system-site-packages "$DOSSIER/env"  # l'environnement voit le lxml de Termux
fi
"$DOSSIER/env/bin/pip" install --quiet --upgrade soco

echo "== 5/5 Lancement automatique et commande « sonos »"
mkdir -p "$HOME/.termux/boot"
cat > "$LANCEUR" <<'FIN'
#!/data/data/com.termux/files/usr/bin/sh
# Lance la télécommande : au démarrage du téléphone (appli Termux:Boot) et par la commande « sonos ».
termux-wake-lock
pkill -f "sonos-telecommande/serveur.py" || true
cd "$HOME/sonos-telecommande"
nohup env/bin/python "$HOME/sonos-telecommande/serveur.py" --hote 127.0.0.1 >> journal.txt 2>&1 &
FIN
chmod +x "$LANCEUR"
ln -sf "$LANCEUR" "$PREFIX/bin/sonos"

"$LANCEUR"
echo "Démarrage : les enceintes répondent en quelques secondes…"
for essai in 1 2 3 4 5 6 7 8 9 10; do
  if curl -fsS -m 15 -o /dev/null http://127.0.0.1:8080/api/etat 2>/dev/null; then
    echo
    echo "C'est prêt. Dans Chrome : http://localhost:8080 puis menu ⋮ → « Ajouter à l'écran d'accueil »."
    echo "Relancer à la main : taper « sonos » dans Termux. Quitter Termux par le bouton d'accueil, pas par « exit »."
    echo "Démarrage automatique : installer l'appli Termux:Boot (F-Droid) et l'ouvrir une fois."
    echo "Batterie : Réglages → Applications → Termux → Batterie → « Non restreinte »."
    exit 0
  fi
  sleep 3
done
echo "La télécommande ne répond pas. Dernières lignes du journal :"
tail -n 20 "$DOSSIER/journal.txt"
exit 1
