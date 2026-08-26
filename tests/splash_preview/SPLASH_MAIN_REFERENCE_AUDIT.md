# Audit de Référence Distante `origin/main` — AIC Splash Screen

> **Fichier de production local (`ui/components/splash_screen.py`)** : STRICTEMENT INTACT — AUCUNE MODIFICATION DE PRODUCTION.  
> **Branche distante auditée** : `origin/main` (SHA: `af092ec63b397a3edf43165e49627c4d6b282fa9`).  
> **Méthodologie** : Inspection directe via `git show origin/main:ui/components/splash_screen.py`.

---

## 1. SHA Exact & Statut des Références Git

- **SHA de `origin/main`** : `af092ec63b397a3edf43165e49627c4d6b282fa9`
- **SHA de `origin/dev`** : `ae27d9581218d86bd4df22ff09d357459b6efd6f`
- **SHA de `HEAD` (local)** : `38b310f870b6b000c2d08a471e10a28ce639588b`

---

## 2. Version de Splash Réellement Présente sur `origin/main`

L'inspection de `origin/main:ui/components/splash_screen.py` révèle une **découverte capitale** :

$$\textbf{La version validée sur } \text{origin/main} \textbf{ est la version SVG Multi-Couches (v2) !}$$

`origin/main` contient déjà l'architecture vectorielle complète :
- **Calques SVG séparés** :
  - `layer_letterform.svg` (Structure de la lettre "A" / "AIC" en Cyan `#30C4EF`).
  - `layer_wave.svg` (Signal sonore vectoriel officiel à 70 tracés en Ambre `#FE8F40`).
  - Superposition dans un `ft.Stack([self.letterform_img, self.wave_img, self.wave_glow])`.
- **Typographie officielle** :
  - Titre `"AIC"` $\rightarrow$ `font_family="Cinzel Decorative Bold"`.
  - Sous-titre `"Audio Intelligence Companion"` $\rightarrow$ `font_family="Cinzel Decorative Regular"`.
- **Structure** : **Composition ouverte centrée** (Aucune carte rectangulaire fermée !).
- **Fond** : `ObsidianColors.BG_DARK` (`#0F1117`) avec gradient ambiant radial.
- **Durée** : Configurée à 5000 ms (`SPLASH_ANIMATION_CONFIG["total_ms"]`).

---

## 3. Matrice Comparative des Versions Historiques & Cible

| Feature / Paramètre | `origin/main` (`af092ec`) | OLD / V1 (`73707ef`) | Fichier Local (`24d5af3`) | `SplashV3Target` (Laboratoire) |
|---------------------|---------------------------|----------------------|---------------------------|--------------------------------|
| **Source Logo** | **`layer_letterform` + `layer_wave`** | `icon.svg` (bloc unique) | `icon.svg` d'un bloc | **`layer_letterform` + `layer_wave`** |
| **Onde Audio** | **Vraie onde SVG (70 paths)** | 5 barres Flet rectangulaires | 5 barres Flet rectangulaires | **Vraie onde SVG (70 paths)** |
| **Structure** | **Composition Ouverte** | Carte 100×100px | Carte clamp(110-165px) | **Composition Ouverte Immersive** |
| **Typographie** | **Cinzel Decorative Bold/Regular** | Système Bold | Système Bold | **Cinzel Decorative Bold/Regular** |
| **Couleur Lettre** | Cyan `#30C4EF` | Blanc `#F9FAFB` | Blanc `#F9FAFB` | **Cyan `#30C4EF`** |
| **Couleur Onde** | Ambre `#FE8F40` | Ambre `#FE8F40` | Ambre `#FE8F40` | **Ambre `#FE8F40`** |
| **Lumière / Halo** | BoxShadow `#38F59E0B` + Scanner | BoxShadow Ambre `#40FE8F40` | BoxShadow Ambre sur Carte | **BoxShadow Ambre V1 pulsant (`#48FE8F40`)** |
| **Fond** | `ObsidianColors.BG_DARK` (`#0F1117`) | `ObsidianColors.BG_DARK` (`#0F1117`) | `ObsidianColors.BG_DARK` (`#0F1117`) | **`ObsidianColors.BG_DARK` (`#0F1117`)** |
| **Sizing Logo** | `min(vw,vh) * 0.65` (`300-560px`) | 64 px | `clamp(110-165px)` | **`clamp(140-220px)`** |
| **Durée** | `5000 ms` | `2300 ms` | `2300 ms` | **`2300 ms` (Paramétrable)** |
| **Rendu Web** | Absolu `str(path)` | Absolu `str(path)` | Absolu `str(path)` | **Relatif (`"layer_letterform.svg"`)** |

---

## 4. Écart entre `origin/main` et le Fichier Local (`24d5af3`)

- **Ce qui s'était passé localement** : Lors des récents refactors locaux, le fichier `ui/components/splash_screen.py` avait été réécrit en s'inspirant d'un commit V1 très ancien (`73707ef`), réintroduisant 5 barres Flet rectangulaires et une carte rectangulaire fermée de 110-165px, tout en ignorant les calques SVG vectoriels et la police Cinzel Decorative.
- **Ce qui existe réellement sur `origin/main`** : `origin/main` possède déjà les calques vectoriels `layer_letterform.svg` + `layer_wave.svg`, la composition ouverte et la typographie Cinzel Decorative !

---

## 5. Diagnostic de la Référence Historique & Source de Vérité

> [!IMPORTANT]
> **Conclusion de l'audit** : L'audit précédent avait effectivement utilisé une mauvaise référence locale temporaire (la V1 basique avec 5 barres Flet) au lieu de la véritable référence distante validée sur `origin/main` (`af092ec`).
> 
> **Source de vérité d'architecture** : La source de vérité officielle du projet est **l'architecture distante de `origin/main` (`af092ec`)**, perfectionnée dans le laboratoire par **`SplashV3Target`** :
> 1. Conservation des calques SVG officiels `layer_letterform.svg` (Cyan) + `layer_wave.svg` (Ambre 70 paths).
> 2. Conservation de la composition ouverte sombre Obsidian `#0F1117` et de la typographie Cinzel Decorative.
> 3. Ajustement du timing à **~2.3s** (au lieu de 5.0s).
> 4. Remplacement du scanner lourd par l'impulsion **Halo BoxShadow Ambre V1**.
> 5. Scaling réactif harmonieux **`clamp(140, min*0.26, 220)`** px.
> 6. Déclaration relative des assets pour le rendu fluide Flet Web HTTP.

---

## 6. Confirmation d'Intégrité de la Production

> [!CAUTION]
> **Le fichier local de production [`ui/components/splash_screen.py`](file:///c:/Users/HP/Documents/Projets%20IA/Local_Recommendation_Engine/ui/components/splash_screen.py) n'a subi AUCUNE modification pendant cet audit.**
> 
> Aucun `git reset`, `git rebase`, `git checkout` ni `git commit` n'a été exécuté.
