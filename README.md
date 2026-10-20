# AIC — Audio Intelligence Companion

![GitHub Actions](https://img.shields.io/github/actions/workflow/status/Flex1-tech/AIC-Audio-Intelligence-Companion/build-desktop.yml?branch=main&label=CI%2FCD&logo=github-actions&logoColor=white)
![GitHub Release](https://img.shields.io/github/v/release/Flex1-tech/AIC-Audio-Intelligence-Companion?label=Release&logo=github)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-0.86%2B-blueviolet?logo=flutter&logoColor=white)
![AI](https://img.shields.io/badge/AI-MusiCNN-orange?logo=tensorflow&logoColor=white)
![ONNX Runtime](https://img.shields.io/badge/ONNX%20Runtime-005CED?logo=onnx&logoColor=white)
![LanceDB](https://img.shields.io/badge/LanceDB-0.21%2B-blue?logo=lancedb&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-MMR%20%7C%20Embeddings-brightgreen?logo=scikit-learn&logoColor=white)
![Audio](https://img.shields.io/badge/Audio-FFprobe%20%7C%20FFmpeg-red?logo=audiomack&logoColor=white)
![License](https://img.shields.io/badge/License-PolyForm%20Noncommercial%201.0.0-lightgrey)

> [!CAUTION]
> Ce logiciel est distribué sous la licence **PolyForm Noncommercial 1.0.0**.
> Toute utilisation commerciale est interdite sans autorisation explicite de l'auteur.
> Pour un usage commercial, veuillez contacter le titulaire des droits.

AIC (Audio Intelligence Companion) est une application de recommandation musicale intelligente fonctionnant **100 % hors ligne et en local**.

Elle analyse votre bibliothèque multimédia à l'aide du réseau de neurones convolutionnel **MusiCNN**, extrait des représentations acoustiques vectorielles denses (embeddings à 200 dimensions), les indexe dans une base vectorielle embarquée **LanceDB**, puis génère des playlists équilibrées grâce à l'algorithme vectorisé **Maximum Marginal Relevance (MMR)**.

L'application est développée en **Python 3.12** avec le framework réactif **Flet** et ne requiert aucune connexion internet ni service cloud tiers.

---

## Downloads

Les versions officielles compilées pour **Windows**, **Linux** et **macOS** sont disponibles dans les GitHub Releases.

| Plateforme | Formats disponibles |
|---|---|
| Windows (x64) | Installateur (`AIC-Setup-vX.Y.Z.exe`) · Portable ZIP (`AIC-Portable-vX.Y.Z.zip`) |
| Linux (x64) | AppImage (`AIC-vX.Y.Z.AppImage`) |
| macOS (Apple Silicon) | DMG (`AIC-vX.Y.Z.dmg`) |

**Dernière release** : https://github.com/Flex1-tech/AIC-Audio-Intelligence-Companion/releases/latest

---

## Installer AIC (Exécutables précompilés)

### Windows — Installateur (recommandé)

1. Télécharger `AIC-Setup-vX.Y.Z.exe` depuis les [Releases](https://github.com/Flex1-tech/AIC-Audio-Intelligence-Companion/releases/latest).
2. Exécuter l'installateur et suivre les étapes.
3. AIC est installé dans `Program Files` avec un raccourci Menu Démarrer.
4. Une entrée de désinstallation est créée dans les Paramètres Windows.

> [!NOTE]
> **Windows SmartScreen** : l'application n'étant pas encore signée avec un certificat commercial, cliquez sur **Informations complémentaires** puis **Exécuter quand même** si un avertissement apparaît.

### Windows — Version Portable

1. Télécharger `AIC-Portable-vX.Y.Z.zip`.
2. Extraire dans le répertoire de votre choix.
3. Double-cliquer sur `AIC.exe`.

La version portable ne modifie pas le registre système et fonctionne directement depuis une clé USB.

### Linux — AppImage

1. Télécharger `AIC-vX.Y.Z.AppImage`.
2. Rendre le fichier exécutable :
   ```bash
   chmod +x AIC-vX.Y.Z.AppImage
   ```
3. Lancer :
   ```bash
   ./AIC-vX.Y.Z.AppImage
   ```

### macOS — DMG

> [!IMPORTANT]
> AIC macOS est compilé exclusivement pour **Apple Silicon (arm64)**. Non compatible avec les Mac Intel (x86_64).

1. Télécharger `AIC-vX.Y.Z.dmg`.
2. Ouvrir le fichier DMG.
3. Glisser `AIC.app` dans le dossier **Applications**.
4. Au premier lancement, ouvrir via **Clic droit → Ouvrir** pour autoriser l'exécution de l'application non notarisée.

---

## Fonctionnalités principales

* **Analyse acoustique locale** : extraction d'empreintes sonores basées sur le modèle MusiCNN pré-entraîné sans téléversement de données.
* **Empreinte cryptographique BLAKE3** : identification unique et instantanée de chaque fichier, garantissant le dédoublonnage et l'intégrité de la bibliothèque.
* **Scan multimédia universel** : support des fichiers audio (`.mp3`, `.flac`, `.ogg`, `.wav`, `.m4a`) et des conteneurs vidéo avec flux audio (`.webm`, `.mp4`).
* **Validation unifiée et bypass intelligent** : vérification par type MIME (`fleep`), détection de flux audio via `ffprobe` et bypass automatique pour les fichiers déjà indexés.
* **Moteur de recommandation MMR vectorisé** : équilibrage mathématique entre pertinence acoustique (proximité avec vos favoris) et diversité de découverte via opérations matricielles NumPy.
* **Base vectorielle LanceDB** : stockage persistant local avec indexation scalaire `file_hash` et index vectoriel `IvfPq` automatique pour les grandes collections.
* **Lecture externe multiplateforme** : intégration transparente avec VLC Media Player, repli vers le lecteur système par défaut et dialogues natifs « Ouvrir avec… ».
* **Exploration dans le système de fichiers** : localisation et mise en surbrillance directe du morceau dans l'Explorateur Windows, Finder macOS ou gestionnaire Linux.
* **Export de playlists M3U / M3U8** : génération au format UTF-8 avec chemins absolus normalisés, compatible avec tous les lecteurs du marché.
* **Outil de capture automatisé HD / 4K** : script de capture reproductible d'écrans et vidéo pour les documentations et assets graphiques.

---

## Architecture du projet

Le projet applique les principes de la **Clean Architecture** et du **Domain-Driven Design (DDD)** :

```text
AIC-Audio-Intelligence-Companion/
│
├── core/                  # Gestion de l'état réactif global (AppState, Bus d'événements)
├── domain/                # Entités et modèles métier purs (Track, MusicLibrary, MusicProfile)
├── services/              # Logique métier et cas d'utilisation
│   ├── ai_engine_service.py         # Métriques ONNX & orchestration de l'inférence
│   ├── audio_validation_service.py  # Validation audio unifiée fleep + ffprobe
│   ├── database_service.py          # Gestion LanceDB & indexation des embeddings
│   ├── library_service.py           # Parcours récursif & scan de dossiers
│   ├── playback_service.py          # Lecture externe multiplateforme & explorateur
│   ├── playlist_export_service.py   # Génération et écriture des fichiers .m3u8
│   └── playlist_service.py          # Orchestration MMR et lancement de lecture
├── providers/             # Fournisseurs d'infrastructure IA (MusiCNN ONNX, LanceDB)
├── repositories/          # Abstraction de la persistance des données
├── controllers/           # Contrôleurs UI ↔ Services métier
├── ui/                    # Interface graphique utilisateur (Flet)
│   ├── components/        # Composants réutilisables (HeaderBar, ResultDialog, TrackItem...)
│   ├── design_system/     # Design Tokens (Thème Obsidian Horizon, typographie, couleurs)
│   └── views/             # Vues principales (LibraryView, AIMetricsView, SettingsView)
├── utils/                 # Utilitaires système et détection audio
├── tools/                 # Outils annexes et scripts de capture
│   └── capture/           # Outil de capture HD/4K automatisée via Playwright
├── tests/                 # Suite de tests automatisés (107 tests unitaires)
│
├── main.py                # Point d'entrée de l'application desktop
├── extraction.py          # Moteur algorithmique (FFmpeg, spectrogrammes Mel, MMR vectorisé)
├── pyproject.toml         # Configuration du projet Python (PEP 621) et dépendances uv
└── requirements.txt       # Dépendances pip alternatives
```

---

## Technologies et composants

| Composant | Technologie | Rôle |
|---|---|---|
| **Interface graphique** | Flet (Flutter engine) | Rendu UI natif multiplateforme |
| **Inférence IA** | ONNX Runtime | Exécution locale du modèle `msd-musicnn-1.onnx` |
| **Modèle acoustique** | MusiCNN | Extraction de vecteurs d'embeddings (200 dimensions) |
| **Base vectorielle** | LanceDB | Stockage local sur disque et requêtes vectorielles |
| **Recommandation** | Maximum Marginal Relevance | Classement vectorisé NumPy (arbitrage similarité / nouveauté) |
| **Hachage & Intégrité** | BLAKE3 | Hachage cryptographique ultra-rapide anti-doublon |
| **Validation média** | FFprobe + Fleep | Détection de conteneurs et flux audio valides |
| **Lecteur multimédia** | VLC Media Player (ou OS par défaut) | Lecture externe des playlists et pistes audio |
| **CI / CD & Tests** | GitHub Actions + pytest | Validation continue, linting et compilation automatisée |

---

## Prérequis

1. **Python 3.12** : version de référence du projet (`>=3.12, <3.13`), requise pour l'environnement `uv`, la suite de tests et le packaging desktop.
2. **FFmpeg & FFprobe** : requis dans le `PATH` système pour le décodage audio et la validation des flux multimédias.
3. **VLC Media Player** *(optionnel mais recommandé)* : permet le lancement direct de playlists complexes. En son absence, AIC bascule automatiquement sur le lecteur de médias associé par défaut par le système d'exploitation.

---

## Installation pour le développement

Le gestionnaire de paquets officiel et recommandé pour AIC est [**uv**](https://docs.astral.sh/uv/).

### 1. Cloner le dépôt

```bash
git clone https://github.com/Flex1-tech/AIC-Audio-Intelligence-Companion.git
cd AIC-Audio-Intelligence-Companion
```

### 2. Installation avec `uv` (recommandé)

`uv` synchronise automatiquement l'environnement virtuel avec le fichier de verrouillage `uv.lock` :

```bash
# Installer les dépendances de production et de développement
uv sync --group dev

# Lancer l'application
uv run python main.py
```

### 3. Installation alternative avec `venv` et `pip`

```bash
# Windows (avec Python 3.12)
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS (avec Python 3.12)
python3.12 -m venv .venv
source .venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Lancement
python main.py
```

---

## Tests et Qualité de code

La suite de tests automatisée comprend **107 tests unitaires** couvrant l'ensemble des modules critiques (extraction audio, MMR vectorisé, non-redondance BLAKE3, scan conditionnel ffprobe, export M3U8, lecture externe et splash screen).

### Exécuter la suite de tests

```bash
uv run pytest tests/ -v
```

### Vérification de la qualité de code (pre-commit)

Le projet applique des règles strictes de formatage et d'analyse statique via `pre-commit` (`black`, `flake8`, `autoflake`, `check-yaml`, `check-toml`) :

```bash
# Installer les hooks git locaux
uv run pre-commit install

# Exécuter les contrôles sur tous les fichiers
uv run pre-commit run --all-files
```

---

## Scan, Importation et Validation Multimédia

Le scan de bibliothèque et l'import de fichiers individuels partagent un pipeline unifié dans `AudioValidationService` :

```text
Sélection (Fichiers ou Dossier)
           │
           ▼
1. Validation d'extension & existence fichier
           │
           ▼
2. Empreinte BLAKE3 + Consultation LanceDB
   ├── Si déjà indexé en base ──────────────► [BYPASS ffprobe] (gain I/O immédiat)
   └── Si nouveau fichier / non indexé :
           │
           ▼
3. Vérification de format MIME (Fleep)
           │
           ▼
4. Validation de flux audio actif (ffprobe -select_streams a:0)
           ├── Flux audio présent ──────────► [VALIDÉ] (Import / Extraction)
           └── Aucun flux audio ────────────► [REJETÉ] (Fichier ignoré sans plantage)
```

Grâce à cette approche, les conteneurs vidéo contenant une piste audio (ex. fichiers `.mp4` ou `.webm` issus d'archives musicales) sont scannés et importés de manière transparente.

---

## Lecture Externe et Playlists M3U8

AIC centralise la lecture externe dans `PlaybackService` (`services/playback_service.py`), garantissant une expérience fluide sans jamais bloquer l'interface Flet :

* **Lecture de Playlist** :
  * Recherche VLC dans le `PATH` et les répertoires standards d'installation (`Program Files\VideoLAN\VLC`, `/Applications/VLC.app`, `/usr/bin/vlc`).
  * Si VLC est absent ou en cas d'erreur de lancement, repli transparent et explicite vers le lecteur média par défaut de l'OS.
* **Lecture de Piste** :
  * Windows : `os.startfile(norm_path)`
  * macOS : `subprocess.Popen(["open", norm_path])`
  * Linux : `xdg-open` avec repli sur `gio open`
* **Dialogue « Ouvrir avec… »** :
  * Windows : dialogue natif système `rundll32.exe shell32.dll,OpenAs_RunDLL`
  * macOS : invite native d'application AppleScript (`choose application`)
  * Linux : sélecteur graphique `zenity` ou `kdialog`
* **Gestionnaire de fichiers** :
  * Windows : sélection directe via `explorer.exe /select,norm_path`
  * macOS : sélection directe dans le Finder via `open -R norm_path`
  * Linux : sélection directe (`nautilus`, `dolphin`, `nemo`) avec repli sur l'ouverture du dossier parent

> [!NOTE]
> **Statut de validation multiplateforme** : Le comportement des commandes système sous Windows, Linux et macOS est entièrement couvert par des tests unitaires mockés et validé sur l'environnement d'intégration continue Ubuntu Linux (`ci-lint.yml`). Les interactions avec les environnements de bureau graphiques spécifiques sous macOS natif et diverses distributions Linux peuvent faire l'objet de validations manuelles d'agrément.

---

## Outil de Capture Automatisée (HD / 4K / Vidéo)

Pour générer des captures d'écrans haute fidélité (PNG) et des enregistrements vidéo (WebM) sans artefacts système ni bordures de fenêtres, AIC intègre un outil automatisé dans `tools/capture/` :

* **Emplacement** : `tools/capture/capture_app.py`
* **Dépendances optionnelles** : `playwright` et `pillow`.

### Installation des dépendances de capture

```bash
uv run pip install playwright pillow
uv run playwright install chromium
```

### Utilisation de l'outil

```bash
# Capture de tous les écrans en Full HD (1920×1080)
uv run python tools/capture/capture_app.py --full-hd --all

# Capture de référence en 4K Ultra HD (3840×2160)
uv run python tools/capture/capture_app.py --4k --all

# Enregistrement vidéo haute fidélité du Splash Screen
uv run python tools/capture/capture_app.py --splash-video --full-hd
```

Les captures générées sont enregistrées dans le répertoire `tools/capture/output/`.

---

## Optimisations et état actuel

Dans le cadre des derniers jalons de performance, plusieurs optimisations majeures ont été intégrées et validées :

| Optimisation | Description technique | Bénéfice mesuré |
|---|---|---|
| **Vectorisation MMR** | Remplacement de la boucle quadratique par calcul matriciel cosinus NumPy $O(N)$ par itération | Classement de 1 000 candidats en **< 5 ms** contre plusieurs centaines de ms auparavant |
| **BLAKE3 non redondant** | Transmission du dictionnaire des empreintes précalculées à l'import lors de la recommandation | **Zéro lecture disque I/O supplémentaire** lors de la génération de playlists |
| **Bypass `ffprobe` au scan** | Court-circuitage des processus ffprobe pour tout fichier dont le hash et la taille figurent dans LanceDB | Temps de rescan de bibliothèque réduit d'environ **90 %** sur les collections volumineuses |
| **Extraction audio parallèle** | Décodage FFmpeg avec `-threads 0` et calcul vectorisé du Zero Crossing Rate (ZCR) | Accélération de **25 à 30 %** de l'extraction des spectrogrammes audio |
| **Démarrage léger (Lazy Loading)** | Importation différée de LanceDB, ONNXRuntime et scikit-learn au premier besoin | Lancement de l'interface graphique en **< 500 ms** sans blocage initial |

---

## Limitations connues et perspectives

* **Indexation initiale séquentielle** : Lors de l'import de nouveaux morceaux non indexés, le calcul des spectrogrammes s'exécute séquentiellement fichier par fichier. La parallélisation multi-cœur via un pool de processus est planifiée pour les versions ultérieures.
* **Surveillance en temps réel** : La mise à jour de la bibliothèque repose actuellement sur une action explicite de scan. La détection automatique en arrière-plan des modifications de fichiers (`watch_service`) fait partie de la feuille de route v3.0.
* **Environnements graphiques Linux exotiques** : Si aucun utilitaire standard (`zenity`, `kdialog`, `xdg-open`) n'est présent sur une distribution Linux minimale, l'utilisateur est invité via un message explicite à sélectionner manuellement son lecteur.

---

## CI / CD et Builds Desktop

Le dépôt s'appuie sur GitHub Actions pour tester et compiler les livrables :

| Workflow | Rôle |
|---|---|
| `ci-lint.yml` | Linting Flake8, vérification des imports et exécution de pytest à chaque PR/push |
| `build-desktop.yml` | Compilation multiplateforme (Windows Inno Setup/ZIP, Linux AppImage, macOS DMG) lors des releases `v*` |
| `lock-update.yml` | Maintien et cohérence de `uv.lock` |

---

## License

Ce projet est distribué sous la licence **PolyForm Noncommercial 1.0.0**.
Elle autorise l'utilisation, la modification et la distribution du logiciel à des fins **non commerciales uniquement**.

Pour toute demande d'utilisation commerciale, contactez le titulaire des droits :
https://github.com/Flex1-tech
