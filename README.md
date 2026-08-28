# AIC — Audio Intelligence Companion

![GitHub Actions](https://img.shields.io/github/actions/workflow/status/Flex1-tech/AIC-Audio-Intelligence-Companion/build-desktop.yml?branch=main&label=CI%2FCD&logo=github-actions&logoColor=white)
![GitHub Release](https://img.shields.io/github/v/release/Flex1-tech/AIC-Audio-Intelligence-Companion?label=Release&logo=github)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-0.86%2B-blueviolet?logo=flutter&logoColor=white)
![AI](https://img.shields.io/badge/AI-MusiCNN-orange?logo=tensorflow&logoColor=white)
![ONNX Runtime](https://img.shields.io/badge/ONNX%20Runtime-005CED?logo=onnx&logoColor=white)
![LanceDB](https://img.shields.io/badge/LanceDB-0.21%2B-blue?logo=lancedb&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-MMR%20%7C%20Embeddings-brightgreen?logo=scikit-learn&logoColor=white)
![Music](https://img.shields.io/badge/Audio-FFprobe-red?logo=audiomack&logoColor=white)
![License](https://img.shields.io/badge/License-PolyForm%20Noncommercial%201.0.0-lightgrey)

> [!CAUTION]
> Ce logiciel est distribue sous la licence **PolyForm Noncommercial 1.0.0**.
> Toute utilisation commerciale est interdite sans autorisation explicite de l'auteur.
> Pour un usage commercial, veuillez contacter le titulaire des droits.

AIC (Audio Intelligence Companion) est une application de recommandation musicale fonctionnant entièrement hors ligne.

Elle analyse votre bibliothèque musicale locale à l'aide du modèle **MusiCNN**, extrait des représentations acoustiques, les indexe dans **LanceDB** puis génère des playlists personnalisées grâce à l'algorithme **Maximum Marginal Relevance (MMR)**.

L'application est développée en **Python** avec **Flet** et ne nécessite aucun service cloud pour fonctionner.

---

## Downloads

Les versions officielles pour **Windows**, **Linux** et **macOS** sont disponibles dans les GitHub Releases.

| Plateforme | Formats disponibles |
|---|---|
| Windows (x64) | Installateur (`AIC-Setup-vX.Y.Z.exe`) · Portable ZIP (`AIC-Portable-vX.Y.Z.zip`) |
| Linux (x64) | AppImage (`AIC-vX.Y.Z.AppImage`) |
| macOS (Apple Silicon) | DMG (`AIC-vX.Y.Z.dmg`) |

**Dernière release** : https://github.com/Flex1-tech/AIC-Audio-Intelligence-Companion/releases/latest

---

## Installer AIC

### Windows — Installateur (recommandé)

1. Télécharger `AIC-Setup-vX.Y.Z.exe` depuis les [Releases](https://github.com/Flex1-tech/AIC-Audio-Intelligence-Companion/releases/latest).
2. Exécuter l'installateur et suivre les étapes.
3. AIC est installé dans `Program Files` avec un raccourci Menu Démarrer.
4. Une entrée de désinstallation est créée dans les Paramètres Windows.

> [!NOTE]
> **Windows SmartScreen** : l'application n'est pas encore signée avec un certificat commercial. Cliquez sur **Informations complémentaires** puis **Exécuter quand même** si un avertissement apparaît.

### Windows — Version Portable

1. Télécharger `AIC-Portable-vX.Y.Z.zip`.
2. Extraire dans le répertoire de votre choix.
3. Double-cliquer sur `AIC.exe`.

La version portable ne modifie pas le système. Elle peut être exécutée depuis une clé USB ou tout répertoire sans installation.

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

> [!NOTE]
> L'AppImage est autonome. Elle ne nécessite pas d'installation. Elle peut être exécutée depuis n'importe quel répertoire.

### macOS — DMG

> [!IMPORTANT]
> AIC macOS est compilé exclusivement pour **Apple Silicon (arm64)**. Non compatible Mac Intel.

1. Télécharger `AIC-vX.Y.Z.dmg`.
2. Ouvrir le fichier DMG.
3. Glisser `AIC.app` dans le dossier **Applications**.
4. L'application n'étant pas notarisée, ouvrir via **clic droit → Ouvrir** au premier lancement.


---

## Features

* Analyse locale d'une bibliothèque musicale
* Recommandations basées sur MusiCNN
* Classement des morceaux avec Maximum Marginal Relevance (MMR)
* Base vectorielle locale LanceDB
* Fonctionnement 100 % hors ligne
* Interface graphique multiplateforme avec Flet

---

## Project Architecture

Le projet suit les principes de la **Clean Architecture** et du **Domain-Driven Design (DDD)**.

```text
AIC-Audio-Intelligence-Companion/
│
├── core/                  # État global de l'application
├── domain/                # Modèles métier
├── services/              # Logique applicative
├── providers/             # IA et services externes
├── repositories/          # Accès aux données
├── controllers/           # Orchestration UI ↔ Services
├── ui/                    # Interface Flet
├── utils/                 # Utilitaires
├── .github/workflows/     # CI/CD GitHub Actions
│
├── main.py
├── pyproject.toml
└── requirements.txt
```

### Structure

| Dossier         | Rôle                                                   |
| --------------- | ------------------------------------------------------ |
| `domain/`       | Entités et modèles métier                              |
| `services/`     | Logique métier                                         |
| `providers/`    | Intégration MusiCNN, ONNX Runtime et services externes |
| `repositories/` | Accès aux données et à LanceDB                         |
| `controllers/`  | Coordination entre l'interface et les services         |
| `ui/`           | Interface graphique Flet                               |
| `core/`         | État global de l'application                           |
| `utils/`        | Fonctions utilitaires                                  |

---

## Technologies

| Composant        | Technologie                      |
| ---------------- | -------------------------------- |
| Interface        | Flet                             |
| IA               | MusiCNN                          |
| Inférence        | ONNX Runtime                     |
| Base vectorielle | LanceDB                          |
| Recommandation   | Maximum Marginal Relevance (MMR) |
| Validation audio | FFprobe + Fleep                  |
| Lecteur audio    | VLC Media Player                 |
| CI/CD            | GitHub Actions                   |

---

## Requirements

* Python 3.10 ou supérieur
* VLC Media Player

---

## Installation

Cloner le dépôt :

```bash
git clone https://github.com/Flex1-tech/AIC-Audio-Intelligence-Companion.git
cd AIC-Audio-Intelligence-Companion
```

Créer un environnement virtuel :

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Lancer l'application :

```bash
python main.py
```

---

## Building

Le projet utilise **Flet Build** et **uv** pour générer des exécutables natifs.

### Prérequis

```bash
uv sync --group dev
```

### Build local

```bash
# Windows
uv run flet build windows --python-version 3.12 --yes

# Linux (sur Linux uniquement)
uv run flet build linux --python-version 3.12 --yes

# macOS (sur macOS uniquement, arm64)
uv run flet build macos --arch arm64 --python-version 3.12 --yes
```

Le bundle est généré dans `build/<plateforme>/`.

> [!IMPORTANT]
> Les builds de production sont exclusivement réalisés via GitHub Actions. Ne pas générer d'exécutables localement pour la distribution.

### Packaging local (Windows uniquement)

Pour générer l'installateur Inno Setup localement :

```powershell
# Installer Inno Setup : https://jrsoftware.org/isdl.php
iscc /DMyAppVersion="2.1.0" installer\AIC.iss
# Résultat : installer\Output\AIC-Setup-2.1.0.exe
```

Pour générer le ZIP portable :

```powershell
Compress-Archive -Path build\windows\* -DestinationPath AIC-Portable-v2.1.0.zip
```

---

## Development

Le projet utilise **pre-commit** pour automatiser les vérifications de qualité et de style de code localement avant chaque commit.

### Installation

```bash
uv sync --dev
uv run pre-commit install
```

### Vérification manuelle

```bash
uv run pre-commit run --all-files
```

### Vérifier un seul fichier

```bash
uv run pre-commit run --files path/to/file.py
```

### Mise à jour des hooks

```bash
uv run pre-commit autoupdate
```

Lorsque vous effectuez un commit, les hooks pre-commit s'exécutent automatiquement :
- Les erreurs de formatage ou d'imports inutilisés sont corrigées automatiquement lorsque c'est possible.
- Si des erreurs de style ou de syntaxe persistent, le commit est bloqué afin de corriger les problèmes.
- Cela garantit un code propre et évite l'échec des vérifications dans le pipeline GitHub Actions.

---

## Continuous Integration

Le dépôt utilise GitHub Actions pour automatiser les différentes tâches.

| Workflow | Déclencheur | Description |
|---|---|---|
| `ci-lint.yml` | Push `.py` sur `main`/`dev` | Lint Flake8 + Import check + pytest |
| `build-desktop.yml` | Push `main`, tag `v*`, `workflow_dispatch` | Build Windows + Linux + macOS, packaging, GitHub Release |
| `lock-update.yml` | Push `pyproject.toml` sur `main` | Synchronisation du `uv.lock` |

---

## Releases

Les versions officielles sont publiées automatiquement lors du push d'un tag Git `v*`.

### Convention de versionnement

```
pyproject.toml  → source de vérité de la version du projet
Tag Git v*      → déclencheur de la release officielle
```

Les deux doivent être cohérents. Le pipeline vérifie cette cohérence avant de publier.

### Procédure de release

```bash
# 1. Mettre à jour la version dans pyproject.toml
#    version = "X.Y.Z"

# 2. Committer et pousser sur main
git checkout main
git pull origin main
git add pyproject.toml
git commit -m "chore: bump version to vX.Y.Z"
git push origin main

# 3. Créer et pousser le tag
git tag vX.Y.Z
git push origin vX.Y.Z
```

Lorsqu'un tag `vX.Y.Z` est poussé, le pipeline :

1. Vérifie la cohérence tag ↔ `pyproject.toml`.
2. Construit les binaires Windows, Linux et macOS.
3. Génère l'installateur Inno Setup et le ZIP portable (Windows).
4. Génère l'AppImage (Linux).
5. Génère le DMG (macOS).
6. Crée une GitHub Release avec les 4 packages.
7. Utilise `RELEASE_NOTES_vX.Y.Z.md` comme corps de la Release.

### Packages publiés

| Plateforme | Fichier |
|---|---|
| Windows installer | `AIC-Setup-vX.Y.Z.exe` |
| Windows portable | `AIC-Portable-vX.Y.Z.zip` |
| Linux | `AIC-vX.Y.Z.AppImage` |
| macOS | `AIC-vX.Y.Z.dmg` |

### Release Notes

Les notes de chaque release sont documentées dans un fichier `RELEASE_NOTES_vX.Y.Z.md` à la racine du dépôt.

* **[Release Notes v2.1.0](./RELEASE_NOTES_v2.1.0.md)**

Ce fichier est utilisé tel quel comme corps de la GitHub Release. Il ne doit pas être modifié après publication.

---

## Contributing

Les contributions sont les bienvenues.

1. Forker le dépôt.
2. Créer une branche.
3. Développer la fonctionnalité.
4. Vérifier que les tests passent.
5. Ouvrir une Pull Request.

Merci de respecter l'architecture du projet et les conventions de code existantes.

---

## License

Ce projet est distribué sous la licence **PolyForm Noncommercial 1.0.0**.

Elle autorise l'utilisation, la modification et la distribution du logiciel à des fins **non commerciales uniquement**.

Toute utilisation commerciale est expressement interdite par cette licence.

Pour toute demande d'utilisation commerciale, contactez le titulaire des droits via :
https://github.com/Flex1-tech

Le texte integral de la licence est disponible dans le fichier [LICENSE](./LICENSE).
