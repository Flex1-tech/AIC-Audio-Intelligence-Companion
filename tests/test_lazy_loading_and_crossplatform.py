"""
tests/test_lazy_loading_and_crossplatform.py
----------------------------------------------
Suite de tests automatisés multiplateforme (OS-independent) pour AIC :
1. Absence des modules lourds au démarrage (boot)
2. Résolution cross-plateforme des chemins utilisateur et des assets
3. Initialisation lazy et thread-safety de LanceDB
4. Initialisation lazy et thread-safety de l'InferenceSession ONNX
5. Export M3U8 multiplateforme avec URIs file://
"""

import os
import sys
import tempfile
import threading
from pathlib import Path


def test_import_main_lightweight():
    """Vérifie que l'importation de main.py ne charge aucune dépendance IA/ML/DB lourde."""
    import main  # noqa: F401

    heavy_libs = [
        "numpy",
        "scipy",
        "sklearn",
        "librosa",
        "numba",
        "llvmlite",
        "pyarrow",
        "onnxruntime",
        "lancedb",
        "soundfile",
        "soxr",
        "audioread",
    ]

    for lib in heavy_libs:
        is_present = lib in sys.modules or any(m.startswith(lib + ".") for m in sys.modules)
        assert not is_present, f"La bibliothèque lourde '{lib}' a été importée de manière prématurée au boot !"


def test_crossplatform_paths():
    """Vérifie la résolution déterministe et OS-independent des répertoires utilisateur."""
    from utils.path_utils import get_user_data_dir, get_default_playlist_dir

    data_dir = get_user_data_dir()
    assert isinstance(data_dir, Path)
    assert data_dir.exists()

    playlist_dir = get_default_playlist_dir()
    assert isinstance(playlist_dir, Path)
    assert playlist_dir.exists()


def test_asset_path_resolution():
    """Vérifie que les assets clés sont correctement résolus via get_asset_path."""
    from utils.path_utils import get_asset_path

    icon_path = get_asset_path("icon.ico")
    assert icon_path is not None
    assert icon_path.exists()
    assert icon_path.is_file()

    model_path = get_asset_path("msd-musicnn-1.onnx")
    assert model_path is not None
    assert model_path.exists()
    assert model_path.is_file()


def test_lazy_lancedb_and_thread_safety():
    """Vérifie l'initialisation lazy et la thread-safety de TrackRepository."""
    from repositories.track_repository import TrackRepository

    with tempfile.TemporaryDirectory() as tmpdir:
        repo = TrackRepository(db_path=os.path.join(tmpdir, "test_lancedb"))

        tables = []
        errors = []

        def worker():
            try:
                tbl = repo.get_table()
                tables.append(tbl)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Erreurs de concurrence LanceDB : {errors}"
        assert len(tables) == 5
        # Toutes les instances doivent pointer sur la même table unique
        first_table = tables[0]
        for tbl in tables:
            assert tbl is first_table, "La table LanceDB a été réinstanciée de manière non thread-safe !"


def test_lazy_onnx_and_thread_safety():
    """Vérifie l'initialisation lazy et la thread-safety de MusicnnProvider."""
    from providers.musicnn_provider import MusicnnProvider

    provider = MusicnnProvider()

    sessions = []
    errors = []

    def worker():
        try:
            sess = provider.get_session()
            sessions.append(sess)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Erreurs de concurrence ONNX : {errors}"
    assert len(sessions) == 5
    # Toutes les instances doivent pointer sur la même session unique mise en cache
    first_sess = sessions[0]
    for sess in sessions:
        assert sess is first_sess, "La session ONNX a été réinstanciée de manière non thread-safe !"


def test_make_m3u_export():
    """Vérifie la génération de fichiers M3U8 multiplateforme."""
    from services.playlist_export_service import make_m3u

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "test_export.m3u8")
        sample_tracks = [
            os.path.join(tmpdir, "track1.mp3"),
            os.path.join(tmpdir, "track2.flac"),
        ]
        make_m3u(sample_tracks, out_file)

        assert os.path.exists(out_file)
        with open(out_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "#EXTM3U" in content
        assert "track1" in content
        assert "track2" in content
