from typing import Callable, List, Dict, Any, Optional
from domain.library import MusicLibrary
from domain.session import SessionState
from domain.history import ActionLog
import time


class AppState:
    """
    Magasin d'état central réactif (Single Source of Truth) pour AIC.
    Gère la bibliothèque musicale, la session, la télémétrie et les abonnés aux événements.
    """

    def __init__(self):
        self.library = MusicLibrary()
        self.session = SessionState()
        self.action_history: List[ActionLog] = []

        # Télémétrie IA et Moteur
        self.is_onnx_loaded: bool = False
        self.is_lancedb_ready: bool = False
        self.total_embeddings_in_db: int = 0
        self.last_inference_duration_ms: float = 0.0
        self.is_processing: bool = False
        self.processing_status_message: str = "Prêt"

        # Listeners (Callbacks pour mise à jour UI réactive)
        self._listeners: List[Callable[[], None]] = []

    def subscribe(self, listener: Callable[[], None]) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[], None]) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def notify(self) -> None:
        for listener in self._listeners:
            try:
                listener()
            except Exception as e:
                print(f"[AppState] Erreur notification listener: {e}")

    def log_action(self, action_type: str, description: str,
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        log = ActionLog(
            action_type=action_type,
            description=description,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.action_history.append(log)
        self.notify()


# Instance unique partagée
app_state = AppState()
