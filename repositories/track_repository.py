from typing import List, Dict, Optional, Any
import lancedb

from extraction import initialize_database, get_file_hash, get_existing_embeddings
from utils.path_utils import get_user_data_dir


class TrackRepository:
    """
    Repository d'accès aux données vectorielles LanceDB pour AIC.
    Encapsule la table 'audio_embeddings' et les requêtes BLAKE3 hash.
    Utilise le répertoire de données utilisateur propre à l'OS (%APPDATA%/AIC/MusicRecommenderDB).
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(get_user_data_dir() / "MusicRecommenderDB")
        self._table: Optional[lancedb.table.Table] = None

    def get_table(self) -> lancedb.table.Table:
        if self._table is None:
            self._table = initialize_database(self.db_path)
        return self._table

    def count_rows(self) -> int:
        try:
            tbl = self.get_table()
            return tbl.count_rows()
        except Exception:
            return 0

    def find_existing_hashes(self, hashes: List[str]) -> Dict[str, Dict[str, Any]]:
        """Retourne les entrées DB sous forme {hash: row_dict}."""
        if not hashes:
            return {}
        try:
            tbl = self.get_table()
            return get_existing_embeddings(hashes, tbl)
        except Exception:
            return {}

    def compute_file_hash(self, file_path: str) -> str:
        return get_file_hash(file_path)
