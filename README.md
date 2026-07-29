# 🎵 AIC — Audio Intelligence Companion

**Audio Intelligence Companion (AIC)** est un assistant musical local d'intelligence artificielle, fonctionnant à 100 % hors-ligne. Il permet de scanner votre bibliothèque musicale locale, d'extraire des caractéristiques acoustiques grâce au réseau de neurones profond **MusiCNN (16 kHz)**, de stocker et d'indexer ces empreintes dans la base vectorielle locale **LanceDB**, et de générer des playlists intelligentes personnalisées basées sur l'algorithme **MMR (Maximal Marginal Relevance)**.

L'application offre une interface graphique moderne et élégante sous le thème **Obsidian**, construite avec **Flet (API 0.86+)**.

---

## 🏛 Architecture du Projet

Le projet respecte les principes de la **Clean Architecture** et du **Domain-Driven Design (DDD)** :

```text
Local_Recommendation_Engine/
├── core/                       # Gestion de l'état global et session applicative
│   └── state.py                # AppState réactif et journal d'actions (telemetry)
├── domain/                     # Modèles métier purs (dataclasses)
│   ├── track.py                # Entité Piste audio
│   ├── library.py              # Collection et filtres de la bibliothèque
│   ├── session.py              # Paramètres de session et configuration UI
│   └── history.py              # Modèle de log pour télémétrie AI
├── repositories/               # Accès aux données vectorielles
│   └── track_repository.py     # Requêtes LanceDB et hachage BLAKE3
├── providers/                  # Abstractions des services externes / ML
│   └── musicnn_provider.py     # Inférence ONNX Runtime pour MusiCNN (200 dimensions)
├── services/                   # Logique applicative métier
│   ├── ai_engine_service.py    # Service d'inférence vectorielle
│   ├── audio_validation_service.py # Validation FFprobe / Fleep
│   ├── database_service.py     # Connexion et gestion LanceDB
│   ├── library_service.py      # Balayage asynchrone des dossiers
│   └── playlist_service.py     # Recommandation MMR et export .m3u8
├── controllers/                # Orchestration entre l'UI et les services
│   ├── library_controller.py   # Ingestion, filtres et favoris (Likes)
│   └── recommendation_controller.py # Génération asynchrone de playlist
├── ui/                         # Interface utilisateur Flet 0.86+ (Obsidian Design)
│   ├── components/             # Composants réutilisables (HeaderBar, Sidebar, ActionBar, etc.)
│   ├── design_system/          # Thème, couleurs HSL tailleur, typographie
│   └── views/                  # Vues principales (LibraryView, AIMetricsView, SettingsView)
├── utils/                      # Utilitaires système et audio
│   └── audio_utils.py          # Utilitaires purs (ffprobe, fleep, détection VLC)
├── .github/workflows/          # Pipelines CI/CD automatisées avec `uv`
│   ├── build-desktop.yml       # Compilation multiplateforme (Windows, Linux, macOS)
│   ├── ci-lint.yml             # Validation statique (flake8, imports, pytest)
│   └── lock-update.yml         # Génération et synchronisation du fichier uv.lock
├── main.py                     # Point d'entrée Flet (ft.run)
├── pyproject.toml              # Métadonnées PEP 621, dépendances et config Flet Build
└── requirements.txt            # Liste explicite des dépendances Python
```

---

## 🛠 Technologies Utilisées

| Composant | Technologie | Rôle |
|---|---|---|
| **GUI** | [Flet 0.86+](https://flet.dev/) | Interface réactive moderne basée sur Flutter |
| **Inférence IA** | [ONNX Runtime](https://onnxruntime.ai/) | Exécution locale du modèle neuronal MusiCNN 16kHz |
| **Base Vectorielle** | [LanceDB](https://lancedb.com/) | Stockage et recherche de vecteurs d'embeddings (200D) |
| **Algorithme MMR** | [scikit-learn](https://scikit-learn.org/) | Diversification et pertinence du ranking musical |
| **Hachage & MIME** | BLAKE3 & Fleep | Identification unique et validation stricte du format audio |
| **Lecteur Audio** | VLC Media Player | Lecture externe de la playlist `.m3u8` générée |
| **CI/CD & Packaging** | `uv` & GitHub Actions | Déploiement et builds automatisés Windows/Linux/macOS |

---

## 🚀 Installation et Développement Local

### Prérequis
- **Python 3.10+** (Python 3.11 recommandé)
- **VLC Media Player** (installé sur le système pour l'écoute des playlists)

### 1. Cloner le dépôt
```bash
git clone https://github.com/Flex1-tech/Local_Recommendation_Engine.git
cd Local_Recommendation_Engine
```

### 2. Créer l'environnement virtuel et installer les dépendances
```bash
python -m venv .venv
# Sur Windows (PowerShell) :
.\.venv\Scripts\Activate.ps1
# Sur Linux / macOS :
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Lancer l'application
```bash
python main.py
```

---

## 🔨 Construction des Exécutables Desktop (Flet Build)

Pour builder l'application sous forme de binaire autonome (Windows `.exe`, Linux binaire, macOS `.app`) :

```bash
# Nécessite flet[build]
pip install "flet[build]>=0.86.0"

# Construire pour votre plateforme courante :
flet build windows
flet build linux
flet build macos
```

Les exécutables générés se trouvent dans le dossier `build/`.

---

## 🤖 Integration CI/CD (GitHub Actions + `uv`)

Le projet utilise **`uv`** (d'Astral) comme gestionnaire ultra-rapide dans les workflows CI/CD :

- **CI Lint & Tests** (`ci-lint.yml`) : Déclenché automatiquement sur chaque `push` sur les branches `main` et `dev`.
- **Desktop Builds** (`build-desktop.yml`) : Compile automatiquement les versions Windows, Linux et macOS sur chaque `push` vers `main`.
- **Mise à jour du lockfile** (`lock-update.yml`) : Maintient le fichier `uv.lock` synchronisé sans nécessiter d'installation locale de `uv`.
