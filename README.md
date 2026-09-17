# 🛡️ PRA - Scripts de Sauvegarde et Restauration Chiffrées

Ensemble d'outils Bash permettant d'assurer la sauvegarde chiffrée et la restauration à chaud de l'arborescence web (/var/www/html).

---

## 📋 Fonctionnalités

- Chiffrement fort : AES-256-CBC avec dérivation de clé PBKDF2 (100 000 itérations).
- Gestion des clés : Génération cryptographique aléatoire de 256 bits par archive (openssl rand).
- Isolation sécurisée : Clés stockées avec permissions restreintes (chmod 600) et option d'effacement sécurisé (shred).
- Restauration sécurisée : Déchiffrement à la volée, backup automatique du dossier existant avant écrasement et réapplication des droits www-data.

---

## ⚙️ Prérequis

Installe les paquets nécessaires sur ta machine/VM Ubuntu :

sudo apt update && sudo apt install -y openssl tar

---

## 🚀 Installation

1. Clone le projet (si ce n'est pas déjà fait) :

git clone git@github.com:gabinlsc/PRA.git
cd PRA

2. Rends les scripts exécutables et déploie-les dans les exécutables système :

sudo chmod +x backup_www.sh restore_www.sh
sudo cp backup_www.sh /usr/local/sbin/
sudo cp restore_www.sh /usr/local/sbin/

---

## 🛠️ Utilisation

### 1. Sauvegarde (backup_www.sh)

Lance le script en root :

sudo /usr/local/sbin/backup_www.sh

Un menu interactif s'affiche :
- Option 1 : Archive le dossier /var/www/html, génère la clé, chiffre l'archive et conserve la clé dans /backup/keys/.
- Option 2 : Même procédure, mais affiche la clé générée à l'écran pour la noter/stocker dans un coffre, puis la supprime du disque avec shred.

Arborescence générée dans /backup :

/backup/
├── archives/   # Archives chiffrées (*.tar.gz.enc)
├── keys/       # Clés de déchiffrement (*.key)
└── logs/       # Journaux d'exécution (*.log)

---

### 2. Restauration (restore_www.sh)

Pour restaurer une sauvegarde précédente :

sudo /usr/local/sbin/restore_www.sh

1. Sélectionne l'archive souhaitée dans la liste des sauvegardes disponibles.
2. Le script utilise la clé locale associée ou t'invite à saisir la clé manuellement si elle a été supprimée du serveur.
3. Le contenu actuel de /var/www/html est déplacé vers un dossier horodaté de sécurité (html.bak.*).
4. L'archive est extraite et les permissions www-data:www-data (dossiers 755, fichiers 644) sont restaurées automatiquement.

---

## ⚠️ Recommandations de sécurité

- Stockage déporté : Ne conserve pas les clés de déchiffrement uniquement sur la machine hébergeant le site. En cas de perte matérielle du serveur, les sauvegardes deviendraient inutilisables.
- Accès restreints : Seul l'utilisateur root doit avoir accès au dossier /backup/keys.