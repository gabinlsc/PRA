#!/usr/bin/env python3
import os
import sys
import tarfile
import datetime
from pathlib import Path
from cryptography.fernet import Fernet

SOURCE_DIR = Path("/var/www/html")
BACKUP_BASE = Path("/backup")
ARCHIVE_DIR = BACKUP_BASE / "archives"
KEYS_DIR = BACKUP_BASE / "keys"


def check_prerequisites():
    if os.geteuid() != 0:
        print("[-] Erreur : ce script doit être exécuté en root (sudo).")
        sys.exit(1)
    if not SOURCE_DIR.exists():
        print(f"[-] Erreur : le dossier {SOURCE_DIR} n'existe pas.")
        sys.exit(1)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(KEYS_DIR, 0o700)


def create_archive(timestamp: str) -> Path:
    temp_archive = ARCHIVE_DIR / f"temp_{timestamp}.tar.gz"
    print(f"[*] Archivage de {SOURCE_DIR}...")
    with tarfile.open(temp_archive, "w:gz") as tar:
        tar.add(SOURCE_DIR, arcname="html")
    return temp_archive


def encrypt_file(file_path: Path, output_path: Path, key: bytes):
    fernet = Fernet(key)
    print("[*] Chiffrement de l'archive...")
    with open(file_path, "rb") as f_in:
        data = f_in.read()
    encrypted_data = fernet.encrypt(data)
    with open(output_path, "wb") as f_out:
        f_out.write(encrypted_data)
    file_path.unlink()


def main():
    check_prerequisites()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    target_enc = ARCHIVE_DIR / f"backup_www_{timestamp}.tar.gz.enc"
    key_file = KEYS_DIR / f"backup_{timestamp}.key"

    print("\n--- PRA Backup System (Python) ---")
    print("1. Sauvegarde standard (clé stockée sur le serveur)")
    print("2. Sauvegarde isolée (afficher la clé et la détruire du disque)")
    choice = input("Choix [1-2] : ").strip()

    if choice not in ("1", "2"):
        print("[-] Choix invalide.")
        sys.exit(1)

    key = Fernet.generate_key()
    temp_archive = create_archive(timestamp)
    encrypt_file(temp_archive, target_enc, key)

    if choice == "1":
        with open(key_file, "wb") as kf:
            kf.write(key)
        os.chmod(key_file, 0o600)
        print(f"[+] Clé enregistrée dans : {key_file}")
    else:
        print("\n[!] ATTENTION : Note bien cette clé dans un gestionnaire sécurisé !")
        print(f"CLÉ : {key.decode()}\n")

    print(f"[+] Sauvegarde terminée : {target_enc}\n")


if __name__ == "__main__":
    main()
