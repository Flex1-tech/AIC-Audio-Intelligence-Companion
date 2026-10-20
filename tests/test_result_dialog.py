"""
tests/test_result_dialog.py
------------------------------
Tests unitaires pour la gestion des dossiers d'export (PlaylistExportService)
et le nouveau ResultDialog.

Vérifie :
1. Export automatique (persist_as_default=True) : met à jour export_folder_path.
2. Export ponctuel (persist_as_default=False) : préserve export_folder_path.
3. set_default_export_folder : mémorise le dossier par défaut.
4. Validité du fichier .m3u8 dans un dossier custom (URIs absolues).
5. Absence de RuntimeWarning sur les callbacks du ResultDialog.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock


# ── Fixtures de base ──────────────────────────────────────────────────────────

def _make_fake_tracks(tmpdir: str) -> list[str]:
    """Crée des fichiers audio factices dans tmpdir et retourne leurs chemins absolus."""
    paths = []
    for name in ("track1.mp3", "track2.flac", "track3.mp3"):
        p = Path(tmpdir) / name
        p.write_bytes(b"\x00" * 128)  # Contenu binaire minimal
        paths.append(str(p))
    return paths


# ── Tests PlaylistExportService ───────────────────────────────────────────────

class TestPlaylistExportService:
    def _get_service(self):
        from services.playlist_export_service import PlaylistExportService
        return PlaylistExportService()

    def test_export_default_persists_folder(self, tmp_path):
        """Export automatique (persist_as_default=True) doit mettre à jour export_folder_path."""
        from core.state import app_state
        original = app_state.session.export_folder_path

        service = self._get_service()
        tracks = [str(tmp_path / "a.mp3"), str(tmp_path / "b.mp3")]
        for t in tracks:
            Path(t).write_bytes(b"\x00" * 64)

        result = service.export_playlist(tracks, custom_folder=str(tmp_path), persist_as_default=True)
        assert result.success
        assert app_state.session.export_folder_path == str(tmp_path)

        # Restauration
        app_state.session.export_folder_path = original

    def test_export_oneoff_preserves_default_folder(self, tmp_path):
        """Export ponctuel (persist_as_default=False) ne doit PAS modifier export_folder_path."""
        from core.state import app_state

        original_default = "/original/default/folder"
        app_state.session.export_folder_path = original_default

        service = self._get_service()
        tracks = [str(tmp_path / "a.mp3"), str(tmp_path / "b.mp3")]
        for t in tracks:
            Path(t).write_bytes(b"\x00" * 64)

        result = service.export_playlist(
            tracks,
            custom_folder=str(tmp_path),
            persist_as_default=False,
        )
        assert result.success
        # Le dossier par défaut doit être inchangé
        assert app_state.session.export_folder_path == original_default

        # Restauration
        app_state.session.export_folder_path = ""

    def test_set_default_export_folder(self, tmp_path):
        """set_default_export_folder doit mémoriser le dossier dans app_state."""
        from core.state import app_state

        service = self._get_service()
        new_folder = str(tmp_path / "my_custom_exports")
        Path(new_folder).mkdir(parents=True, exist_ok=True)

        service.set_default_export_folder(new_folder)
        assert app_state.session.export_folder_path == new_folder

        # Restauration
        app_state.session.export_folder_path = ""

    def test_export_stores_playlist_paths_in_result(self, tmp_path):
        """ExportResult.playlist_paths doit contenir les chemins d'origine."""
        service = self._get_service()
        tracks = [str(tmp_path / "a.mp3"), str(tmp_path / "b.mp3")]
        for t in tracks:
            Path(t).write_bytes(b"\x00" * 64)

        result = service.export_playlist(tracks, custom_folder=str(tmp_path), persist_as_default=False)
        assert result.success
        assert result.playlist_paths == tracks

    def test_m3u8_uses_absolute_paths_in_custom_folder(self, tmp_path):
        """Le fichier .m3u8 doit contenir des chemins absolus natifs, indépendants du dossier cible."""
        from services.playlist_export_service import make_m3u

        export_dir = tmp_path / "exports"
        export_dir.mkdir()

        # Fichiers sources dans un dossier complètement différent
        source_dir = tmp_path / "source_music"
        source_dir.mkdir()
        track1 = source_dir / "song1.mp3"
        track2 = source_dir / "song2.flac"
        track1.write_bytes(b"\x00" * 64)
        track2.write_bytes(b"\x00" * 64)

        out_file = export_dir / "playlist.m3u8"
        make_m3u([str(track1), str(track2)], str(out_file))

        content = out_file.read_text(encoding="utf-8")
        assert "#EXTM3U" in content
        assert "song1" in content
        assert "song2" in content
        # Toutes les lignes d'entrée doivent être des chemins absolus natifs
        lines = [ln for ln in content.splitlines() if ln and not ln.startswith("#")]
        for line in lines:
            p = Path(line)
            assert p.is_absolute(), f"Le chemin n'est pas absolu : {line!r}"
        # Les chemins ne doivent PAS contenir le chemin du dossier export
        for line in lines:
            assert str(export_dir) not in line, (
                f"Le chemin contient le dossier d'export alors qu'il devrait pointer vers la source : {line!r}"
            )

    def test_empty_playlist_returns_failure(self, tmp_path):
        """Une playlist vide doit retourner un ExportResult.success=False sans créer de fichier."""
        service = self._get_service()
        result = service.export_playlist([], custom_folder=str(tmp_path))
        assert not result.success
        assert result.track_count == 0

    def test_last_playlist_path_updated_on_export(self, tmp_path):
        """app_state.session.last_generated_playlist_path doit être mis à jour après chaque export."""
        from core.state import app_state
        from services.playlist_export_service import PlaylistExportService

        service = PlaylistExportService()
        track = tmp_path / "song.mp3"
        track.write_bytes(b"\x00" * 64)

        result = service.export_playlist([str(track)], custom_folder=str(tmp_path), persist_as_default=False)
        assert result.success
        assert app_state.session.last_generated_playlist_path == result.file_path


# ── Tests ResultDialog : Absence de RuntimeWarning ────────────────────────────

class TestResultDialogCallbackSafety:
    """Vérifie que les callbacks sync et async ne produisent pas de RuntimeWarning ni de TypeError."""

    def test_sync_callback_executed_directly(self):
        """Un callback synchrone doit être exécuté directement sans appeler run_task ni lever RuntimeWarning."""
        from ui.components.result_dialog import ResultDialog
        import warnings

        called = []

        def sync_callback():
            called.append(True)

        dialog = ResultDialog(
            count=5,
            file_name="test.m3u8",
            on_close=sync_callback,
        )
        mock_page = MagicMock()
        with patch.object(ResultDialog, "page", new_callable=PropertyMock, return_value=mock_page):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")
                dialog._handle_close()

        runtime_warnings = [w for w in warning_list if issubclass(w.category, RuntimeWarning)]
        assert not runtime_warnings, f"RuntimeWarning inattendu : {runtime_warnings}"
        assert called, "Le callback synchrone n'a pas été appelé."
        assert not mock_page.run_task.called, "run_task ne doit pas être appelé pour un callback synchrone."

    def test_native_async_callback_passed_as_coroutine_function(self):
        """Un callback `async def` doit être transmis directement à page.run_task en tant que coroutine function."""
        from ui.components.result_dialog import ResultDialog
        import inspect
        import warnings

        async def async_callback():
            pass

        dialog = ResultDialog(
            count=5,
            file_name="test.m3u8",
            on_export_to=async_callback,
        )
        mock_page = MagicMock()
        with patch.object(ResultDialog, "page", new_callable=PropertyMock, return_value=mock_page):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")
                dialog._handle_export_to()

        runtime_warnings = [w for w in warning_list if issubclass(w.category, RuntimeWarning)]
        assert not runtime_warnings, f"RuntimeWarning inattendu : {runtime_warnings}"
        assert mock_page.run_task.called, "page.run_task doit être appelé pour un callback async."

        # Règle stricte Flet 0.86.4 : le handler transmis DOIT être une coroutine function
        handler = mock_page.run_task.call_args[0][0]
        assert inspect.iscoroutinefunction(handler), (
            f"Flet 0.86.4 requiert inspect.iscoroutinefunction(handler) == True, reçu {handler}"
        )
        assert handler is async_callback, "Le callback async natif doit être transmis directement."

    def test_wrapper_returning_coroutine_passed_safely(self):
        """Un wrapper/lambda synchrone retournant une coroutine doit être géré via _await_coroutine."""
        from ui.components.result_dialog import ResultDialog
        import inspect
        import warnings

        async def inner_async():
            pass

        wrapper_callback = lambda: inner_async()

        dialog = ResultDialog(
            count=5,
            file_name="test.m3u8",
            on_regenerate=wrapper_callback,
        )
        mock_page = MagicMock()
        with patch.object(ResultDialog, "page", new_callable=PropertyMock, return_value=mock_page):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")
                dialog._handle_regenerate()

        runtime_warnings = [w for w in warning_list if issubclass(w.category, RuntimeWarning)]
        assert not runtime_warnings, f"RuntimeWarning inattendu : {runtime_warnings}"
        assert mock_page.run_task.called, "page.run_task doit être appelé."

        handler = mock_page.run_task.call_args[0][0]
        coro_arg = mock_page.run_task.call_args[0][1]
        assert inspect.iscoroutinefunction(handler), (
            f"Le handler Flet doit être une coroutine function, reçu {handler}"
        )
        assert inspect.iscoroutine(coro_arg), "La coroutine retournée doit être passée en argument."
        coro_arg.close()  # Nettoyage propre

    def test_detached_control_closes_coroutine_without_warning(self):
        """Lorsque le contrôle n'est pas encore attaché à une page, les coroutines doivent être fermées proprement."""
        from ui.components.result_dialog import ResultDialog
        import warnings

        async def inner_async():
            pass

        wrapper_callback = lambda: inner_async()

        dialog = ResultDialog(
            count=5,
            file_name="test.m3u8",
            on_regenerate=wrapper_callback,
        )
        # dialog non attaché : dialog.page lève RuntimeError
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            dialog._handle_regenerate()

        runtime_warnings = [w for w in warning_list if issubclass(w.category, RuntimeWarning)]
        assert not runtime_warnings, f"RuntimeWarning inattendu : {runtime_warnings}"

    def test_update_export_location_updates_display(self):
        """update_export_location doit mettre à jour les textes réactifs du modal."""
        from ui.components.result_dialog import ResultDialog

        dialog = ResultDialog(
            count=3,
            folder_path="/old/folder",
            file_name="old.m3u8",
            file_path="/old/folder/old.m3u8",
            is_default_folder=True,
        )
        # ft.Control.page est read-only → le laisser à None (comportement hors Flet event loop)
        # update_export_location appelle page.update() seulement si self.page est truthy.

        dialog.update_export_location(
            folder_path="/new/folder",
            file_path="/new/folder/new.m3u8",
            file_name="new.m3u8",
            is_default=False,
        )
        assert dialog.folder_path == "/new/folder"
        assert dialog.file_name == "new.m3u8"
        assert not dialog._is_current_default
        assert dialog._set_default_btn.visible is True
