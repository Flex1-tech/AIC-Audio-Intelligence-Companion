# AIC v2.1.0 — Release Notes

## 1. Nouveautés & Expérience Utilisateur

### Splash Screen Validé & Intégration SVG Transparente
Intégration et validation officielle de l'écran de démarrage basé sur l'architecture validée de `origin/main` (`af092ec`), enrichie d'actifs vectoriels SVG transparents :
- **Architecture vectorielle multi-couches** : séparation propre du logo en deux calques SVG transparents sans fond noir :
  - `layer_letterform.svg` : structure Cyan (`#30C4EF`) du logo "A".
  - `layer_wave.svg` : onde sonore Ambre (`#FE8F40`) composée de 71 tracés vectoriels.
- **Composition & Dimensionnement Responsive** :
  - Fond sombre Obsidian Horizon (`#0F1117`).
  - Redimensionnement automatique à 65 % de la plus petite dimension de la fenêtre (clampé entre 300 px et 560 px).
- **Animation & Timing (Séquence 5,0 secondes)** :
  - Animation par faisceau de balayage ambre horizontal (`wave_glow`) et impulsion de halo lumineux.
  - Séquencement centralisé dans `SPLASH_ANIMATION_CONFIG` (`total_ms = 5000`).
  - Fondu de sortie fluide (400 ms) vers l'interface principale.
- **Préchargement non bloquant** : chargement asynchrone du modèle IA MusiCNN ONNX et de la base LanceDB exécuté en arrière-plan via un thread démon (~2,5s à 3,6s) sans bloquer l'affichage de l'UI.

### Typographie de Branding (Cinzel Decorative)
Adoption de la famille typographique **Cinzel Decorative** pour l'identité visuelle de la marque AIC :
- **Hiérarchie typographique** : utilisation de `Cinzel Decorative Bold` pour le titre principal "AIC" et `Cinzel Decorative Regular` pour les sous-titres et cartes d'identité.
- **Intégration locale TrueType (.ttf)** : fichiers de polices embarqués directement dans `assets/fonts/` sans dépendance réseau.

---

## 2. Design System & Normalisation UI

### Refonte du Système de Thèmes Obsidian Horizon
- **Harmonisation sémantique des jetons** : alignement complet des couleurs de marque (`ObsidianColors.PRIMARY`, `SURFACE_CONTAINER`, `ON_SURFACE_VARIANT`).
- **Composants UI normalisés** : révision des composants graphiques (`action_bar`, `header_bar`, `sidebar`, `track_item`, `library_view`, `settings_view`, `ai_metrics_view`) pour garantir une cohérence visuelle optimale.
- **Modules de Tokens** : ajout et normalisation des modules de jetons d'élévation (`elevation.py`) et de mouvement (`motion.py`) dans le Design System.
- **Conformité WCAG AAA** : ajustement des contrastes visuels (notamment sur les alertes et boutons d'action).

---

## 3. Stabilité Desktop & Architecture Système

### Localisation & Données Utilisateur Multi-Plateformes
- **`utils/path_utils.py`** : résolution déterministe des chemins d'assets (`get_asset_path`) assurant le fonctionnement en mode développement (`flet run`), en bundle Flet et en binaire.
- **Stockage OS standard** : gestion des bases de données et des logs selon les répertoires applicatifs standards OS (`%APPDATA%\AIC` sur Windows, `~/.local/share/AIC` sur Linux, `Application Support` sur macOS).
- **Journalisation & Interception des erreurs** : intercepteurs globaux `sys.excepthook` et `threading.excepthook` prévenant les fermetures silencieuses, associés à un écran de secours au démarrage et à la génération automatique des logs dans `logs/aic.log`.

---

## 4. Nettoyage Conservateur du Dépôt

Dans le cadre de cette release, un nettoyage rigoureux des artefacts et dossiers temporaires d'expérimentation a été réalisé :
- **Laboratoires et prototypes supprimés** : suppression des répertoires temporaires d'essais `tests/splash_demo/` et `tests/splash_comparison/`.
- **Rapports d'audit temporaires supprimés** : nettoyage des fichiers Markdown temporaires issus des phases d'investigation (`SPLASH_MAIN_REFERENCE_AUDIT.md`, `SPLASH_ARCHITECTURE_AUDIT.md`, `SPLASH_V3_AUDIT.md`, `V3_REFACTOR_REPORT.md`, etc.).
- **Artefacts d'extractions nettoyés** : suppression des dossiers temporaires d'extraction de builds situés sous `assets/`.

---

## 5. Qualité, Tests & Intégration Continue

### Contrôle Qualité et Tests Unitaires
- **Suite de tests pytest** : 100 % de réussite sur les tests unitaires et de non-régression (`uv run pytest` : **19 / 19 PASSED**).
- **Conformité de style et linting** : validation intégrale des accroches pre-commit (`uv run pre-commit run --all-files` : **100% PASSED** sous Black, Flake8, Autoflake, Check-YAML et Trailing-Whitespace).

### Stratégie de Compilation CI/CD
- **Zéro build local** : aucun exécutable (`.exe` / `pyinstaller` / `flet build`) n'a été généré localement.
- **Compilation GitHub Actions** : la génération et la publication des exécutables multi-plateformes (Windows, Linux, macOS) restent confiées exclusivement au pipeline d'intégration continue GitHub Actions (`.github/workflows/build-desktop.yml`).

---

## 6. Synthèse

La version 2.1.0 d'AIC apporte la validation finale du Splash Screen vectoriel responsive avec ses assets transparents, une typographie de marque embarquée, une normalisation complète du Design System Obsidian Horizon, un nettoyage approfondi du dépôt et une garantie de stabilité Desktop multi-plateforme validée par la suite de tests unitaires.
