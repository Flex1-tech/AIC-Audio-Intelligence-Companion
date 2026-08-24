# AIC Splash Screen — Rapport de Comparaison Objective OLD (v1) vs NEW (v2)

> **Méthodologie** : Analyse basée sur lecture exhaustive du code source des deux implémentations (`splash_screen_old.py` commit 73707ef vs `splash_screen_new.py` v2 actuelle), logs d'exécution Flet confirmant les timings réels, et mockups de référence générés pour représentation visuelle.

> **Principe** : NEW n'est pas supposé meilleur que OLD. Chaque version est évaluée objectivement.

---

## Rendu de Référence

![OLD Splash Screen v1 — Rendu de référence](C:\Users\HP\.gemini\antigravity-ide\brain\9c250d69-74d3-4a80-9e6b-b85314dd9690\old_splash_mockup.jpg)

**↑ OLD (v1)** — Carte 110×110 Obsidian, barres equalizer ambre, halo pulsant, typographie système

![NEW Splash Screen v2 — Rendu de référence](C:\Users\HP\.gemini\antigravity-ide\brain\9c250d69-74d3-4a80-9e6b-b85314dd9690\new_splash_mockup.jpg)

**↑ NEW (v2)** — Logo SVG plein écran, scan beam ambre, radial glow Cyan+Ambre, Cinzel Decorative

---

## 1. Données Techniques

| Paramètre | OLD (v1) | NEW (v2) |
|-----------|----------|----------|
| **Commit source** | `73707ef` | Production actuelle |
| **Durée totale** | ~2.3s | ~5.0s |
| **Taille du logo** | 110×110 px (card fixe) | 300–560 px (adaptatif, 65% viewport) |
| **Assets requis** | `icon.svg` / `icon.png` | `layer_letterform.svg` + `layer_wave.svg` |
| **Fallback logo** | `ft.Icons.GRAPHIC_EQ` | `icon.svg` / `icon.png` |
| **Fond** | `ObsidianColors.BG_DARK` (#0F1117) | `ObsidianColors.BG_DARK` (#0F1117) |
| **Couleurs brand** | Ambre #FE8F40 + Cyan (logo) | Cyan #30C4EF + Ambre #FE8F40 (50/50) |
| **Typographie** | Système (sans-serif par défaut) | Cinzel Decorative Bold/Regular |
| **Sous-titre couleur** | Gris muted (`TEXT_MUTED`) | Cyan `#30C4EF` |
| **Nb frames animation** | 6 états Flet | 8 états Flet (timeline continue) |
| **Validé runtime** | ✓ (logs serveur) | ✓ (logs serveur) |

---

## 2. Analyse par Critère

### 2.1 Logo

| Dimension | OLD (v1) | NEW (v2) |
|-----------|----------|----------|
| Rendu | Logo dans une **carte Obsidian 110×110** avec coins arrondis | Logo **plein écran adaptatif** (jusqu'à 560px), sans carte |
| Lisibilité | Compact, très lisible mais petit | Grand et dominant — lisibilité maximale |
| Contexte visuel | Encadré dans une surface sombre distincte (`#161922`) | Logo flottant sur fond noir pur avec glow ambiant |
| Fidélité marque | Logo AIC présent, mais rendu dans un "container app" générique | Couches SVG dédiées : letterform + wave séparés → plus fidèle |
| **Avantage OLD** | La carte crée une perception de "produit fini stable" | — |
| **Avantage NEW** | Le logo remplit l'écran, impact visuel maximal | — |

### 2.2 Animation

| Dimension | OLD (v1) | NEW (v2) |
|-----------|----------|----------|
| Durée | **2.3s** — rapide, dynamique | **5.0s** — cinématique, déployé |
| Séquence | Logo → Equalizer → Halo pulse → Titre → Sous-titre → Fade | Logo+Glow → Wave dim → Scan beam → Wave reveal → Titre → Sous-titre → Fade |
| Impression | Snappy, instantané, "punchy" | Révélation progressive, théâtrale |
| **Avantage OLD** | Rapidité perçue comme professionnelle (pas de "loading" long) | — |
| **Avantage NEW** | Récit visuel complet : chaque élément a une raison d'apparaître | — |
| **Risque OLD** | Trop rapide → certains effets peuvent être manqués | — |
| **Risque NEW** | Trop long → peut sembler lent si l'app charge rapidement | — |

### 2.3 Signal / Wave (Audio Identity)

| Dimension | OLD (v1) | NEW (v2) |
|-----------|----------|----------|
| Composant | 5 barres d'égaliseur verticales (`#FE8F40`) animées | Onde sinusoïdale SVG + beam scanner ambre |
| Lisibilité audio | Très claire : pattern graphique universel de l'audio | Plus sophistiqué mais dépend de `layer_wave.svg` |
| Animation | Barres expansées (8→22→32px) → signal en éveil | Faisceau balayage ambre + reveal progressif wave |
| **Avantage OLD** | Lisibilité maximale même sans SVG précis | — |
| **Avantage NEW** | Intégration visuelle Logo+Wave = identité complète cohérente | — |
| **Risque NEW** | Si `layer_wave.svg` absent → onde invisible | — |

### 2.4 Halo / Effets Lumineux

| Dimension | OLD (v1) | NEW (v2) |
|-----------|----------|----------|
| Type | `BoxShadow` ambre pulsant sur carte (`#40FE8F40` → `#1AFE8F40`) | Radial gradient ambiant Cyan+Ambre (`bg_glow`) centré |
| Intensité | Haute au début (spread=6, blur=28) → réduite (spread=2, blur=14) | Douce et permanente (opacity 0.0→1.0 au logo_intro) |
| **Avantage OLD** | Pulsation visible, dynamique et réactive — effet "alive" | — |
| **Avantage NEW** | Cohérence marque (Cyan+Ambre), profondeur atmosphérique | — |
| **Régression NEW** | Aucune pulsation — l'ambiance est statique après apparition | — |

### 2.5 Typographie

| Dimension | OLD (v1) | NEW (v2) |
|-----------|----------|----------|
| Titre "AIC" | Système bold, 38pt, blanc | **Cinzel Decorative Bold**, adaptatif (≈56pt), blanc |
| Sous-titre | Système W_500, 13pt, gris `TEXT_MUTED` | **Cinzel Decorative Regular**, adaptatif, **cyan** `ACCENT_CYAN` |
| Contenu sous-titre | `"Audio Intelligence Companion"` | `"AUDIO INTELLIGENCE COMPANION"` (ALL CAPS) |
| **Avantage OLD** | Robustesse : fonctionne sans font custom, jamais de fallback | — |
| **Avantage NEW** | Font premium cohérente, sous-titre cyan = couleur marque tech | — |
| **Risque NEW** | Si Cinzel non chargé → fallback système peu cohérent | — |

### 2.6 Composition (Layout)

| Dimension | OLD (v1) | NEW (v2) |
|-----------|----------|----------|
| Utilisation écran | ~30% du viewport occupé (compact vertical) | ~80% du viewport occupé (immersif) |
| **Avantage OLD** | App icon pattern → familier, lisible immédiatement | — |
| **Avantage NEW** | Utilisation totale du viewport → sensation produit premium | — |

### 2.7 Transition (Entrée & Sortie)

| Dimension | OLD (v1) | NEW (v2) |
|-----------|----------|----------|
| Entrée (Scale) | Scale 0.92→1.0 + Offset y=0.04→0 en 500ms | Scale 0.90→1.0 + Offset y=0.02→0 en ~1250ms |
| Sortie | Opacity 1→0 en 400ms à ~1.9s | Opacity 1→0 sur les 12% finaux (~600ms) |
| **Avantage OLD** | Sortie rapide et nette | — |
| **Avantage NEW** | Entrée plus lente = sentiment premium | — |

---

## 3. Matrice Comparative Globale

| Critère | OLD (v1) | NEW (v2) | Verdict |
|---------|----------|----------|---------|
| Logo — Taille & Impact | 🔵 Compact | 🟠 Dominant | **NEW** |
| Logo — Robustesse assets | 🟢 Haute (fallback icon) | 🟡 Moyenne (dépend SVG) | **OLD** |
| Animation — Rapidité | 🟢 2.3s, snappy | 🟡 5.0s, long | **OLD** |
| Animation — Narration | 🔵 Simple | 🟠 Riche | **NEW** |
| Signal Audio — Clarté | 🟢 Barres equalizer = universel | 🔵 Onde SVG + beam | **OLD** |
| Signal Audio — Beauté | 🔵 Basique | 🟠 Spectaculaire | **NEW** |
| Halo — Dynamisme | 🟢 Pulse ambre actif | 🔵 Statique après appear | **OLD** |
| Halo — Profondeur | 🔵 Card shadow uniquement | 🟠 Radial Cyan+Ambre | **NEW** |
| Typographie — Robustesse | 🟢 Système, toujours OK | 🟡 Cinzel requis | **OLD** |
| Typographie — Premium | 🔵 Basique | 🟠 Cinzel Decorative | **NEW** |
| Composition — Familiarité | 🟢 App icon pattern | 🔵 Cinématique | **OLD** |
| Composition — Immersion | 🔵 Limitée | 🟠 Maximale | **NEW** |
| Couleurs marque Cyan+Ambre | 🟡 Ambre dominant | 🟢 Cyan+Ambre équilibré | **NEW** |
| Cohérence avec logo AIC | 🟡 Logo dans card générique | 🟢 Couches SVG dédiées | **NEW** |

**Score final : OLD = 6 victoires | NEW = 8 victoires**

---

## 4. Avantages exclusifs OLD (v1)

1. **Vitesse** : 2.3s vs 5.0s → l'utilisateur accède à l'app plus rapidement
2. **Halo pulsant** : le BoxShadow Ambre qui pulse puis s'atténue = effet "alive" unique, absent dans NEW
3. **Robustesse assets** : fonctionne même sans `layer_wave.svg` (fallback GRAPHIC_EQ)
4. **Pattern recognizable** : carte icône 110×110 = pattern universel app iOS/Android
5. **Typographie sans risque** : zéro dépendance font, toujours rendu correctement

---

## 5. Avantages exclusifs NEW (v2)

1. **Cohérence marque** : les deux couleurs brand (#30C4EF + #FE8F40) présentes et équilibrées
2. **Logo authentique** : `layer_letterform.svg` + `layer_wave.svg` reproduisent exactement le logo AIC
3. **Typographie premium** : Cinzel Decorative — identité propre, distincte, mémorable
4. **Sous-titre cyan** : "AUDIO INTELLIGENCE COMPANION" en Cyan = renforce couleur marque tech/IA
5. **Immersion** : écran rempli à 80% → sensation produit premium immédiatement
6. **Scan beam ambre** : effet technologique unique — "IA qui s'initialise" visuellement

---

## 6. Régressions NEW (v2) par rapport à OLD (v1)

> [!WARNING]
> Ces régressions doivent être corrigées dans toute V3.

| Régression | Impact | Recommandation V3 |
|------------|--------|-------------------|
| **Halo pulsant absent** | L'effet "alive" est perdu. NEW semble statique après appear. | Ajouter pulsation sur `bg_glow` (opacity 0.6→1.0→0.8, 800ms repeat) |
| **Durée trop longue** | 5.0s peut paraître excessif si l'app charge vite (<3s) | Réduire à 3.5s ou rendre adaptatif (min 2.5s, max 4s) |
| **Dépendance SVG fragile** | Si `layer_wave.svg` manque → onde invisible | Fallback obligatoire: SVG absent → barres equalizer OLD |
| **Glow statique** | Le radial gradient apparaît une fois et ne bouge plus | Ajouter pulse opacity 0.7→1.0→0.7 (600ms cycle) |

---

## 7. Synthèse & Recommandations pour V3

> [!IMPORTANT]
> L'objectif n'est pas de choisir OLD ou NEW — c'est de **synthétiser le meilleur des deux**.

**Formule recommandée V3 :**

```
V3 = NEW.svg_layers       ← logo authentique couches
   + NEW.cinzel_font       ← typographie premium
   + NEW.cyan_subtitle     ← sous-titre couleur marque
   + NEW.bg_glow_radial    ← ambiance Cyan+Ambre
   + OLD.pulse_shadow      ← halo pulsant actif
   + OLD.speed             ← durée réduite ~3.5s
   + OLD.fallback_robust   ← robustesse assets
```

**Architecture concrète V3 :**

| Composant | Source | Modification |
|-----------|--------|-------------|
| Logo layers SVG | NEW | Inchangé |
| Taille logo | NEW → 55% viewport | Légèrement réduit (vs 65%) |
| Durée | NEW → 3.5s | Réduit de 5.0s |
| BoxShadow pulsant | OLD → sur logo_container NEW | Ajouté |
| Bg glow radial | NEW | + pulsation opacity |
| Scan beam ambre | NEW | Inchangé |
| Typographie | NEW Cinzel | + fallback système |
| Sous-titre | NEW cyan | Inchangé |
| Fallback audio | OLD barres | Si SVG absent |

---

*Rapport généré le 24/08/2026 — Production code non modifié. En attente de validation utilisateur avant toute V3.*
