# Audit d'Architecture & Intention Visuelle — AIC Splash Screen (Phase 0)

> **Statut du code** : AUCUNE modification de production appliquée (`ui/components/splash_screen.py` inchangé).  
> **Source de vérité visuelle** : Exécution Flet Web réelle (`tests/splash_preview/main.py`) — **Aucune image artificielle générée**.  
> **Spécifications projet** : Conformité avec `ui/design_system/THEMING.md` (Ambre `#FE8F40` = Audio/Signal, Cyan `#30C4EF` = IA/Structure).

---

## 1. Intention Originale & Identité de Marque

L'intention visuelle originale du Splash Screen AIC (Audio Intelligence Companion) est de procurer une sensation immédiate d'activation applicative :

$$\text{Sensation recherchée} = \textbf{"AIC est en train de s'allumer"}$$

- **Caractère** : Immersif, calme, technologique, premium, réactif.
- **Dualité de marque** :
  - **Ambre `#FE8F40` (Signal Audio / Énergie)** : La résonance sonore, l'onde audio vive qui s'éveille.
  - **Cyan `#30C4EF` (Intelligence IA / Structure)** : La structure de marque "AIC", la précision de l'IA.
- **Expérience** : Une composition centrée équilibrée qui s'allume avec élégance en **~2.3 secondes**, puis s'efface de manière fluide pour laisser place à `MainLayout`.

---

## 2. OLD v1 — Ce qui doit être conservé (Fondation Visuelle)

1. **La composition centrée et maîtrisée** : Équilibre visuel parfait entre le logo, l'onde audio et le bloc textuel.
2. **Le halo Ambre pulsant V1** : L'élément lumineux réactif principal (`ft.BoxShadow` ambre `#40FE8F40` qui créait l'impulsion de vie au centre).
3. **Le rythme rapide (~2.3 secondes)** : Séquence réactive qui ne fait jamais patienter l'utilisateur.
4. **La typographie système Bold** : Choix de la police système pour un rendu net et instantané (lisibilité > décoration).
5. **La robustesse & le fallback** : Capacité du composant à s'exécuter sans crash si une ressource est absente (`ft.Icons.GRAPHIC_EQ`).

---

## 3. NEW v2 — Ce qui doit rester rejeté

1. **La durée excessive (5.0s)** : Ressentie comme un écran publicitaire lent.
2. **Le logo géant (65% du viewport, 300–560px)** : Trop massif et encombrant.
3. **Le balayage scanner démonstratif** : Mouvement de faisceau trop complexe qui détournait l'attention du signal.
4. **La typographie sérif imposée (Cinzel Decorative)** : Moins lisible à grande vitesse dans une interface audio moderne.
5. **La surcharge multicolore** : Perte de la sobriété Obsidian.

---

## 4. V3 Actuelle — Ce qui est correct

- **Rapidité** : Conservée à 2.3s par défaut (`SPLASH_ANIMATION_DURATION_MS = 2300`).
- **Pulsation Ambre** : Présence du halo `BoxShadow` ambre et du signal audio Ambre `#FE8F40`.
- **Fond Obsidian** : Fond sombre `#0F1117` avec gradient ambiant.
- **Stabilité & Tests** : 100% des tests unitaires pytest (11/11) et linter pre-commit validés.

---

## 5. V3 Actuelle — Régressions Identifiées

1. **Onde audio officielle SVG contournée** :
   - Au lieu d'utiliser l'onde vectorielle officielle du logo (`assets/layer_wave.svg`, composée de 70 tracés SVG fins), la V3 actuelle dessine **5 rectangles génériques Flet `Container`** (`wave_bar1..5`).
   - *Conséquence* : Le logo officiel est partiellement remplacé par une construction Flet synthétique.
2. **Séparation des calques SVG ignorée** :
   - `assets/layer_letterform.svg` (Cyan) et `assets/layer_wave.svg` (Ambre) ont été créés spécifiquement pour séparer la lettre et l'onde. La V3 actuelle charge `icon.svg` d'un bloc.
3. **Rendu "Loading Card" trop petit** :
   - La formule de clamping `clamp(110, min*0.22, 165)` limite la carte à 165px max. Sur un écran desktop 1920×1080, la composition reste bloquée dans un petit carré au centre, perçu comme une "petite carte de chargement" au lieu de l'immersion "AIC s'allume".

---

## 6. Assets — Inventaire & Rôle de Chaque Fichier

| Asset | Taille | Intention & Rôle Officiel | Statut Recommandé |
|-------|--------|---------------------------|-------------------|
| `assets/layer_letterform.svg` | 2.9 KB | Calque vectoriel officiel de la lettre "AIC" en Cyan `#30C4EF` (3 paths). | **À UTILISER** (Calque structure) |
| `assets/layer_wave.svg` | 11.5 KB | Calque vectoriel officiel de l'onde sonore Ambre `#FE8F40` (70 paths). | **À UTILISER** (Calque signal audio) |
| `assets/icon.svg` | 14.9 KB | Logo officiel combiné (lettre + onde d'un bloc). | Fallback unique & Icône de fenêtre |
| `assets/icon.png` | 44.1 KB | Fallback raster PNG. | Fallback système OS |
| `assets/fonts/CinzelDecorative-*.ttf` | ~62 KB | Polices sérif optionnelles. | Réservez aux titres de l'app si besoin (non retenu pour Splash) |

---

## 7. Architecture Recommandée (Le Schéma Cible)

L'architecture visuelle cible réconcilie les **vrais calques SVG officiels** avec la **fondation lumineuse et rapide de OLD v1** :

```
                               AIC Logo
                                  │
                       ┌──────────┴──────────┐
                       │                     │
                  LETTERFORM              WAVE
                     SVG                   SVG
                 Cyan #30C4EF         Ambre #FE8F40
                    (A Core)          (70 Vector Paths)
                       │                     │
                       └──────────┬──────────┘
                                  │
                             COMPOSITION
                          Carte Obsidian / Halo
                                  │
                              HALO OLD
                       (BoxShadow Ambre Pulsant)
                                  │
                          OBSIDIAN BACKGROUND
                         (BG_DARK #0F1117 + Glow)
                                  │
                          RESPONSIVE SCALE
                      (Clamp Harmonieux 140-220px)
                                  │
                             ~2.3 secondes
                                  │
                                  ↓
                             MAIN LAYOUT
```

---

## 8. Stratégie Responsive Harmonieuse

Pour dépasser le piège du "petit widget 165px" sans créer un logo gigantesque :

### 1. Formule d'Échelle de la Composition
```python
# Clamping adaptatif harmonieux de la composition centrale
LOGO_MIN_SIZE = 140
LOGO_MAX_SIZE = 220
logo_size = clamp(LOGO_MIN_SIZE, min(viewport_w, viewport_h) * 0.26, LOGO_MAX_SIZE)
```

### 2. Proportions Relatives Intègres
- **Calques SVG (`letterform` + `wave`)** : Superposés dans un `ft.Stack(width=logo_size, height=logo_size)`.
- **Titre "AIC"** : `size = clamp(36, logo_size * 0.28, 52)` pt, Bold Système.
- **Sous-titre "Audio Intelligence Companion"** : `size = clamp(12, logo_size * 0.085, 16)` pt, Ambre `#FE8F40`.
- **Espacements & Marges** : Proportionnels à `logo_size` (`gap = logo_size * 0.12`).
- **Glow Ambiant** : `bg_glow_size = min(viewport_w, viewport_h) * 0.60`.

---

## 9. Stratégie d'Animation & Timing (~2.3s)

Constante unique de contrôle :
```python
SPLASH_ANIMATION_DURATION_MS = 2300
```

### Séquence des Phasages au Prorata

```
  t=0ms         t=350ms             t=800ms               t=1150ms      t=1425ms      t=1650ms            t=2300ms
  ├─── Apparition ──┼── Révélation ────┼─── Impulsion Halo ───┼── Titre ────┼── Sous-titre ┼── Fondu de sortie ──┤
  │    Structure    │    Onde Vector  │    Ambre BoxShadow   │   AIC Bold  │   Ambre      │   vers MainLayout   │
  │    (Cyan)       │    (Ambre)      │    (Peak Pulse)      │             │              │                     │
```

1. **t = 0 ms (0% - 15%)** : Apparition de la carte Obsidian & du calque `layer_letterform.svg` (Cyan `#30C4EF`).
2. **t = 350 ms (15% - 35%)** : Éveil et apparition fluide de `layer_wave.svg` (L'onde vectorielle Ambre `#FE8F40` s'allume).
3. **t = 800 ms (35% - 50%)** : Peak du Halo Ambre pulsant V1 (`BoxShadow` `spread=9, blur=36, color=#48FE8F40`).
4. **t = 1150 ms (50% - 62%)** : Révélation du titre "AIC" (Système Bold blanc).
5. **t = 1425 ms (62% - 72%)** : Atténuation du halo vers un niveau d'équilibre (`blur=20`) et apparition du sous-titre Ambre.
6. **t = 1650 ms → 2300 ms (72% - 100%)** : Maintien de contemplation puis fondu de sortie global vers `MainLayout`.

---

## 10. Stratégie des Couleurs (Conformité `THEMING.md`)

- **Letterform ("A")** : Cyan `#30C4EF` (déclaré nativement dans `layer_letterform.svg`).
- **Onde Audio Vectorielle** : Ambre `#FE8F40` (déclaré nativement dans `layer_wave.svg`).
- **Halo Pulsant** : Ambre `#FE8F40` (`#48FE8F40`).
- **Titre "AIC"** : Blanc `#F9FAFB` (`ObsidianColors.TEXT_PRIMARY`).
- **Sous-titre** : Ambre `#FE8F40` (`ObsidianColors.PRIMARY`).

---

## 11. Stratégie du Halo V1

- Le halo est généré par `ft.BoxShadow` ambre pulsant sur le conteneur du logo.
- L'animation fait passer l'opacité et le flou de `spread=0, blur=0` → `spread=9, blur=36, color=#48FE8F40` → `spread=3, blur=20, color=#20FE8F40`.
- Cela crée l'effet physique d'impulsion énergétique d'allumage sans utiliser de scanner artificiel.

---

## 12. Stratégie Fond Obsidian & Texture Noise

- **Fond** : `ObsidianColors.BG_DARK` (`#0F1117`).
- **Lumière ambiante** : `ft.RadialGradient` très doux centré derrière le logo (`rgba(254, 143, 64, 0.12)` Ambre + `rgba(48, 196, 239, 0.04)` Cyan).
- **Noise / Grain** : Aucun asset de texture bruit/grain n'existant dans le projet, nous n'inventerons aucune texture artificielle. Le fond Obsidian Horizon pur Material 3 est conservé.

---

## 13. Plan de Migration Zéro Régression

1. **Préparation du Laboratoire** : Mettre à jour `tests/splash_preview/splash_variants.py` avec la variante `SplashV3Vector` utilisant la superposition réactive `layer_letterform.svg` + `layer_wave.svg`.
2. **Observation Flet Web** : Lancer `uv run flet run tests/splash_preview/main.py --web` et valider le rendu dans le navigateur réel.
3. **Approbation & Migration Production** : Une fois la variante validée, mettre à jour `ui/components/splash_screen.py`.
4. **Validation des Tests Automatisés** : Exécuter `pytest` et `pre-commit`.
5. **Validation Runtime Réelle** : Exécuter `uv run flet run main.py` pour valider le boot complet et la transition vers `MainLayout`.

---

## 14. Risques de Régression & Mesures de Prévention

| Risque potentiel | Mesure de prévention |
|------------------|----------------------|
| SVG non trouvés dans un binaire pyinstaller | Utiliser `get_asset_path()` avec fallback automatique sur `icon.svg` d'un bloc puis `ft.Icons.GRAPHIC_EQ`. |
| Décalage entre la lettre et l'onde | `layer_letterform.svg` et `layer_wave.svg` partagent exactement la même viewBox `1024x1024`. Superposés à `width=S, height=S` dans un `ft.Stack`, leur alignement est mathématiquement parfait. |
| Ralentissement de l'animation | Conserver la mise à jour sélective `_safe_update(control)` par composant au lieu de `page.update()` global. |

---

## 15. Tests Nécessaires

1. `test_responsive_dimensions_small_viewport` : Vérifier `LOGO_MIN_SIZE = 140`.
2. `test_responsive_dimensions_large_viewport` : Vérifier `LOGO_MAX_SIZE = 220`.
3. `test_svg_layers_resolution` : Vérifier que `layer_letterform.svg` et `layer_wave.svg` sont résolus correctement.
4. `test_splash_animation_custom_duration` : Vérifier le recalcul au prorata de `SPLASH_ANIMATION_DURATION_MS`.
5. `uv run pytest` : 100% PASS.
6. `uv run pre-commit run --all-files` : 100% PASS.
7. `uv run flet run main.py` : Boot réel validé.
