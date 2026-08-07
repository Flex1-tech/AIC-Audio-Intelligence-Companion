from pydantic import Field
from lancedb.pydantic import LanceModel, Vector


class TrackEmbeddingModel(LanceModel):
    """
    Modèle de données pour stocker les embeddings des pistes audio dans LanceDB.
    Chaque instance représente une piste audio avec son embedding et ses métadonnées associées.

    Sorties MusiCNN stockées :
        - taggram : sortie index 0 du modèle, vecteur de 50 probabilités de tags MSD.
        - vector  : sortie index 1 du modèle, embedding latent de dimension 200.
    """

    # Identifiant unique de la piste
    file_hash: str = Field(
        json_schema_extra={"primary_key": True},
        description="Blake3 hash du fichier audio, utilisé comme identifiant unique",
    )

    # Métadonnées générales
    file_name: str
    file_path: str
    file_size_bytes: int

    # Sortie 0 du modèle : taggram (50 tags du Million Song Dataset)
    taggram: Vector(50) = Field(  # type: ignore
        description="Vecteur de 50 probabilités de tags musicaux MSD (sortie index 0 de MusiCNN)"
    )

    # Sortie 1 du modèle : embedding latent de dimension 200
    vector: Vector(200) = Field(  # type: ignore
        description="Embedding audio de dimension 200 (sortie index 1 de MusiCNN)"
    )
