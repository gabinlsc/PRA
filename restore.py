#!/usr/bin/env python3
import os
import sys
import shutil
import tarfile
import datetime
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

TARGET_DIR = Path("/var/www/html")
BACKUP_BASE = Path("/backup")
ARCHIVE_DIR = BACKUP_BASE / "archives"
KEYS_DIR = BACKUP_BASE / "keys"


def check_prerequisites():
    if os.geteuid() != 0:
        print("[-] Erreur : ce script doit être exécuté en root (sudo).")
        sys.exit(1)
    if not ARCHIVE_DIR.exists():
        print(f"[-] Erreur : aucun dossier {ARCHIVE_DIR} trouvé.")
        sys.exit(1)


def list_backups():
    archives = sorted(list(ARCHIVE_DIR.glob("*.tar.gz.enc")), reverse=True)
    if not archives:
        print("[-] Aucune sauvegarde trouvée.")
        sys.exit(1)
    print("\n--- Sauvegardes disponibles ---")
    for idx, arc in enumerate(archives, 1):
        print(f"{idx}. {arc.name}")
    return archives


def fix_permissions(path: Path):
    print("[*] Réapplication des droits www-data...")
    try:
        shutil.chown(path, user="www-data", group="www-data")
        for root, dirs, files in os.walk(path):
            for d in dirs:
                full_d = os.path.join(root, d)
                os.chmod(full_d, 0o755)
                shutil.chown(full_d, user="www-data", group="www-data")
            for f in files:
                full_f = os.path.join(root, f)
                os.chmod(full_f, 0o644)
                shutil.chown(full_f, user="www-data", group="www-data")
    except KeyError:
        print("[!] Note : utilisateur www-data non trouvé sur ce système.")


def main():
    check_prerequisites()
    archives = list_backups()

    try:
        choice = int(input("\nNuméro de l'archive à restaurer : ").strip())
        if not 1 <= choice <= len(archives):
            raise ValueError
    except ValueError:
        print("[-] Sélection invalide.")
        sys.exit(1)

    selected_archive = archives[choice - 1]
    timestamp_str = selected_archive.name.replace("backup_www_", "").replace(".tar.gz.enc", "")
    associated_key_file = KEYS_DIR / f"backup_{timestamp_str}.key"

    key = None
    if associated_key_file.exists():
        print(f"[+] Clé locale détectée : {associated_key_file}")
        with open(associated_key_file, "rb") as kf:
            key = kf.read().strip()
    else:
        user_key = input("[?] Clé locale introuvable. Saisis la clé manuellement : ").strip()
        key = user_key.encode()

    try:
        fernet = Fernet(key)
        print("[*] Déchiffrement...")
        with open(selected_archive, "rb") as f_in:
            encrypted_data = f_in.read()
        decrypted_data = fernet.decrypt(encrypted_data)
    except (InvalidToken, Exception):
        print("[-] Échec du déchiffrement : clé incorrecte ou fichier corrompu.")
        sys.exit(1)

    temp_tar = BACKUP_BASE / "temp_restore.tar.gz"
    with open(temp_tar, "wb") as f_out:
        f_out.write(decrypted_data)

    if TARGET_DIR.exists():
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_current = TARGET_DIR.parent / f"html.bak.{now}"
        print(f"[*] Sauvegarde de sécurité : {backup_current}")
        TARGET_DIR.rename(backup_current)

    print(f"[*] Extraction vers {TARGET_DIR.parent}...")
    with tarfile.open(temp_tar, "r:gz") as tar:
        tar.extractall(path=TARGET_DIR.parent)
    temp_tar.unlink()

    fix_permissions(TARGET_DIR)
    print("[+] Restauration terminée avec succès !\n")


if __name__ == "__main__":
    main()
