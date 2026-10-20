# 📸 AIC — Système de Capture HD / 4K & Vidéo Automatisée (V2)

Outil automatisé de génération de captures haute fidélité (PNG) et d'enregistrements vidéo (WebM) pour **AIC (Audio Intelligence Companion)**.

Ce module garantit des visuels professionnels, déterministes et reproductibles pour la documentation, le README, le site web, les mockups et les démonstrations vidéo, sans bordures Windows ni barres d'adresse de navigateur.

---

## 🏗️ Architecture technique V2

Le système combine **Flet Web** et **Playwright (Chromium)** avec navigation sémantique et validation de contenu :

```text
               ┌────────────────────────────────────────────────────────┐
               │              capture_app.py (CLI V2)                   │
               └──────────────────────────┬─────────────────────────────┘
                                          │
               ┌──────────────────────────┴─────────────────────────────┐
               │           Serveur Flet Web Isolé                       │
               │         (FLET_FORCE_WEB_SERVER=1)                      │
               │             http://127.0.0.1:port                      │
               └──────────────────────────┬─────────────────────────────┘
                                          │ HTTP 200 Ready
               ┌──────────────────────────┴─────────────────────────────┐
               │            Playwright Chromium                         │
               │   • Arbre sémantique accessible Flutter                │
               │   • Navigation par rôle et label textuel               │
               │   • Assertion de contenu avant capture                 │
               │   • Enregistrement vidéo WebM natif                    │
               └──────────────────────────┬─────────────────────────────┘
                                          │
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
        ┌─────────────────────────┐               ┌─────────────────────────┐
        │     Screenshots 4K      │               │   Vidéo Splash Screen   │
        │ • aic-dashboard-4k.png  │               │ • aic-splash-4k.webm    │
        │ • aic-telemetry-4k.png  │               │ • aic-splash-fullhd.webm│
        │ • aic-settings-4k.png   │               └─────────────────────────┘
        └─────────────────────────┘
```

---

## 📦 1. Installation des prérequis

### Dépendances de développement (`uv`)

Playwright est configuré comme dépendance de développement dans le groupe `dev` de `pyproject.toml` :

```powershell
uv sync --group dev
```

### Installation du binaire Chromium

Installez les binaires du navigateur Chromium gérés par Playwright :

```powershell
uv run playwright install chromium
```

---

## 🚀 2. Utilisation

### Capture 4K Ultra HD (3840×2160 PNG) — Recommandé

Génère une capture de référence du tableau de bord principal à `3840×2160` (Viewport CSS `1920×1080` avec `device_scale_factor=2`) :

```powershell
uv run python tools/capture/capture_app.py --4k
```

### Capture de tous les écrans applicatifs (Dashboard, Telemetry, Settings)

Génère l'ensemble des vues clés de l'application statique avec assertion de contenu :

```powershell
uv run python tools/capture/capture_app.py --4k --all
```

### Capture Full HD (1920×1080 PNG)

```powershell
uv run python tools/capture/capture_app.py --full-hd
```

### Capture d'un écran spécifique

```powershell
# Tableau de bord / Bibliothèque musicale
uv run python tools/capture/capture_app.py --4k --screen dashboard

# Écran de télémétrie & métriques IA
uv run python tools/capture/capture_app.py --4k --screen telemetry

# Écran des réglages
uv run python tools/capture/capture_app.py --4k --screen settings
```

---

## 🎬 3. Enregistrement Vidéo du Splash Screen

Le Splash Screen d'AIC étant une animation complète (~5.0s, éveil de l'onde ambre, logo Cinzel Decorative, transition fondu), il est capturé en vidéo WebM haute fidélité depuis `t=0` jusqu'à la transition sur l'interface principale :

```powershell
# Enregistrement vidéo Splash en 4K Ultra HD
uv run python tools/capture/capture_app.py --splash-video --4k

# Enregistrement vidéo Splash en Full HD
uv run python tools/capture/capture_app.py --splash-video --full-hd
```

---

## ⚙️ 4. Options CLI

| Argument | Description | Valeur par défaut |
| :--- | :--- | :--- |
| `--4k` | Active le preset 4K (3840×2160) | `False` |
| `--full-hd` | Active le preset Full HD (1920×1080) | `False` |
| `--splash-video` | Active l'enregistrement vidéo WebM de l'animation Splash | `False` |
| `--all` | Capture l'ensemble des écrans statiques (`dashboard`, `telemetry`, `settings`) | `False` |
| `--screen` | Écran ciblé (`dashboard`, `telemetry`, `settings`) | `dashboard` |
| `--output-dir` | Répertoire de destination | `tools/capture/output` |
| `--filename` | Nom personnalisé du fichier de sortie | Calculé automatiquement |
| `--headed` | Affiche la fenêtre Chromium (débogage visuel) | `False` (Headless) |
| `--port` | Port TCP Flet (0 = allocation dynamique automatique) | `0` |
| `--timeout` | Timeout global en secondes | `45.0` |
| `--wait-splash` | Délai d'attente maximum pour le splash screen | `6.5` |

---

## 📂 5. Répertoire de sortie

Tous les screenshots et vidéos générés sont enregistrés dans :

```text
tools/capture/output/
```

Fichiers types générés :
- `aic-dashboard-4k.png` (3840×2160 PNG)
- `aic-telemetry-4k.png` (3840×2160 PNG)
- `aic-settings-4k.png` (3840×2160 PNG)
- `aic-splash-4k.webm` (3840×2160 WebM)
- `aic-splash-fullhd.webm` (1920×1080 WebM)

> [!NOTE]
> Le contenu du dossier `tools/capture/output/*.png` et `*.webm` est automatiquement ignoré par `.gitignore` afin de ne pas alourdir l'historique Git.

---

## 🔍 6. Garanties de Fidélité V2

1. **Navigation 100% Sémantique** : Aucun clic par coordonnées `(x, y)`. Les onglets sont ciblés via leur rôle accessible et leur label (`Bibliothèque`, `Télémétrie`, `Réglages`).
2. **Assertion de Contenu** : Avant chaque capture, le script vérifie la présence de mots-clés distinctifs de la vue cible. Une incohérence interrompt le script et ne génère aucune image erronée.
3. **Validation Binaire Automatisée** :
   - Dimensions vérifiées au pixel près via Pillow (PNG) et en-têtes EBML (WebM).
   - Rejet automatique des images noires ou vides.
