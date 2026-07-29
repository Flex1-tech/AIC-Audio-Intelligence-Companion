from typing import List, Dict, Optional, Any
import lancedb

from extraction import initialize_database, get_file_hash, get_existing_embeddings


class TrackRepository:
    """
    Repository d'accès aux données vectorielles LanceDB pour AIC.
    Encapsule la table 'audio_embeddings' et les requêtes BLAKE3 hash.
    """

    def __init__(self, db_path: str = "./MusicRecommenderDB"):
        self.db_path = db_path
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

    def find_existing_hashes(
            self, hashes: List[str]) -> Dict[str, Dict[str, Any]]:
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
