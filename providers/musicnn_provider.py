import onnxruntime as ort
from typing import Optional
import numpy as np

from extraction import load_musicnn, compute_embedding


class MusicnnProvider:
    """
    Fournisseur d'inférence audio Deep Learning MusiCNN (ONNX Runtime).
    """

    def __init__(self, model_path: str = "./msd-musicnn-1.onnx"):
        self.model_path = model_path
        self._session: Optional[ort.InferenceSession] = None

    def get_session(self) -> ort.InferenceSession:
        if self._session is None:
            self._session = load_musicnn(self.model_path)
        return self._session

    def is_model_loaded(self) -> bool:
        return self._session is not None

    def extract_embedding(self, file_path: str) -> Optional[np.ndarray]:
        session = self.get_session()
        return compute_embedding(file_path, session)
