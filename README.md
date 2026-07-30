# AIC — Audio Intelligence Companion

![GitHub Actions](https://img.shields.io/github/actions/workflow/status/Flex1-tech/Local_Recommendation_Engine/build-desktop.yml?branch=main&label=CI%2FCD&logo=github-actions&logoColor=white)
![GitHub Release](https://img.shields.io/github/v/release/Flex1-tech/Local_Recommendation_Engine?label=Release&logo=github)
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

Les versions compilées pour **Windows**, **Linux** et **macOS** sont disponibles dans les GitHub Releases.

**Latest release**

https://github.com/Flex1-tech/Local_Recommendation_Engine/releases/latest

**All releases**

https://github.com/Flex1-tech/Local_Recommendation_Engine/releases

---

## Lancer l'application depuis les binaires téléchargés

Les binaires publiés sont prêts à être exécutés et ne nécessitent pas l'installation de Python.

| Plateforme | Archive | Exécutable |
|----------------------|------------------------------|------------|
| Windows (x64) | `AIC-<version>-Windows-x64.zip` | `AIC.exe` |
| Linux (x64) | `AIC-<version>-Linux-x64.zip` | `AIC` |
| macOS (Apple Silicon) | `AIC-<version>-macOS-arm64.zip` | `AIC.app` |

Téléchargez l'archive correspondant à votre plateforme depuis la [dernière Release](https://github.com/Flex1-tech/Local_Recommendation_Engine/releases/latest).

### Windows

1. Télécharger l'archive `AIC-<version>-Windows-x64.zip` depuis la page [Releases](https://github.com/Flex1-tech/Local_Recommendation_Engine/releases/latest).
2. Extraire l'archive ZIP.
3. Ouvrir le dossier extrait.
4. Double-cliquer sur `AIC.exe`.

> [!NOTE]
> **Windows Defender / SmartScreen** : Il est normal qu'un avertissement apparaisse pour une application distribuée sans certificat de signature. Pour continuer, cliquez sur **Informations complémentaires** puis sur **Exécuter quand même**.
> Lors du premier lancement, Windows ou votre antivirus peut analyser l'application. Attendez simplement que cette analyse soit terminée.

### Linux

1. Télécharger l'archive `AIC-<version>-Linux-x64.zip` depuis la page [Releases](https://github.com/Flex1-tech/Local_Recommendation_Engine/releases/latest).
2. Extraire l'archive.
3. Si nécessaire, attribuer les permissions d'exécution :
   ```bash
   chmod +x AIC
   ```
4. Lancer l'application :
   ```bash
   ./AIC
   ```
   *(Un double-clic sur le binaire `AIC` fonctionne également selon votre environnement de bureau).*

> [!NOTE]
> Les binaires Linux ont été construits sur Ubuntu 22.04 et requièrent GTK 3 (`libgtk-3-0`) ainsi que `mpv` pour la lecture audio. Ces paquets sont généralement disponibles dans les gestionnaires de paquets des distributions courantes.

### macOS

> [!IMPORTANT]
> Les binaires macOS sont générés exclusivement pour l'architecture **Apple Silicon (arm64)**. Ils ne sont pas compatibles avec les Mac à processeur Intel.

1. Télécharger l'archive `AIC-<version>-macOS-arm64.zip` depuis la page [Releases](https://github.com/Flex1-tech/Local_Recommendation_Engine/releases/latest).
2. Extraire l'archive.
3. L'application n'étant pas signée avec un certificat Apple, ouvrez-la via :
   - **Clic droit** (ou `Control` + clic) sur `AIC.app`
   - Sélectionner **Ouvrir**
   - Confirmer l'ouverture dans la fenêtre d'avertissement Gatekeeper.


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
Local_Recommendation_Engine/
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
git clone https://github.com/Flex1-tech/Local_Recommendation_Engine.git
cd Local_Recommendation_Engine
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

Le projet utilise **Flet Build** pour générer des exécutables natifs.

Exemple :

```bash
flet build windows
```

ou

```bash
flet build linux
```

ou

```bash
flet build macos
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

| Workflow      | Description                          |
| ------------- | ------------------------------------ |
| CI            | Vérification du code et des tests    |
| Desktop Build | Compilation Windows, Linux et macOS  |
| Release       | Publication automatique des versions |
| Lock Update   | Synchronisation du fichier `uv.lock` |

---

## Releases

Les versions officielles sont publiées automatiquement à partir d'un tag Git.

Créer une nouvelle version :

```bash
git checkout main
git pull origin main

git tag v2.0.1
git push origin v2.0.1
```

Lorsqu'un tag `v*` est poussé :

1. Les builds Windows, Linux et macOS sont exécutés.
2. Les exécutables sont générés.
3. Une GitHub Release est créée automatiquement.
4. Les notes de version sont générées automatiquement.
5. Les exécutables sont attachés à la Release.

Les binaires sont ensuite disponibles dans :

https://github.com/Flex1-tech/Local_Recommendation_Engine/releases

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
