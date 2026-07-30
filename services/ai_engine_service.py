from typing import Optional
from providers.musicnn_provider import MusicnnProvider
from core.state import app_state


class AIEngineService:
    """
    Service gérant le cycle de vie du modèle MusiCNN et les métriques de télémétrie IA.
    """

    def __init__(self, provider: Optional[MusicnnProvider] = None):
        self.provider = provider or MusicnnProvider()

    def initialize_engine() -> bool:
        pass

    def preload_resources(self) -> bool:
        try:
            session = self.provider.get_session()
            app_state.is_onnx_loaded = session is not None
            if app_state.is_onnx_loaded:
                app_state.log_action("AI_ENGINE_LOADED", "Modèle Musicnn ONNX chargé avec succès")
            return app_state.is_onnx_loaded
        except Exception as e:
            app_state.is_onnx_loaded = False
            app_state.log_action("AI_ENGINE_ERROR", f"Échec chargement Musicnn ONNX: {e}")
            return False
