import os
from typing import List, Tuple
from utils.audio_utils import is_audio_file, is_valid_media
from domain.track import Track
from repositories.track_repository import TrackRepository


class AudioValidationService:
    """
    Service de validation des fichiers audio via FFprobe et Fleep.

    Optimisation : les fichiers dont le hash BLAKE3 est déjà présent dans LanceDB
    (signifiant qu'ils ont déjà été validés et indexés) ne passent pas par ffprobe,
    ce qui réduit drastiquement le temps de rescan d'une bibliothèque existante.
    Les nouveaux fichiers (hash inconnu) restent soumis à fleep + ffprobe.
    """

    def __init__(self, repository: TrackRepository = None):
        self.repository = repository or TrackRepository()

    def validate_file_paths(
        self,
        file_paths: List[str],
        skip_ffprobe_for_known: bool = True,
    ) -> Tuple[List[Track], int]:
        """
        Valide une liste de chemins de fichiers et retourne les objets Track valides
        ainsi que le nombre de fichiers ignorés.

        Stratégie d'optimisation (skip_ffprobe_for_known=True, défaut) :
        1. Calcule BLAKE3 pour chaque fichier présent sur disque (fleep passe toujours).
        2. Effectue un seul lookup batch pour retrouver les hashes déjà en base LanceDB.
        3. Les fichiers dont le hash est connu (déjà validé) contournent ffprobe.
        4. Les fichiers dont le hash est inconnu passent par fleep + ffprobe comme
           auparavant, garantissant qu'aucun fichier corrompu n'est accepté.
        """
        from extraction import get_file_hash

        valid_tracks: List[Track] = []
        invalid_count = 0

        # ── Phase 1 : fleep + BLAKE3 pour tous les fichiers existants ─────────
        # fleep lit uniquement 128 octets (détection du type MIME).
        # BLAKE3 via mmap est très rapide (~4–13 ms).
        file_stats: dict = {}  # path -> {hash, stat}
        for path in file_paths:
            if not os.path.isfile(path):
                invalid_count += 1
                continue
            try:
                if not is_audio_file(path):
                    invalid_count += 1
                    continue
                h = get_file_hash(path)
                st = os.stat(path)
                file_stats[path] = {"hash": h, "stat": st}
            except Exception:
                invalid_count += 1

        if not file_stats:
            return valid_tracks, invalid_count

        # ── Phase 2 : Lookup batch unique des hashes déjà en base LanceDB ────
        all_hashes = [m["hash"] for m in file_stats.values()]
        known_entries: dict = {}  # hash -> row (file_path stocké en base)
        if skip_ffprobe_for_known:
            try:
                known_entries = self.repository.find_existing_hashes(all_hashes)
            except Exception:
                known_entries = {}  # Fallback sécurisé : tout repasse par ffprobe

        # ── Phase 3 : Validation conditionnelle ───────────────────────────────
        for path, meta in file_stats.items():
            h = meta["hash"]
            st = meta["stat"]
            try:
                if h in known_entries:
                    # Hash déjà validé en base : bypass ffprobe
                    row = known_entries[h]
                    # Mise à jour du chemin si le fichier a été déplacé/renommé
                    if row["file_path"] != path:
                        try:
                            tbl = self.repository.get_table()
                            tbl.update(
                                where=f"file_hash = '{h}'",
                                values={"file_path": path},
                            )
                        except Exception:
                            pass  # Mise à jour non critique : ne pas bloquer la validation
                    track = Track(
                        file_path=path,
                        file_size_bytes=st.st_size,
                        file_hash=h,
                        is_valid=True,
                    )
                    valid_tracks.append(track)
                else:
                    # Hash inconnu : validation complète avec ffprobe (comportement actuel)
                    if is_valid_media(path):
                        track = Track(
                            file_path=path,
                            file_size_bytes=st.st_size,
                            file_hash=h,
                            is_valid=True,
                        )
                        valid_tracks.append(track)
                    else:
                        invalid_count += 1
            except Exception:
                invalid_count += 1

        return valid_tracks, invalid_count
