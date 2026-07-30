# AIC — Audio Intelligence Companion

**AIC** est un assistant musical local fonctionnant entierement hors-ligne. Il analyse votre bibliotheque audio, extrait des caracteristiques acoustiques via le reseau de neurones **MusiCNN**, et genere des playlists personnalisees basees sur vos titres favoris.

---

## Telecharger

Les executables Windows, Linux et macOS sont disponibles sur la page Releases :

**[Telecharger la derniere version](https://github.com/Flex1-tech/Local_Recommendation_Engine/releases)**

---

## Prerequis

- **VLC Media Player** installe sur le systeme (pour l'ecoute des playlists generees)
- **Python 3.10+** (uniquement pour lancer depuis les sources)

---

## Lancer depuis les sources

```bash
git clone https://github.com/Flex1-tech/Local_Recommendation_Engine.git
cd Local_Recommendation_Engine

python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

---

## Technologies

| Composant | Technologie |
|---|---|
| Interface graphique | [Flet 0.86+](https://flet.dev/) |
| Inference IA (MusiCNN) | [ONNX Runtime](https://onnxruntime.ai/) |
| Base vectorielle locale | [LanceDB](https://lancedb.com/) |
| Algorithme de recommandation | MMR (scikit-learn) |
| Validation audio | FFprobe + Fleep |
| Lecteur audio | VLC Media Player |

---

## Releases

Les binaires sont construits et publies automatiquement par GitHub Actions a chaque nouveau tag.

Pour publier une nouvelle version :

```bash
git tag v1.0.0
git push --tags
```

GitHub Actions compile les versions Windows, Linux et macOS puis cree automatiquement la Release avec les archives attachees.
