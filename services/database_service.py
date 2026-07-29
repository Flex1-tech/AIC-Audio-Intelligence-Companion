from typing import Optional
from repositories.track_repository import TrackRepository
from core.state import app_state


class DatabaseService:
    """
    Service gérant la base de données vectorielle LanceDB et le cache de hash.
    """

    def __init__(self, repository: Optional[TrackRepository] = None):
        self.repository = repository or TrackRepository()

    def initialize_db(self) -> bool:
        try:
            table = self.repository.get_table()
            app_state.is_lancedb_ready = (table is not None)
            app_state.total_embeddings_in_db = self.repository.count_rows()
            if app_state.is_lancedb_ready:
                app_state.log_action(
                    "DATABASE_READY",
                    f"LanceDB prêt ({app_state.total_embeddings_in_db} morceaux en cache)")
            return app_state.is_lancedb_ready
        except Exception as e:
            app_state.is_lancedb_ready = False
            app_state.log_action(
                "DATABASE_ERROR",
                f"Échec initialisation LanceDB: {e}")
            return False

    def refresh_stats(self) -> None:
        if app_state.is_lancedb_ready:
            app_state.total_embeddings_in_db = self.repository.count_rows()
            app_state.notify()
