from __future__ import annotations

import threading
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from utils.path_utils import get_user_data_dir

if TYPE_CHECKING:
    import lancedb


class TrackRepository:
    """
    Repository d'accès aux données vectorielles LanceDB pour AIC.
    Encapsule la table 'audio_embeddings' et les requêtes BLAKE3 hash.
    Utilise le répertoire de données utilisateur propre à l'OS (%APPDATA%/AIC/lancedb).
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            user_dir = get_user_data_dir()
            new_path = user_dir / "lancedb"
            old_path = user_dir / "MusicRecommenderDB"
            # Auto-migration de l'ancien dossier vers le nouveau nom
            if old_path.exists() and not new_path.exists():
                try:
                    old_path.rename(new_path)
                except Exception:
                    pass
            self.db_path = str(new_path)
        else:
            self.db_path = db_path
        self._table: Optional[lancedb.table.Table] = None
        self._lock = threading.Lock()

    def get_table(self) -> lancedb.table.Table:
        if self._table is None:
            with self._lock:
                if self._table is None:
                    from extraction import initialize_database

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
            from extraction import get_existing_embeddings

            tbl = self.get_table()
            return get_existing_embeddings(hashes, tbl)
        except Exception:
            return {}

    def compute_file_hash(self, file_path: str) -> str:
        from extraction import get_file_hash

        return get_file_hash(file_path)
