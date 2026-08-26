# Livrable d'Investigation Architectural & Recalage Visuel — Splash Screen AIC

> **Production (`ui/components/splash_screen.py`)** : STRICTEMENT INTACTE — AUCUNE MODIFICATION DE PRODUCTION.  
> **Source de vérité visuelle** : Prototypes Flet exécutables dans `tests/splash_preview/` (Flet Web).  
> **Aucune génération d'images** : Basé exclusivement sur le rendu Flet réel.

---

## A. Architecture Cible Proposée

L'architecture cible reconstruit l'intention visuelle originale : **« AIC est en train de s'allumer »**.

Elle réconcilie la **fondation visuelle et le rythme réactif de OLD v1** avec les **vrais calques SVG vectoriels officiels de NEW v2** :

```
                                  AIC Logo Vectoriel
                                          │
                             ┌────────────┴────────────┐
                             │                         │
                        LETTERFORM                  WAVE
                           SVG                       SVG
                       Cyan #30C4EF             Ambre #FE8F40
                   (Structure A - 3 paths)   (Onde Audio - 70 paths)
                             │                         │
                             └────────────┬────────────┘
                                          │
                                     COMPOSITION
                               Stack viewBox 1024x1024
                                          │
                                      HALO V1
                              (BoxShadow Ambre Pulsant)
                                          │
                                OBSIDIAN BACKGROUND
                               (BG_DARK #0F1117 + Glow)
                                          │
                                RESPONSIVE SCALING
                              (Clamp Harmonieux 140-220px)
                                          │
                                   ~2.3 secondes
                                          │
                                          ↓
                                     MAIN LAYOUT
```

---

## B. Matrice de Comparaison Chronologique

| FEATURE | V1 (OLD) | V2 (NEW) | V3 (Actuel) | TARGET (Cible) | RAISON |
|---------|----------|----------|-------------|----------------|--------|
| **Source Logo** | `icon.svg` d'un bloc | `layer_letterform` + `layer_wave` | `icon.svg` d'un bloc | **`layer_letterform` + `layer_wave`** | Respecte l'art vectoriel officiel AIC sans duplication. |
| **Onde Audio** | 5 barres Flet `Container` | SVG `layer_wave` (70 paths) + scanner | 5 barres Flet `Container` (synthetiques) | **Vraie onde SVG (`layer_wave.svg`)** | Élimine la re-création Flet artificielle. L'onde officielle possède 70 tracés vectoriels fins. |
| **Couleur Signal** | Ambre `#FE8F40` | Ambre `#FE8F40` | Ambre `#FE8F40` | **Ambre `#FE8F40`** | Conformité avec `THEMING.md` (Ambre = Audio/Signal/Énergie). |
| **Couleur Lettre** | Blanc / Inclus | Cyan `#30C4EF` | Blanc / Inclus | **Cyan `#30C4EF`** | Conformité avec `THEMING.md` (Cyan = Intelligence IA/Structure). |
| **Animation Onde** | Variations de hauteur (8->32px) | Scanner horizontal (5s) | Variations de hauteur (12->45px) | **Opacité & Révélation lumineuse (~2.3s)** | Éveil réactif de l'onde sans faisceau scanner démonstratif. |
| **Lumière / Halo** | `BoxShadow` Ambre pulsant | `BoxShadow` + Faisceau gradient | `BoxShadow` Ambre pulsant | **`BoxShadow` Ambre pulsant V1** | C'est l'impulsion lumineuse originale qui donne la sensation "AIC s'allume". |
| **Format Structure** | Carte 100x100px | Conteneur ouvert 65% | Carte clamp(110, min*0.22, 165)px | **Prototypage double (A: Ouvert / B: Carte)** | Tester en laboratoire quelle structure restitue le mieux l'immersion. |
| **Taille Logo** | 64px fixe | 300–560px | 63–95px (dans carte 165px max) | **140–220px réactif** | Évite le logo minuscule et le logo géant. Respire dans la fenêtre. |
| **Typographie** | Système Bold | Cinzel Decorative (Sérif) | Système Bold | **Système Bold** | Lisibilité instantanée à haute vitesse (~2.3s). |
| **Durée** | ~2.3s | ~5.0s | ~2.3s (`SPLASH_ANIMATION_DURATION_MS`) | **~2.3s (Paramétrable)** | Rapidité et réactivité au démarrage applicatif. |
| **Fond** | Obsidian `#0F1117` | Obsidian + Radial Gradient | Obsidian + Radial Gradient | **Obsidian `#0F1117` + Radial Gradient** | Atmosphere sombre Obsidian Horizon pure. |

---

## C. Inventaire des Assets Réellement Présents

| Asset | Dimension / viewBox | Couleur Native | Statut Historique | Rôle & Décision Target |
|-------|----------------------|----------------|-------------------|------------------------|
| `assets/layer_letterform.svg` | `1024x1024` (3 paths) | Cyan `#30C4EF` | Introduit dans V2 (`855e481`) | **RÉINTÉGRÉ**. Calque officiel de la lettre "A" / "AIC". |
| `assets/layer_wave.svg` | `1024x1024` (70 paths) | Ambre `#FE8F40` | Introduit dans V2 (`855e481`) | **RÉINTÉGRÉ**. Calque officiel du signal sonore vectoriel. |
| `assets/icon.svg` | `1024x1024` (1 path) | Multi | V1 & Fallback | **Fallback 1** (si calques séparés non trouvés). |
| `assets/icon.png` | `1024x1024` (Raster) | Multi | Fallback OS | **Fallback 2** (si SVG non supporté). |
| `assets/fonts/CinzelDecorative-*.ttf` | Vector TTF | N/A | Introduit V2 | Écarté (police système préférée pour le Splash). |

---

## D. Décisions d'Ingénierie Visual & Technique

### 1. Calques SVG
- `layer_letterform.svg` et `layer_wave.svg` partagent la **même viewBox `0 0 1024 1024`**.
- Placés dans un `ft.Stack(width=size, height=size)`, leur alignement géométrique est **mathématiquement parfait sans décalage**.

### 2. Rapport d'Investigation Noise / Grain
- **Recherche exhaustive** dans `assets/`, `.git/`, history log, design system et code CSS/Flet.
- **Résultat** : Aucun asset de texture bruit ou grain (`noise.png`, `grain.png`) n'a **jamais existé dans le projet**.
- **Décision** : Aucun bruit artificiel n'est généré. Le fond utilise la couleur officielle Obsidian Horizon `ObsidianColors.BG_DARK` (`#0F1117`) sublimée par un gradient ambiant radial `ft.RadialGradient`.

### 3. Scaling Responsive (Fin de la "Petite Carte 165px")
- Formule d'échellonnement : `logo_size = clamp(140, min(viewport_w, viewport_h) * 0.26, 220)`.
- Évite l'effet "petite carte de chargement" sur écran 1920x1080 sans jamais occuper 80% de l'écran.

### 4. Structure (Carte vs Ouvert)
- Deux prototypes ont été construits dans le laboratoire `tests/splash_preview/splash_variants.py` :
  - `SplashV3Vector` (Hypothèse A : Composition ouverte sans carte rigide).
  - `SplashV3VectorCard` (Hypothèse B : Carte Obsidian Surface `#161922` avec coins arrondis).

### 5. Timing
- Constante centralisée : `SPLASH_ANIMATION_DURATION_MS = 2300` ms.
- Dérivation des phases au prorata pour conserver la cohérence temporelle en cas de changement de durée.

---

## E. Prototypes du Laboratoire (`tests/splash_preview/`)

Le laboratoire contient désormais les prototypes exécutables Flet Web :

```bash
uv run flet run tests/splash_preview/main.py --web --port 8570
```

1. **`★ Cible A — Vectoriel Ouvert` (`SplashV3Vector`)** : Superposition directe des calques SVG officiels (`letterform` Cyan + `wave` Ambre 70 paths) dans un espace ouvert réactif avec halo ambre.
2. **`★ Cible B — Vectoriel Carte Obsidian` (`SplashV3VectorCard`)** : Superposition des calques SVG officiels dans une carte Obsidian Surface responsive.
3. **`Production Actuelle (V3)` (`SplashProduction`)** : Pour comparaison directe sans toucher au code de production.

---

## F. Tests et Vérifications Prévisibles

1. `test_responsive_dimensions_small_viewport` : Vérification des bornes min `logo_size >= 140`.
2. `test_responsive_dimensions_large_viewport` : Vérification des bornes max `logo_size <= 220`.
3. `test_vector_svg_assets_resolution` : Résolution des calques `layer_letterform.svg` et `layer_wave.svg`.
4. `test_animation_timing_recalculation` : Valider la dérivation temporelle selon `SPLASH_ANIMATION_DURATION_MS`.
5. Run `uv run pytest` -> 100% PASS.
6. Run `uv run pre-commit run --all-files` -> 100% PASS.
7. Run `uv run flet run main.py` -> Validation du boot binaire réel et transition `MainLayout`.

---

## G. Risques Identifiés & Prévention

- **Risque** : Non-résolution des chemins d'assets en mode binaire PyInstaller.  
  **Prévention** : Utilisation de `get_asset_path()` avec fallback à 3 niveaux : `layer_letterform`+`layer_wave` -> `icon.svg` -> `ft.Icons.GRAPHIC_EQ`.
- **Risque** : Modification de la production avant validation.  
  **Prévention** : Fichier `ui/components/splash_screen.py` maintenu 100% inchangé jusqu'à décision explicite de migration.

---

## H. Questions d'Arbitrage pour l'Utilisateur

Merci de m'indiquer vos préférences pour la migration finale :

1. **Structure de Composition :** Préférez-vous l'**Hypothèse A (Vectoriel Ouvert)** ou l'**Hypothèse B (Carte Obsidian)** observées dans le laboratoire Flet Web ?
2. **Attribution de la lumière :** Le halo pulsant Ambre doît-il entourer l'ensemble du logo vectoriel ou spécifiquement la zone du signal audio ?
