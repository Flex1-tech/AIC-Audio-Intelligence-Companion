"""
tests/test_ffprobe_conditional.py
-----------------------------------
Tests unitaires pour le ffprobe conditionnel de l'étape 3B.
Vérifie :
- nouveau fichier → ffprobe appelé (hash inconnu de la base)
- fichier inchangé et connu → 0 ffprobe (bypass)
- fichier modifié après validation → hash différent → ffprobe appelé
- fichier corrompu → hash différent → ffprobe invalide → rejet
- fichier renommé/déplacé → reconnu par hash → file_path mis à jour → 0 ffprobe
- fichier supprimé → pas de crash
- lookup LanceDB failure → fallback sécurisé avec ffprobe
- skip_ffprobe_for_known=False → comportement legacy complet
- lookup batch appelé exactement 1 fois

NOTE : Ce fichier n'importe aucun module lourd (numpy, lancedb, extraction…)
au niveau module afin de ne pas polluer sys.modules avant l'exécution de
test_import_main_lightweight. Tous les imports lourds sont effectués à
l'intérieur des fixtures ou des fonctions de test.
"""

import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import pytest


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_setup():
    """
    Crée un environnement minimal :
    - Deux faux fichiers (contenu binaire quelconque suffisant pour BLAKE3)
    - Une table LanceDB avec track_a indexé
    - Un AudioValidationService injecté avec ce repo

    Les imports lourds (numpy, lancedb, extraction…) sont effectués ICI,
    à l'intérieur de la fixture, pour ne pas contaminer sys.modules avant
    que test_import_main_lightweight ait pu tourner.
    """
    import numpy as np
    import lancedb
    from extraction import get_file_hash
    from services.audio_validation_service import AudioValidationService
    from repositories.track_repository import TrackRepository
    from schema import TrackEmbeddingModel

    temp_dir = Path(tempfile.mkdtemp(prefix="aic_test_ffprobe_cond_"))
    db = lancedb.connect(str(temp_dir / "test_lancedb"))
    table = db.create_table("audio_embeddings", schema=TrackEmbeddingModel)

    repo = TrackRepository(db_path=str(temp_dir / "test_lancedb"))
    repo._table = table

    file_a = temp_dir / "track_a.mp3"
    file_a.write_bytes(b"audio content A valid for testing" * 100)
    hash_a = get_file_hash(str(file_a))

    file_b = temp_dir / "track_b.mp3"
    file_b.write_bytes(b"audio content B never indexed" * 100)
    hash_b = get_file_hash(str(file_b))

    # Indexer track_a en base (simuler un fichier déjà validé et indexé)
    table.add([{
        "file_name": file_a.name,
        "file_path": str(file_a),
        "file_hash": hash_a,
        "file_size_bytes": file_a.stat().st_size,
        "taggram": np.zeros(50, dtype=np.float32),
        "vector": np.random.randn(200).astype(np.float32),
    }])

    val_service = AudioValidationService(repository=repo)

    yield {
        "temp_dir": temp_dir,
        "table": table,
        "repo": repo,
        "val_service": val_service,
        "file_a": file_a,
        "hash_a": hash_a,
        "file_b": file_b,
        "hash_b": hash_b,
    }

    shutil.rmtree(str(temp_dir), ignore_errors=True)


# ---------------------------------------------------------------------------
# Tests de base
# ---------------------------------------------------------------------------

def test_known_file_skips_ffprobe(temp_setup):
    """Fichier inchangé et connu dans LanceDB → ffprobe non appelé."""
    file_a = temp_setup["file_a"]
    val_service = temp_setup["val_service"]

    with patch("services.audio_validation_service.is_audio_file", return_value=True), \
         patch("services.audio_validation_service.is_valid_media") as mock_valid:
        tracks, invalid = val_service.validate_file_paths([str(file_a)])
        mock_valid.assert_not_called()

    assert len(tracks) == 1, f"Track attendu mais non retourné. invalid={invalid}"
    assert tracks[0].file_hash == temp_setup["hash_a"]
    assert invalid == 0


def test_new_file_calls_ffprobe(temp_setup):
    """Nouveau fichier non indexé → is_valid_media (ffprobe) appelé."""
    file_b = temp_setup["file_b"]
    val_service = temp_setup["val_service"]

    with patch("services.audio_validation_service.is_audio_file", return_value=True), \
         patch("services.audio_validation_service.is_valid_media", return_value=True) as mock_valid:
        tracks, invalid = val_service.validate_file_paths([str(file_b)])
        mock_valid.assert_called_once()

    assert len(tracks) == 1
    assert invalid == 0


def test_modified_file_calls_ffprobe(temp_setup):
    """Fichier modifié après indexation → nouveau hash → is_valid_media appelé."""
    from extraction import get_file_hash

    file_a = temp_setup["file_a"]
    val_service = temp_setup["val_service"]

    file_a.write_bytes(b"COMPLETELY DIFFERENT CONTENT - new version" * 100)
    hash_new = get_file_hash(str(file_a))
    assert hash_new != temp_setup["hash_a"], "Le hash devrait avoir changé"

    with patch("services.audio_validation_service.is_audio_file", return_value=True), \
         patch("services.audio_validation_service.is_valid_media", return_value=True) as mock_valid:
        tracks, invalid = val_service.validate_file_paths([str(file_a)])
        mock_valid.assert_called_once()

    assert len(tracks) == 1
    assert tracks[0].file_hash == hash_new


def test_corrupted_file_rejected(temp_setup):
    """Fichier corrompu (hash inconnu) → ffprobe retourne invalide → rejeté."""
    temp_dir = temp_setup["temp_dir"]
    val_service = temp_setup["val_service"]

    corrupt = temp_dir / "corrupt.mp3"
    corrupt.write_bytes(b"random trash bytes for corrupted test" * 100)

    with patch("services.audio_validation_service.is_audio_file", return_value=True), \
         patch("services.audio_validation_service.is_valid_media", return_value=False):
        tracks, invalid = val_service.validate_file_paths([str(corrupt)])

    assert len(tracks) == 0
    assert invalid == 1


def test_renamed_file_updates_path_no_ffprobe(temp_setup):
    """Fichier renommé → reconnu par hash → file_path mis à jour → 0 ffprobe."""
    file_a = temp_setup["file_a"]
    temp_dir = temp_setup["temp_dir"]
    val_service = temp_setup["val_service"]
    table = temp_setup["table"]

    renamed = temp_dir / "track_a_renamed.mp3"
    shutil.copy(str(file_a), str(renamed))

    with patch("services.audio_validation_service.is_audio_file", return_value=True), \
         patch("services.audio_validation_service.is_valid_media") as mock_valid:
        tracks, invalid = val_service.validate_file_paths([str(renamed)])
        mock_valid.assert_not_called()

    assert len(tracks) == 1
    assert tracks[0].file_path == str(renamed)
    assert invalid == 0

    rows = table.search().where(f"file_hash = '{temp_setup['hash_a']}'").to_list()
    assert len(rows) == 1
    assert rows[0]["file_path"] == str(renamed)


def test_deleted_file_no_crash(temp_setup):
    """Fichier inexistant → géré proprement, pas de crash."""
    val_service = temp_setup["val_service"]

    tracks, invalid = val_service.validate_file_paths(["/nonexistent/path/track.mp3"])
    assert len(tracks) == 0
    assert invalid == 1


def test_fallback_when_lookup_fails(temp_setup):
    """Échec du lookup LanceDB → fallback : is_valid_media appelé pour tous les fichiers."""
    file_a = temp_setup["file_a"]
    val_service = temp_setup["val_service"]

    with patch.object(val_service.repository, "find_existing_hashes", side_effect=RuntimeError("DB down")):
        with patch("services.audio_validation_service.is_audio_file", return_value=True), \
             patch("services.audio_validation_service.is_valid_media", return_value=True) as mock_valid:
            tracks, invalid = val_service.validate_file_paths([str(file_a)])
            mock_valid.assert_called_once()

    assert len(tracks) == 1


def test_skip_ffprobe_false_always_calls_ffprobe(temp_setup):
    """Avec skip_ffprobe_for_known=False → comportement legacy : ffprobe pour tous."""
    file_a = temp_setup["file_a"]
    val_service = temp_setup["val_service"]

    with patch("services.audio_validation_service.is_audio_file", return_value=True), \
         patch("services.audio_validation_service.is_valid_media", return_value=True) as mock_valid:
        tracks, invalid = val_service.validate_file_paths(
            [str(file_a)], skip_ffprobe_for_known=False
        )
        mock_valid.assert_called_once()

    assert len(tracks) == 1


# ---------------------------------------------------------------------------
# Tests de garanties architecturales
# ---------------------------------------------------------------------------

def test_batch_lookup_called_exactly_once(temp_setup):
    """Le lookup LanceDB est effectué en UN SEUL appel batch pour toute la liste."""
    file_a = temp_setup["file_a"]
    file_b = temp_setup["file_b"]
    val_service = temp_setup["val_service"]

    lookup_call_count = {"count": 0}
    orig_find = val_service.repository.find_existing_hashes

    def counting_find(hashes):
        lookup_call_count["count"] += 1
        return orig_find(hashes)

    val_service.repository.find_existing_hashes = counting_find

    with patch("services.audio_validation_service.is_audio_file", return_value=True), \
         patch("services.audio_validation_service.is_valid_media", return_value=True):
        val_service.validate_file_paths([str(file_a), str(file_b)])

    assert lookup_call_count["count"] == 1, (
        f"Lookup DB appelé {lookup_call_count['count']} fois au lieu de 1 !"
    )


def test_mixed_batch_known_and_unknown(temp_setup):
    """Batch avec un fichier connu et un nouveau → 1 seul ffprobe, 0 pour le connu."""
    file_a = temp_setup["file_a"]
    file_b = temp_setup["file_b"]
    val_service = temp_setup["val_service"]

    ffprobe_calls_on = []

    def mock_valid(path):
        ffprobe_calls_on.append(path)
        return True

    with patch("services.audio_validation_service.is_audio_file", return_value=True), \
         patch("services.audio_validation_service.is_valid_media", side_effect=mock_valid):
        tracks, invalid = val_service.validate_file_paths([str(file_a), str(file_b)])

    assert str(file_a) not in ffprobe_calls_on, "ffprobe appelé sur track_a (connu) !"
    assert str(file_b) in ffprobe_calls_on, "ffprobe pas appelé sur track_b (nouveau) !"
    assert len(tracks) == 2
    assert invalid == 0


def test_generation_no_extra_blake3(temp_setup):
    """Après scan, la génération ne refait aucun BLAKE3 si track_hashes transmis."""
    import extraction

    file_a = temp_setup["file_a"]
    table = temp_setup["table"]
    val_service = temp_setup["val_service"]

    with patch("services.audio_validation_service.is_audio_file", return_value=True):
        tracks, _ = val_service.validate_file_paths([str(file_a)])
    track_hashes = {t.file_path: t.file_hash for t in tracks}

    path_dict = {str(file_a): False}
    blake3_calls = {"count": 0}
    orig = extraction.get_file_hash

    def counting_hash(p):
        blake3_calls["count"] += 1
        return orig(p)

    extraction.get_file_hash = counting_hash
    try:
        extraction.process_files_batch(
            path_dict, session=None, table=table, track_hashes=track_hashes
        )
    finally:
        extraction.get_file_hash = orig

    assert blake3_calls["count"] == 0, (
        f"BLAKE3 recalculé {blake3_calls['count']} fois pendant la génération !"
    )
