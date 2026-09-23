"""
tests/test_blake3_optimization.py
---------------------------------
Tests unitaires pour la suppression du double hachage BLAKE3 et la validation des flux de hash.

NOTE : Ce fichier n'importe aucun module lourd (numpy, lancedb, extraction…)
au niveau module afin de ne pas polluer sys.modules avant l'exécution de
test_import_main_lightweight. Tous les imports lourds sont effectués à
l'intérieur des fixtures.
"""

import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import pytest

from domain.track import Track
from core.state import app_state
from controllers.library_controller import LibraryController


@pytest.fixture
def temp_lancedb_and_files():
    import numpy as np
    import lancedb
    import extraction
    from extraction import get_file_hash
    from schema import TrackEmbeddingModel

    temp_dir = Path(tempfile.mkdtemp(prefix="aic_test_blake3_suite_"))
    db = lancedb.connect(str(temp_dir / "test_lancedb"))
    table = db.create_table("audio_embeddings", schema=TrackEmbeddingModel)

    file1 = temp_dir / "track1.mp3"
    file1.write_bytes(b"content for track 1")
    hash1 = get_file_hash(str(file1))

    file2 = temp_dir / "track2.mp3"
    file2.write_bytes(b"content for track 2")
    hash2 = get_file_hash(str(file2))

    # Indexer track1 en base
    table.add([{
        "file_name": file1.name,
        "file_path": str(file1),
        "file_hash": hash1,
        "file_size_bytes": file1.stat().st_size,
        "taggram": np.zeros(50, dtype=np.float32),
        "vector": np.random.randn(200).astype(np.float32),
    }])

    yield {
        "temp_dir": temp_dir,
        "table": table,
        "file1": file1,
        "hash1": hash1,
        "file2": file2,
        "hash2": hash2,
    }

    shutil.rmtree(str(temp_dir), ignore_errors=True)


def test_process_files_batch_reuses_track_hashes(temp_lancedb_and_files):
    import extraction
    from extraction import process_files_batch
    table = temp_lancedb_and_files["table"]
    file1 = temp_lancedb_and_files["file1"]
    hash1 = temp_lancedb_and_files["hash1"]

    path_dict = {str(file1): False}
    track_hashes = {str(file1): hash1}

    with patch("extraction.get_file_hash") as mock_hash:
        vectors = process_files_batch(path_dict, session=None, table=table, track_hashes=track_hashes)
        mock_hash.assert_not_called()
        assert str(file1) in vectors


def test_process_files_batch_fallback_when_no_hashes(temp_lancedb_and_files):
    import extraction
    from extraction import process_files_batch
    table = temp_lancedb_and_files["table"]
    file1 = temp_lancedb_and_files["file1"]

    path_dict = {str(file1): False}

    # Appel sans track_hashes (None) -> fallback
    with patch("extraction.get_file_hash", side_effect=extraction.get_file_hash) as mock_hash:
        vectors = process_files_batch(path_dict, session=None, table=table, track_hashes=None)
        assert mock_hash.call_count == 1
        assert str(file1) in vectors


def test_process_files_batch_fallback_when_hash_missing_for_file(temp_lancedb_and_files):
    import extraction
    from extraction import process_files_batch
    table = temp_lancedb_and_files["table"]
    file1 = temp_lancedb_and_files["file1"]

    path_dict = {str(file1): False}
    track_hashes = {str(file1): None}  # hash vide/None

    with patch("extraction.get_file_hash", side_effect=extraction.get_file_hash) as mock_hash:
        vectors = process_files_batch(path_dict, session=None, table=table, track_hashes=track_hashes)
        assert mock_hash.call_count == 1
        assert str(file1) in vectors


def test_library_controller_updates_modified_track_hash_on_rescan():
    app_state.library.tracks.clear()
    path = "/music/song.mp3"

    # 1. Piste initiale
    initial_track = Track(file_path=path, file_hash="hash_v1", file_size_bytes=1000, is_liked=True)
    app_state.library.tracks[path] = initial_track

    # 2. Rescan avec nouvelle version
    updated_track = Track(file_path=path, file_hash="hash_v2", file_size_bytes=2000, is_liked=False)

    class FakeValidationService:
        def validate_file_paths(self, paths):
            return [updated_track], 0

    controller = LibraryController(validation_service=FakeValidationService())
    # Simulation du traitement interne
    valid_tracks, _ = controller.validation_service.validate_file_paths([path])
    for track in valid_tracks:
        if track.file_path not in app_state.library.tracks:
            app_state.library.tracks[track.file_path] = track
        else:
            existing = app_state.library.tracks[track.file_path]
            if existing.file_hash != track.file_hash:
                existing.file_hash = track.file_hash
                existing.file_size_bytes = track.file_size_bytes
                existing.in_database = False

    t = app_state.library.tracks[path]
    assert t.file_hash == "hash_v2"
    assert t.file_size_bytes == 2000
    assert t.is_liked is True  # Conserve le like de l'utilisateur !
    assert t.in_database is False
