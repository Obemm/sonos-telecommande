"""Installer la télécommande sur un téléphone Android (Termux) depuis ce PC, par le Wi-Fi (US-02).

Lancer sur le PC, branché au même Wi-Fi que le téléphone, depuis la racine du dépôt :
    python termux/servir.py
puis taper dans Termux la commande affichée. Ne sert que deux fichiers : installer.sh et
l'archive de la télécommande (sans tests ni caches). Arrêter avec Ctrl+C une fois installé.
"""
from __future__ import annotations

import argparse
import io
import json
import socket
import sys
import tarfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ICI = Path(__file__).resolve().parent
OUTIL = ICI.parent
FICHIERS = ["serveur.py", "demo.py", "config.json", "README.md", "lecons.md",
            "web/index.html", "web/manifest.json", "web/icone.svg"]


def archive() -> bytes:
    """La télécommande en .tar.gz, rangée dans un dossier sonos-telecommande/."""
    tampon = io.BytesIO()
    with tarfile.open(fileobj=tampon, mode="w:gz") as tar:
        for nom in FICHIERS:
            tar.add(OUTIL / nom, arcname=f"sonos-telecommande/{nom}")
    return tampon.getvalue()


def installeur(source: str) -> bytes:
    """installer.sh avec l'adresse de ce PC, en fins de ligne Unix (bash refuse les retours chariot)."""
    texte = (ICI / "installer.sh").read_text(encoding="utf-8").replace("\r\n", "\n")
    return texte.replace("@SOURCE@", source).encode("utf-8")


def adresse_vers(ip: str) -> str:
    """Adresse de ce PC sur le réseau des enceintes (rien n'est envoyé)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((ip, 1400))
        return s.getsockname()[0]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--port", type=int, default=8090)
    a = p.parse_args()
    conf = json.loads((OUTIL / "config.json").read_text(encoding="utf-8"))
    source = f"http://{adresse_vers(conf['enceintes'][0])}:{a.port}"
    fichiers = {"/installer.sh": (installeur(source), "text/plain; charset=utf-8"),
                "/sonos-telecommande.tar.gz": (archive(), "application/gzip")}

    class Gestion(BaseHTTPRequestHandler):
        def do_GET(self):
            corps, typ = fichiers.get(self.path, (None, None))
            if corps is None:
                return self.send_error(404)
            self.send_response(200)
            self.send_header("Content-Type", typ)
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            self.wfile.write(corps)

    print("Dans Termux, sur le téléphone branché au même Wi-Fi :", flush=True)
    print(f"  curl -fsSLO {source}/installer.sh && bash installer.sh", flush=True)
    ThreadingHTTPServer(("0.0.0.0", a.port), Gestion).serve_forever()


if __name__ == "__main__":
    main()
