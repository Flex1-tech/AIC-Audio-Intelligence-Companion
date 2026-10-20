"""
tests/test_playback_and_scan.py
---------------------------------
Tests unitaires pour l'Étape 5B :
1. Scan de dossiers par contenu (médias vidéo avec audio, vidéos muettes, non-médias, erreurs).
2. Même pipeline de validation (AudioValidationService) pour scan et import.
3. Préservation des optimisations 3B (bypass ffprobe sur hashes connus).
4. Export M3U8 avec chemins natifs absolus UTF-8 (accents, apostrophes, Unicode).
5. Service de lecture externe PlaybackService (VLC, fallback, Ouvrir avec, Explorateur).

NOTE : Pour préserver test_import_main_lightweight, aucun module lourd
(numpy, lancedb, etc.) n'est importé au niveau module.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest


# ---------------------------------------------------------------------------
# 1. Tests Scan de Dossier & Pipeline de Validation
# ---------------------------------------------------------------------------

def test_scan_directory_empty_folder():
    """Un dossier vide retourne 0 chemins découverts et 0 tracks sans planter."""
    from services.library_service import LibraryService

    temp_dir = tempfile.mkdtemp(prefix="aic_test_scan_empty_")
    try:
        service = LibraryService()
        discovered = service.scan_directory(temp_dir)
        assert discovered == []

        tracks, invalid_count = service.process_folder_import(temp_dir)
        assert len(tracks) == 0
        assert invalid_count == 0
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scan_directory_rejects_non_media_files():
    """Les fichiers texte, zip, pdf, images sont ignorés sans analyse ffprobe."""
    from services.library_service import LibraryService

    temp_dir = Path(tempfile.mkdtemp(prefix="aic_test_scan_nonmedia_"))
    try:
        # Création de faux fichiers non multimédias
        (temp_dir / "readme.txt").write_text("Ceci est un texte", encoding="utf-8")
        (temp_dir / "document.pdf").write_bytes(b"%PDF-1.4 header...")
        (temp_dir / "archive.zip").write_bytes(b"PK\x03\x04 fake zip content")
        (temp_dir / "photo.png").write_bytes(b"\x89PNG\r\n\x1a\n fake image content")

        service = LibraryService()
        with patch("services.audio_validation_service.is_valid_media") as mock_ffprobe:
            tracks, invalid_count = service.process_folder_import(str(temp_dir))
            assert len(tracks) == 0
            assert invalid_count == 4
            # ffprobe ne doit JAMAIS être appelé pour des fichiers rejetés par fleep
            mock_ffprobe.assert_not_called()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scan_directory_with_valid_audio_files():
    """Découvre et valide les fichiers audio admissibles."""
    from services.library_service import LibraryService
    from domain.track import Track

    temp_dir = Path(tempfile.mkdtemp(prefix="aic_test_scan_audio_"))
    try:
        f1 = temp_dir / "song1.mp3"
        f1.write_bytes(b"ID3\x03" + b"\x00" * 200)
        f2 = temp_dir / "song2.flac"
        f2.write_bytes(b"fLaC" + b"\x00" * 200)

        service = LibraryService()
        mock_t1 = Track(file_path=str(f1), file_name="song1.mp3", duration_seconds=180.0, audio_format="MP3")
        mock_t2 = Track(file_path=str(f2), file_name="song2.flac", duration_seconds=210.0, audio_format="FLAC")

        with patch.object(service.validation_service, "validate_file_paths", return_value=([mock_t1, mock_t2], 0)):
            tracks, invalid_count = service.process_folder_import(str(temp_dir))
            assert len(tracks) == 2
            assert invalid_count == 0
            assert tracks[0].file_name == "song1.mp3"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scan_directory_with_video_container_with_audio():
    """Un fichier .webm ou .mp4 avec audio est retenu et transmis à la validation."""
    from services.library_service import LibraryService
    from domain.track import Track

    temp_dir = Path(tempfile.mkdtemp(prefix="aic_test_scan_video_audio_"))
    try:
        video_file = temp_dir / "clip.webm"
        # Magic bytes EBML / WebM : 1A 45 DF A3
        video_file.write_bytes(b"\x1a\x45\xdf\xa3" + b"\x00" * 200)

        service = LibraryService()
        mock_track = Track(file_path=str(video_file), file_name="clip.webm", duration_seconds=240.0, audio_format="WEBM")

        with patch.object(service.validation_service, "validate_file_paths", return_value=([mock_track], 0)) as mock_val:
            tracks, invalid_count = service.process_folder_import(str(temp_dir))
            assert len(tracks) == 1
            assert tracks[0].file_name == "clip.webm"
            # Vérifie que clip.webm a bien été passé à validate_file_paths
            candidates = mock_val.call_args[0][0]
            assert str(video_file) in candidates
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_is_valid_media_rejects_video_without_audio():
    """is_valid_media() rejette les conteneurs vidéo sans piste audio."""
    from utils.audio_utils import is_valid_media
    import subprocess

    def mock_subprocess_run(cmd, *args, **kwargs):
        cmd_str = " ".join(cmd)
        if "select_streams" in cmd_str and "a:0" in cmd_str:
            # Aucun flux audio détecté (sortie vide)
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=b"", stderr=b"")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=b"", stderr=b"")

    with patch("subprocess.run", side_effect=mock_subprocess_run):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 100)
            f_path = f.name
        try:
            assert is_valid_media(f_path) is False
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)


def test_is_valid_media_accepts_video_with_audio():
    """is_valid_media() accepte les conteneurs vidéo avec au moins une piste audio."""
    from utils.audio_utils import is_valid_media
    import subprocess

    def mock_subprocess_run(cmd, *args, **kwargs):
        cmd_str = " ".join(cmd)
        if "select_streams" in cmd_str and "a:0" in cmd_str:
            # Flux audio détecté
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=b"audio\n", stderr=b"")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=b"", stderr=b"")

    with patch("subprocess.run", side_effect=mock_subprocess_run):
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(b"\x1a\x45\xdf\xa3" + b"\x00" * 100)
            f_path = f.name
        try:
            assert is_valid_media(f_path) is True
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)


def test_scan_directory_handles_permission_error():
    """Une erreur de permission ou d'accès sur un sous-dossier ne fait pas échouer tout le scan."""
    from services.library_service import LibraryService

    temp_dir = Path(tempfile.mkdtemp(prefix="aic_test_scan_perm_"))
    try:
        f1 = temp_dir / "valid.mp3"
        f1.write_bytes(b"ID3\x03" + b"\x00" * 100)

        service = LibraryService()

        orig_walk = os.walk
        def mock_walk(top, *args, **kwargs):
            yield (str(temp_dir), ["forbidden_dir"], ["valid.mp3"])
            raise PermissionError("Access is denied")

        with patch("os.walk", side_effect=mock_walk):
            paths = service.scan_directory(str(temp_dir))
            # Le scan a géré l'erreur sans crasher
            assert isinstance(paths, list)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_scan_and_import_share_same_validation_pipeline():
    """Vérifie que scan_directory et validate_file_paths utilisent la même instance de validation."""
    from services.library_service import LibraryService
    from services.audio_validation_service import AudioValidationService

    service = LibraryService()
    assert isinstance(service.validation_service, AudioValidationService)


def test_scan_preserves_step_3b_ffprobe_bypass():
    """Un fichier déjà indexé scanné dans un dossier contourne ffprobe grâce à son hash BLAKE3."""
    from services.library_service import LibraryService
    from services.audio_validation_service import AudioValidationService
    from extraction import get_file_hash

    temp_dir = Path(tempfile.mkdtemp(prefix="aic_test_scan_3b_"))
    try:
        f1 = temp_dir / "song1.mp3"
        f1.write_bytes(b"ID3\x03" + b"\x00" * 300)
        h1 = get_file_hash(str(f1))

        mock_repo = MagicMock()
        mock_repo.find_existing_hashes.return_value = {h1: {"file_path": str(f1), "file_hash": h1}}

        val_service = AudioValidationService(repository=mock_repo)
        lib_service = LibraryService(validation_service=val_service)

        with patch("services.audio_validation_service.is_audio_file", return_value=True), \
             patch("services.audio_validation_service.is_valid_media") as mock_ffprobe:
            tracks, invalid = lib_service.process_folder_import(str(temp_dir))
            mock_ffprobe.assert_not_called()
            assert len(tracks) == 1
            assert tracks[0].file_hash == h1
            assert invalid == 0
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# 2. Tests Export M3U8 (Chemins Absolus Natifs & Caractères Spéciaux)
# ---------------------------------------------------------------------------

def test_m3u8_native_absolute_paths_on_windows():
    """make_m3u() écrit des chemins natifs Windows (C:\\...) au lieu de file:///."""
    from services.playlist_export_service import make_m3u

    tracks = [
        r"C:\Users\HP\Music\Rock\Queen - Bohemian Rhapsody.mp3",
        r"C:\Users\HP\Music\Rap\4Keus - À l'époque du carré.mp3",
        r"D:\Audio\日本語\Track 01.flac",
    ]

    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False, mode="w", encoding="utf-8") as f:
        dest_path = f.name

    try:
        make_m3u(tracks, dest_path)
        content = Path(dest_path).read_text(encoding="utf-8")

        assert content.startswith("#EXTM3U")
        # Aucun file:/// ne doit figurer dans le fichier généré
        assert "file:///" not in content
        # Présence des chemins natifs intacts
        assert r"C:\Users\HP\Music\Rock\Queen - Bohemian Rhapsody.mp3" in content
        assert r"C:\Users\HP\Music\Rap\4Keus - À l'époque du carré.mp3" in content
        assert r"D:\Audio\日本語\Track 01.flac" in content
        # Présence de l'en-tête #EXTINF avec accents préservés
        assert "À l'époque du carré" in content
        assert "日本語" in content
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_m3u8_handles_apostrophes_spaces_and_accents():
    """Vérifie le respect des caractères spéciaux et apostrophes dans les noms de fichiers."""
    from services.playlist_export_service import make_m3u

    tracks = [
        r"C:\Music\Élégie & L'été d'amour (2024) [Bonus].wav",
    ]
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        dest_path = f.name

    try:
        make_m3u(tracks, dest_path)
        content = Path(dest_path).read_text(encoding="utf-8")
        assert "Élégie & L'été d'amour (2024) [Bonus]" in content
        assert r"C:\Music\Élégie & L'été d'amour (2024) [Bonus].wav" in content
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)


# ---------------------------------------------------------------------------
# 3. Tests Service de Lecture Externe (PlaybackService)
# ---------------------------------------------------------------------------

def test_playback_service_vlc_available():
    """Quand VLC est disponible, play_playlist le lance en tâche de fond."""
    from services.playback_service import PlaybackService
    import subprocess

    service = PlaybackService()
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        dummy_file = f.name

    try:
        with patch("services.playback_service.find_vlc", return_value=r"C:\Program Files\VideoLAN\VLC\vlc.exe"):
            with patch("subprocess.Popen") as mock_popen:
                success, msg = service.play_playlist(dummy_file, prefer_vlc=True)
                assert success is True
                assert "VLC" in msg
                mock_popen.assert_called_once()
                args = mock_popen.call_args[0][0]
                assert args[0] == r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                assert args[1] == dummy_file
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)


def test_playback_service_vlc_absent_fallback_to_default():
    """Quand VLC est absent, play_playlist bascule proprement sur l'application par défaut."""
    from services.playback_service import PlaybackService

    service = PlaybackService()
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        dummy_file = f.name

    try:
        with patch("services.playback_service.find_vlc", return_value=None):
            with patch.object(service, "play_with_default_app", return_value=(True, "Lecture lancée avec l'application par défaut")) as mock_default:
                success, msg = service.play_playlist(dummy_file, prefer_vlc=True)
                assert success is True
                assert "VLC non détecté" in msg
                mock_default.assert_called_once_with(dummy_file)
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)


def test_playback_service_play_track():
    """play_track lance l'ouverture du morceau individuel."""
    from services.playback_service import PlaybackService

    service = PlaybackService()
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        dummy_file = f.name

    try:
        with patch.object(service, "play_with_default_app", return_value=(True, "Ouverture réussie")) as mock_open:
            success, msg = service.play_track(dummy_file)
            assert success is True
            mock_open.assert_called_once_with(dummy_file)
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)


def test_playback_service_open_with_dialog_windows():
    """open_with_dialog invoque OpenAs_RunDLL sur Windows."""
    from services.playback_service import PlaybackService

    service = PlaybackService()
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        dummy_file = f.name

    try:
        with patch("sys.platform", "win32"):
            with patch("subprocess.Popen") as mock_popen:
                success, msg = service.open_with_dialog(dummy_file)
                assert success is True
                assert "Ouvrir avec" in msg
                mock_popen.assert_called_once()
                cmd = mock_popen.call_args[0][0]
                assert "OpenAs_RunDLL" in " ".join(cmd)
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)


def test_playback_service_show_in_explorer_windows():
    """show_in_explorer invoque explorer.exe /select sur Windows."""
    from services.playback_service import PlaybackService

    service = PlaybackService()
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        dummy_file = f.name

    try:
        with patch("sys.platform", "win32"):
            with patch("subprocess.Popen") as mock_popen:
                success, msg = service.show_in_explorer(dummy_file)
                assert success is True
                assert "Explorateur" in msg
                mock_popen.assert_called_once()
                cmd = mock_popen.call_args[0][0]
                assert "explorer.exe" in cmd[0]
                assert f"/select,{dummy_file}" in cmd[1]
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)


def test_playback_service_nonexistent_file():
    """play_track ou play_playlist retourne une erreur claire si le fichier est introuvable."""
    from services.playback_service import PlaybackService

    service = PlaybackService()
    success, msg = service.play_track(r"C:\nonexistent_song_12345.mp3")
    assert success is False
    assert "Fichier introuvable" in msg


def test_playback_service_launch_failure_reports_error():
    """Si le lancement système échoue (ex: PermissionError ou WinError), une erreur intelligible est retournée."""
    from services.playback_service import PlaybackService

    service = PlaybackService()
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        dummy_file = f.name

    try:
        with patch("sys.platform", "win32"):
            with patch("os.startfile", side_effect=OSError("Access denied")):
                success, msg = service.play_with_default_app(dummy_file)
                assert success is False
                assert "Access denied" in msg
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)
