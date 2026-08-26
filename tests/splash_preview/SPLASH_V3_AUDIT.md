# Audit Critique Complémentaire — AIC Splash Screen V3 & Intention Originale

> **Statut du code** : AUCUNE modification appliquée au code de production (`ui/components/splash_screen.py`).  
> **Méthodologie d'audit** : Inspection de l'historique Git (`git log`, `git diff`), analyse des assets dans `assets/`, audit du système de design `ui/design_system/THEMING.md` et revue d'architecture.

---

## 1. Historique Chronologique Réel (Git Audit)

L'inspection de l'historique Git du projet révèle l'évolution exacte du composant :

```
73707ef  feat(ui): add premium splash screen animation (Obsidian Horizon v1)
  └─ OLD v1 : Carte 100x100 Obsidian, icon.svg, 5 barres Flet Container ambre (#FE8F40), halo BoxShadow ambre pulsant, 2.3s.

855e481  feat(ui): splash screen v2 - SVG layers, responsive logo, wave glow scanner, Space Grotesk font
  └─ NEW v2 : Séparation de icon.svg en 2 calques SVG (layer_letterform.svg + layer_wave.svg), faisceau balayage ambre (wave_glow), 65% viewport logo (300-560px), 5.0s duration.

5d2fb8a  feat(ui): use Cinzel Decorative font for splash screen and app title
  └─ Intégration de la police Cinzel Decorative sur "AIC".

3ce222a  feat(splash): stabilize V3 splash screen
  └─ V3 Base : Décision de revenir à la structure OLD v1 comme fondation (carte 110x110, 2.3s, barres Flet, halo BoxShadow).

cd377f8  feat(splash): enlarge audio animation and restore pure ambre audio identity
  └─ V3.1 : Retour strict à l'Ambre #FE8F40 pour les barres Flet et le halo, amplitude des barres portée à 40px.

868efc6  feat(splash): implement V3.2 Immersive splash screen with responsive card
  └─ V3.2 : Carte adaptative clamp(130, min*0.22, 160)px, barres Flet max 45px, durée 2.5s.

24d5af3  refactor(splash): clean up, parameterize global duration, and improve responsive composition
  └─ Refactor V3 : Centralisation de SPLASH_ANIMATION_DURATION_MS = 2300 et calculs réactifs clamp(110, min*0.22, 165)px.
```

---

## 2. Architecture OLD v1 (`73707ef`)

- **Structure** : Carte Obsidian `#161922` de 100×100 px centrée.
- **Logo** : Icône statique unique `icon.svg` (64×64 px) placée au centre de la carte.
- **Signal Audio** : 5 barres verticales Flet `Container` (`wave_bar1..5`) de 3px de large placées en bas de la carte et animées en hauteur (`8/14/22/14/8` → `14/24/32/24/14`).
- **Lumière** : Shadow `ft.BoxShadow` ambre `#40FE8F40` pulsant directement sur le contour de la carte 100×100.
- **Typographie** : "AIC" 38pt bold système + "Audio Intelligence Companion" 13pt muted system.
- **Durée** : 2.3s.

---

## 3. Architecture NEW v2 (`855e481`)

- **Structure** : Grand conteneur centré ouvert (65% du viewport, `300-560px`), sans carte fermée.
- **Logo SVG Multi-couches** : `icon.svg` a été scindé en deux calques SVG distincts :
  1. `layer_letterform.svg` (forme de lettre "A" en cyan `#30C4EF`, 3 tracé SVG).
  2. `layer_wave.svg` (l'onde sonore vectorielle continue en ambre `#FE8F40`, 70 tracés SVG).
- **Scanner & Onde** : Un faisceau dégradé ambre (`wave_glow`) balayait horizontalement de gauche à droite sur `layer_wave.svg` pour "allumer" l'onde sonore vectorielle SVG.
- **Typographie** : Cinzel Decorative Bold/Regular (chargée via assets TTF).
- **Durée** : 5.0s.

---

## 4. Architecture V3 Actuelle

- **Structure** : Carte Obsidian `#161922` avec clamping responsive `clamp(110, min*0.22, 165)` px.
- **Logo** : Static image unique `icon.svg` (ou `icon.png`) chargée d'un bloc.
- **Signal Audio** : Reconstitution par 5 barres verticales Flet `Container` (4px de large, hauteur max 46px) dessinées sous l'icône dans la carte.
- **Lumière** : Halo BoxShadow ambre pulsant sur la carte + gradient radial ambiant très doux en fond.
- **Typographie** : Système Bold 38pt blanc + sous-titre Ambre `#FE8F40`.
- **Durée** : 2.3s (`SPLASH_ANIMATION_DURATION_MS = 2300`).

---

## 5. Audit Approfondi des Assets

Voici l'inventaire exact du dossier `assets/` et l'analyse de leur utilisation :

| Asset | Taille | Rôle & Origine | Statut Actuel | Statut Historique | Analyse Audit |
|-------|--------|----------------|---------------|-------------------|---------------|
| `assets/icon.svg` | 14.9 KB | Icône officielle complète AIC (lettre + onde combinées). | **Utilisé** dans production actuelle | Utilisé dans OLD v1 | SVG complet de la marque. Fonctionne bien d'un bloc mais ne permet pas d'animer l'onde séparément de la lettre. |
| `assets/icon.png` | 44.1 KB | Fallback raster de l'icône AIC. | **Utilisé** (comme fallback si SVG absent) | Ajouté commit `b045ce6` | Inchangé, rôle de fallback. |
| `assets/layer_letterform.svg` | 2.9 KB | Calque vectoriel de la lettre Cyan `#30C4EF` (3 paths). | **NON UTILISÉ** | Créé dans NEW v2 (`855e481`) | **Ignoré dans la V3 actuelle.** |
| `assets/layer_wave.svg` | 11.5 KB | Calque vectoriel de l'onde ambre `#FE8F40` (70 paths). | **NON UTILISÉ** | Créé dans NEW v2 (`855e481`) | **Ignoré dans la V3 actuelle.** |
| `assets/fonts/CinzelDecorative-Bold.ttf` | 62.3 KB | Police sérif décorative. | **NON UTILISÉ** | Ajouté commit `8ec7f64` | Délibérément écarté pour privilégier la lisibilité système. |
| `assets/fonts/CinzelDecorative-Regular.ttf` | 60.4 KB | Police sérif régulière. | **NON UTILISÉ** | Ajouté commit `8ec7f64` | Délibérément écarté. |
| `assets/msd-musicnn-1.onnx` | 3.16 MB | Modèle d'extraction de features audio ML. | N/A (Modèle ML backend) | Commit `b045ce6` | Sans rapport avec le Splash. |

> [!IMPORTANT]
> **Noise / Grain** : Aucun fichier de texture bruit/grain (`noise.png`, `grain.png`, etc.) n'existe dans `assets/` ni dans l'historique Git du dépôt. Le fond a toujours été le fond sombre Obsidian `#0F1117` avec un halo ou dégradé radial Flet.

---

## 6. Point Critique — Onde Audio (SVG vs Flet)

### Constat de l'Audit
Dans la V3 actuelle, **l'onde audio animée N'EST PAS l'asset SVG vectoriel du logo (`layer_wave.svg`)**.
Il s'agit d'une **génération Flet synthétique** composée de 5 contrôles `ft.Container` rectangulaires verticaux (`wave_bar1..5`), placés dans un `ft.Row`.

### Origine de cette situation
1. **Commit `855e481` (NEW v2)** avait découpé `icon.svg` en deux fichiers : `layer_letterform.svg` (lettre) et `layer_wave.svg` (l'onde vectorielle à 70 tracés). NEW v2 superposait les deux dans un `ft.Stack` et faisait passer un faisceau dégradé ambre sur `layer_wave.svg`.
2. **Commit `3ce222a` (V3)** est revenu à l'architecture de OLD v1 pour des raisons de compacité (carte 110x110). Dans OLD v1, les barres d'égaliseur étaient 5 conteneurs Flet rectangulaires et l'icône au-dessus était `icon.svg`.
3. **Conséquence** : `layer_wave.svg` (la vraie onde vectorielle officielle composée de 70 tracés SVG) a été totalement mise de côté lors du retour à OLD v1.

### Comparaison Visuelle des deux approches

```
          [ Approche Actuelle (Barres Flet) ]                   [ Approche Vectorielle (layer_wave.svg) ]
                |   |   |   |   |                                ~~~/\/\/\---/\/\/\~~~
                |   |   |   |   |                                70 tracés vectoriels fins
          5 réctangles Flet verticaux                             Vraie onde du logo officiel AIC
```

---

## 7. Audit du Responsive & de l'Immersion

### Analyse de la formule actuelle
La V3 actuelle utilise : `card_size = clamp(110, min(vw, vh) * 0.22, 165)`.

- **Problème** : Sur un écran 1920×1080 (standard desktop), `1080 * 0.22 = 237px`, qui est plafonné à **165px**.
- **Résultat visuel** : La composition reste bloquée dans un petit widget/carte au centre d'un grand écran sombre. Cela donne une impression de "carte de chargement" (Loading Widget) plutôt que l'expérience "AIC est en train de s'allumer" (App Activation).

### Vision de l'Immersion sans perdre OLD
- Conserver la **composition centrée maîtrisée, le halo ambre et le rythme rapide (~2.3-2.5s)**.
- Mais permettre à la composition de **respirer dans le viewport** avec une échelle adapative réelle, ou en faisant interagir la lueur ambiante ambre et les calques vectoriels du logo (`layer_letterform.svg` + `layer_wave.svg`) directement sur l'écran.

---

## 8. Audit des Couleurs (`THEMING.md`)

Le document de spécification de la charte graphique (`ui/design_system/THEMING.md`) confirme :
- **Ambre (`#FE8F40`)** = Audio, Signal, Onde Sonore, Action Principale, Énergie.
- **Cyan (`#30C4EF`)** = Intelligence IA, Structure, Télémétrie, Systèmes.

Dans le Splash Screen :
- L'animation du signal sonore et de l'activation **DOIT être Ambre `#FE8F40`** (Ambre Audio).
- La structure de la lettre ("AIC") peut intégrer la touche Cyan `#30C4EF` officielle de la marque (du fait que `layer_letterform.svg` utilise la couleur `#30C4EF`).

---

## 9. Régressions Identifiées par rapport à l'Intention Originale

1. **Séparation des calques SVG abandonnée** : `layer_letterform.svg` (Cyan) et `layer_wave.svg` (Ambre) ne sont pas utilisés. `icon.svg` est chargé d'un bloc statique.
2. **Vraie onde vectorielle remplacée par des barres Flet** : L'onde officielle du logo (70 tracés vectoriels) est remplacée par 5 bâtonnets Flet génériques.
3. **Sensation de carte de chargement réduite** : Le clamping max à 165px empêche la lueur et la présence du logo de donner une sensation d'allumage immersif de l'application.

---

## 10. Questions Bloquantes & Décisions Soumises à l'Utilisateur

Avant toute écriture de code, merci de trancher les points suivants :

> [!IMPORTANT]
> **Question 1 — Onde Audio : Souhaitez-vous réintégrer la vraie onde vectorielle SVG (`layer_wave.svg`) ?**  
> *Option A (Recommandée)* : Superposer `layer_letterform.svg` (Cyan) et `layer_wave.svg` (Ambre) dans une composition centrée. L'onde vectorielle officielle à 70 tracés s'anime en opacité/lumière pendant le démarrage.  
> *Option B* : Conserver les 5 barres d'égaliseur rectangulaires Flet actuelles.

> [!IMPORTANT]
> **Question 2 — Immersion & Scaling : Préférez-vous une composition ouverte respirante (sans boîte 110-165px) ou conservez-vous la carte Obsidian ?**  
> *Option A (Recommandée - Immersion)* : Supprimer les contours rigides de la carte 110x110px. Laisser le logo SVG (`letterform` + `wave`) flotter dans l'espace avec son halo pulsant Ambre réactif et son fond lumineux ambiant. Cela donne l'impression exacte de "AIC s'allume".  
> *Option B* : Conserver la carte Obsidian rectangulaire de la V1 mais en augmentant ses plafonds responsive.

> [!IMPORTANT]
> **Question 3 — Timing : Confirmez-vous le maintien de la durée cible à ~2.3s – 2.5s ?**

---

### Attente de validation
Aucune ligne de code de production n'a été modifiée. J'attends vos réponses sur ces 3 décisions d'architecture visuelle avant de proposer le plan d'implémentation.
