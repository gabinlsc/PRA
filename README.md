# 🛡️ PRA - Scripts de sauvegarde et restauration chiffrées

Ce dépôt regroupe l'ensemble des procédures et scripts d'automatisation dédiés à la sauvegarde chiffrée, au versioning et à la restauration à chaud de l'arborescence web `/var/www/html`.

Le projet propose deux implémentations complémentaires :
* **Bash** : solution native, légère, basée sur `tar` et `openssl` (sans runtime supplémentaire).
* **Python** : solution modulaire via la bibliothèque standard et `cryptography` (Fernet : AES-128-CBC + HMAC-SHA256).

---

## 📁 Structure du Dépôt

```text
.
├── backup_www.sh       # Script de sauvegarde Bash (OpenSSL AES-256-CBC)
├── restore_www.sh      # Script de restauration Bash
├── backup.py           # Script de sauvegarde Python (Fernet / AES + HMAC)
├── restore.py          # Script de restauration Python
├── requirements.txt    # Dépendances Python (cryptography)
└── README.md           # Documentation globale
```

---

## ⚙️ Prérequis Globaux

Sur la machine ou VM Ubuntu hôte :

```bash
sudo apt update && sudo apt install -y openssl tar python3 python3-pip python3-venv
```

---

## 🚀 Installation & Déploiement

1. Cloner le dépôt :

```bash
git clone git@github.com:gabinlsc/PRA.git
cd PRA
```

2. Préparer l'environnement Python :

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Définir les permissions d'exécution :

```bash
chmod +x backup_www.sh restore_www.sh backup.py restore.py
```

---

## 🛠️ Utilisation

Les deux solutions partagent la même logique d'arborescence cible dans `/backup` :
* `/backup/archives/` : archives compressées et chiffrées (`.enc`)
* `/backup/keys/` : clés symétriques stockées localement (`.key`, droits `600`)

---

### Méthode 1 — Version Python (Recommandée)

#### 1. Sauvegarde

```bash
sudo ./venv/bin/python backup.py
```

* **Option 1 (Standard)** : archive `/var/www/html`, génère une clé Fernet, chiffre l'archive et consigne la clé dans `/backup/keys/backup_<timestamp>.key`.
* **Option 2 (Air-gap / Coffre)** : chiffre l'archive, imprime la clé unique sur la sortie standard (terminal) et ne conserve aucune trace sur le disque.

#### 2. Restauration

```bash
sudo ./venv/bin/python restore.py
```

1. Détection et sélection interactive de l'archive dans `/backup/archives/`.
2. Résolution automatique de la clé locale correspondante ou saisie manuelle si la clé a été externalisée.
3. Rotation de précaution : déplacement de `/var/www/html` en `/var/www/html.bak.<timestamp>`.
4. Déchiffrement en mémoire, décompression et réapplication récursive des permissions `www-data:www-data` (dossiers `755`, fichiers `644`).

---

### Méthode 2 — Version Bash (Sans dépendance Python)

#### 1. Sauvegarde

```bash
sudo ./backup_www.sh
```

* Archive via `tar -czf`.
* Chiffrement avec `openssl enc -aes-256-cbc -pbkdf2 -iter 100000`.
* Génération de clé pseudo-aléatoire 256 bits (`openssl rand -base64 32`).
* Choix entre stockage local sécurisé (`chmod 600`) ou effacement sécurisé (`shred -u`).

#### 2. Restauration

```bash
sudo ./restore_www.sh
```

* Déchiffrement de l'archive via `openssl enc -d`.
* Sauvegarde miroir préalable (`html.bak.*`).
* Extraction et rétablissement des droits utilisateur web (`chown -R www-data:www-data`).

---

## 🔒 Bonnes Pratiques & Sécurité

- Stockage déporté : Ne conserve pas les clés de déchiffrement uniquement sur la machine hébergeant le site. En cas de perte matérielle du serveur, les sauvegardes deviendraient inutilisables.
- Accès restreints : Seul l'utilisateur root doit avoir accès au dossier /backup/keys.
* **Principe du moindre privilège** : le répertoire `/backup/keys/` doit impérativement rester sous permissions `700` (`rwx------`) appartenant à `root:root`.
* **Externalisation** : synchroniser régulièrement les archives (`.tar.gz.enc`) vers un stockage distant (S3, NAS, SFTP secondaire) et conserver les clés dans un gestionnaire de secrets dédié (Vault, Bitwarden, Keepass).
