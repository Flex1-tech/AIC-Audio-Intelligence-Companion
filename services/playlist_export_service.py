import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from utils.path_utils import get_default_playlist_dir
from core.state import app_state


def make_m3u(playlist_paths: List[str], output_path: str) -> None:
    """Génère un fichier .m3u à partir d'une liste de chemins de fichiers audio."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for path in playlist_paths:
            p = Path(path)
            f.write(f"#EXTINF:-1,{p.stem}\n")
            f.write((p if p.is_absolute() else p.resolve()).as_uri() + "\n")


@dataclass
class ExportResult:
    """
    Résultat structuré d'un export de playlist.
    """

    success: bool
    file_path: str
    folder_path: str
    file_name: str
    track_count: int
    message: str


class PlaylistExportService:
    """
    Service dédié à la gestion, au nommage intelligent et à l'exportation des playlists.
    Gère la résolution cross-plateforme des dossiers, les conflits de nommage et la mémorisation des préférences.
    """

    def generate_smart_filename(self, target_dir: Path) -> str:
        """
        Génère un nom de fichier intelligent horodaté sans conflit :
        Format : AIC Playlist - YYYY-MM-DD - HH-MM.m3u8
        En cas de collision : AIC Playlist - YYYY-MM-DD - HH-MM (1).m3u8
        """
        now = datetime.datetime.now()
        base_name = f"AIC Playlist - {now.strftime('%Y-%m-%d - %H-%M')}"
        extension = ".m3u8"
        filename = f"{base_name}{extension}"
        counter = 1

        while (target_dir / filename).exists():
            filename = f"{base_name} ({counter}){extension}"
            counter += 1

        return filename

    def export_playlist(
        self,
        playlist_paths: List[str],
        custom_folder: Optional[str] = None,
    ) -> ExportResult:
        """
        Exporte la liste de pistes audio sous forme de fichier .m3u8 dans le dossier spécifié ou mémorisé.
        """
        if not playlist_paths:
            return ExportResult(
                success=False,
                file_path="",
                folder_path="",
                file_name="",
                track_count=0,
                message="Aucun morceau dans la playlist à exporter.",
            )

        # 1. Résolution du dossier cible
        folder_str = custom_folder or app_state.session.get_effective_export_folder()
        target_dir = Path(folder_str)

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback vers le dossier par défaut si le dossier personnalisé est inaccessible
            target_dir = get_default_playlist_dir()
            target_dir.mkdir(parents=True, exist_ok=True)

        # 2. Nommage intelligent sans conflit
        filename = self.generate_smart_filename(target_dir)
        full_path = target_dir / filename

        # 3. Écriture du fichier .m3u8 (UTF-8)
        try:
            make_m3u(playlist_paths, str(full_path))
            app_state.session.last_generated_playlist_path = str(full_path)
            app_state.session.export_folder_path = str(target_dir)
            app_state.notify()

            return ExportResult(
                success=True,
                file_path=str(full_path),
                folder_path=str(target_dir),
                file_name=filename,
                track_count=len(playlist_paths),
                message=f"Playlist exportée avec succès ({len(playlist_paths)} morceaux).",
            )
        except Exception as err:
            return ExportResult(
                success=False,
                file_path="",
                folder_path=str(target_dir),
                file_name=filename,
                track_count=len(playlist_paths),
                message=f"Erreur lors de l'écriture de la playlist : {err}",
            )
