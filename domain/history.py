from dataclasses import dataclass, field
import time
from typing import Dict, Any


@dataclass
class ActionLog:
    """
    Représente une action historisée dans AIC pour le journal et l'Undo/Redo.
    """
    action_type: str  # ex: "IMPORT_FILES", "LIKE_TRACK", "RESET_LIBRARY", "GENERATE_RECOMMENDATION"
    description: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def formatted_time(self) -> str:
        return time.strftime("%H:%M:%S", time.localtime(self.timestamp))
