# <img src="../picgomd-web/public/maoer.png" width="39" height="39" alt="Picgo.MD Logo" style="vertical-align: middle;">   Picgo.MD · MdImgConverter

Convertissez les images Markdown au format WebP et téléchargez-les vers des services d'hébergement d'images en un clic ! (=^･ω･^=)✧

![Preview](../icons/image/preview.png)

---

## 💫 Caractéristiques

### 🌟 Fonctions Principales
- 🐾 **Conversion en Un Clic** : Détecte automatiquement les images Markdown et les convertit au format WebP
- 🎚️ **Qualité Ajustable** : Contrôle l'équilibre qualité/taille avec curseur, par défaut 73% optimal
- 🔗 **Réécriture de Chemins** : Remplacement intelligent des liens `images/*.webp` ou URL externes
- ☁️ **Téléchargement vers Hébergement d'Images** : Support pour Alibaba Cloud OSS, Tencent Cloud COS, Qiniu Cloud, S3, GitHub et autres services

### 🚀 Versions d'Application
- 🖥️ **Version Bureau** : Construite avec Tauri, taille compacte, excellentes performances, expérience native
- 🌐 **Version Web** : React moderne + Chakra UI, supporte l'utilisation en ligne
- 🪄 **Interface Épurée** : Supprimés les boutons de débogage et configuration backend, concentré sur la fonctionnalité principale

---

## 🚀 Démarrage Rapide

### 🖥️ Application Bureau (Recommandée)
- Allez à la page Releases du dépôt et téléchargez la dernière version bureau :
  - 📦 **Installateur MSI** : `Picgo.MD_0.1.0_x64_en-US.msi` - Installateur Windows standard
  - 🚀 **Version Portable** : `Picgo.MD_0.1.0_x64-setup.exe` - Exécute directement sans installation
- Si bloqué par SmartScreen lors de la première exécution, cliquez sur "Plus d'informations" → "Exécuter quand même"
- Construit avec Tauri, taille compacte et excellentes performances ! ✨

### 🌐 Application Web
- Expérience en ligne : Visitez la version Web déployée
- Nécessite service backend : `python picgomd-backend/main.py`
- Adapté pour déploiement serveur ou développement local

### 👨‍💻 Version Développeur
- Voulez exécuter depuis le code source ? Voir `Read.md/coder-README.md`
- Développement bureau : `cd desktop && npm run tauri dev`
- Développement web : `cd picgomd-web && npm run dev`

---

## 🎯 Utilisation

### 🖥️ Utilisation Bureau
1. 📝 **Saisie de Contenu** : Collez ou glissez des fichiers Markdown dans l'éditeur
2. 🎚️ **Ajuster Qualité** : Utilisez le curseur droit pour ajuster la qualité de compression (par défaut 73% est parfait)
3. 🔄 **Démarrer Conversion** : Cliquez sur le bouton "Démarrer la Conversion"
4. ☁️ **Télécharger vers Hébergement d'Images** : Besoin de liens externes ? Cliquez sur "Paramètres" pour configurer l'hébergement d'images pour téléchargement automatique
5. 💾 **Sauvegarder Résultats** : Sauvegardez le nouveau fichier Markdown après conversion

### 🌐 Utilisation Web
1. 🚀 Démarrer backend : `python picgomd-backend/main.py`
2. 🌐 Ouvrir interface Web (habituellement `http://localhost:8000`)
3. 📝 Saisissez contenu Markdown dans l'éditeur gauche
4. 🎛️ Ajustez paramètres à droite et cliquez convertir
5. 📥 Téléchargez le fichier converti

---

## 🧰 Services d'Hébergement d'Images Supportés

### 📡 Alibaba Cloud OSS
**Paramètres de Configuration :**
- **Access Key ID** et **Access Key Secret** : Clés de compte Alibaba Cloud
- **Bucket** : Nom du bucket de stockage
- **Endpoint** : ex., `oss-cn-beijing` (complète automatiquement protocole et domaine)
- **Domaine Personnalisé** : Optionnel, domaine CDN lié
- **Préfixe de Chemin de Stockage** : Optionnel, ex., `images/` crée structure de répertoire dans bucket

**Format d'URL :** `https://bucket.oss-cn-beijing.aliyuncs.com/path/file.webp`

### 🌪️ Tencent Cloud COS
**Paramètres de Configuration :**
- **Secret ID** et **Secret Key** : Clés de compte Tencent Cloud
- **Bucket** : Nom du bucket de stockage (format : `bucket-appid`)
- **Region** : Région, ex., `ap-beijing`
- **Domaine Personnalisé** : Optionnel, domaine CDN lié
- **Préfixe de Chemin de Stockage** : Optionnel, préfixe de répertoire

**Format d'URL :** `https://bucket-appid.cos.ap-beijing.myqcloud.com/path/file.webp`

### 🦄 Qiniu Cloud Kodo
**Paramètres de Configuration :**
- **Access Key** et **Secret Key** : Clés de compte Qiniu Cloud
- **Bucket** : Nom de l'espace de stockage
- **Domain** : Domaine d'accès lié (requis)
- **Préfixe de Chemin de Stockage** : Optionnel, préfixe de répertoire

**Format d'URL :** `https://your-domain.com/path/file.webp`

### 🪣 Stockage Compatible S3
**Services Supportés :** AWS S3, MinIO, Alibaba Cloud OSS S3 API, Tencent Cloud COS S3 API, etc.
**Paramètres de Configuration :**
- **Access Key** et **Secret Key** : Clés d'accès S3
- **Bucket** : Nom du bucket de stockage
- **Region** : Région, ex., `us-east-1`
- **Endpoint** : Optionnel, endpoint personnalisé (ex., adresse serveur MinIO)
- **Domaine Personnalisé** : Optionnel, domaine CDN
- **Préfixe de Chemin de Stockage** : Optionnel, préfixe de répertoire
- **Style de Chemin** : Optionnel, activer accès style chemin

**Format d'URL :** `https://s3.region.amazonaws.com/bucket/path/file.webp`

### 🐙 Dépôt GitHub
**Paramètres de Configuration :**
- **Personal Access Token** : Token d'accès personnel GitHub (nécessite permissions repo)
- **Repository Owner** : Nom d'utilisateur ou organisation GitHub
- **Repository Name** : Nom du dépôt pour stocker images
- **Branch** : Branche cible, ex., `main` ou `master`
- **Préfixe de Chemin du Dépôt** : Optionnel, ex., `images/` crée répertoire dans dépôt
- **Domaine Personnalisé** : Optionnel, accès par domaine personnalisé
- **Utiliser jsDelivr CDN** : Optionnel, accès accéléré via CDN

**Format d'URL :**
- Lien direct GitHub : `https://raw.githubusercontent.com/user/repo/branch/path/file.webp`
- jsDelivr CDN : `https://cdn.jsdelivr.net/gh/user/repo@branch/path/file.webp`

## 🔧 Conseils de Configuration
- **Endpoint Alibaba Cloud OSS** : `oss-cn-beijing` → devient automatiquement `https://oss-cn-beijing.aliyuncs.com`
- **Protocole URL** : Tous les services supportent HTTPS (recommandé) et HTTP
- **Effacer Configuration** : Cliquez sur le bouton "Effacer" dans la boîte de dialogue de paramètres d'hébergement d'images
- **Tester Téléchargement** : Cliquez sur "Tester le Téléchargement" après configuration pour vérifier que les paramètres sont corrects

---

## 🌍 Support Multi-langue
L'application supporte maintenant plusieurs langues :
- 🇨🇳 **Chinois** (Par défaut)
- 🇺🇸 **Anglais**
- 🇪🇸 **Espagnol**
- 🇫🇷 **Français**

Vous pouvez changer de langue en utilisant le sélecteur de langue dans le coin supérieur droit de l'interface.

---

## 🧭 Feuille de Route de Développement
- ✅ **Optimisation Interface** : Supprimés boutons de débogage et configuration backend pour interface plus propre
- ✅ **Version Bureau** : Application bureau moderne basée sur Tauri terminée
- ✅ **Version Web** : Interface moderne React + Chakra UI
- ✅ **Support Multi-langue** : Chinois, Anglais, Espagnol, Français
- 🔄 **Ajouter Animations UI**
- 🔄 **Support pour Autres Formats de Compression** (AVIF, JPEG XL)
- 🔄 **Ajouter Aperçu de Rendu de Fichiers Markdown**
- 🔄 **Mode de Traitement par Lots**

---

## 📝 Licence
MIT. Bienvenue développement secondaire et créations de fans (veuillez conserver l'attribution miaou).

---

## 📚 Navigation Documentation

### 🎯 Documentation Utilisateur
- **[README.md](../README.md)** - Page d'accueil du projet, guide de démarrage rapide
- **[README-en.md](README-en.md)** - Documentation version anglaise
- **[README-es.md](README-es.md)** - Documentation version espagnole
- **[README-fr.md](README-fr.md)** - Documentation version française
- **[BUILD_GUIDE.md](BUILD_GUIDE.md)** - Guide détaillé de construction et empaquetage
- **[PACKAGING_COMPARISON.md](PACKAGING_COMPARISON.md)** - Comparaison de configuration d'empaquetage

### 🔧 Documentation Développeur
- **[coder-README.md](coder-README.md)** - Documentation technique, configuration environnement de développement
- **[coder-picgo-README.md](coder-picgo-README.md)** - Guide développement extension hébergement d'images
- **[imd-README.md](imd-README.md)** - Documentation détaillée bibliothèque centrale imarkdown
- **[imd-README_zh.md](imd-README_zh.md)** - Documentation chinoise imarkdown

### 🎨 Ressources Design
- **[ICON_MANIFEST.md](ICON_MANIFEST.md)** - Liste vérification utilisation icônes et instructions configuration
- **[../icons/README.md](../icons/README.md)** - Instructions détaillées pack icônes multi-plateforme

### 📊 Gestion Projet
- **[meum-README.md](meum-README.md)** - Description complète structure répertoires projet
- **[DOCS_INDEX.md](DOCS_INDEX.md)** - Index documentation et navigation

### 🧪 Documentation Test
- **[../md-converter-gui/test_images.md](../md-converter-gui/test_images.md)** - Cas de test GUI

---

**Navigation Rapide :**
- 🚀 Voulez utiliser rapidement ? Voir [README.md](../README.md)
- 🔧 Voulez développer extensions ? Voir [coder-README.md](coder-README.md)
- 📦 Voulez empaqueter vous-même ? Voir [BUILD_GUIDE.md](BUILD_GUIDE.md)
- 🎨 Voulez comprendre icônes ? Voir [ICON_MANIFEST.md](ICON_MANIFEST.md)
- 📁 Voulez comprendre structure ? Voir [meum-README.md](meum-README.md)
