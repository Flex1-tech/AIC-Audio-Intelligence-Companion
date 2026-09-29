"""Tests de non-régression et de validation des optimisations d'extraction audio (Étape 5A).

Vérifie :
1. Équivalence numérique et cas limites du calcul ZCR vectorisé vs librosa.
2. Invariance de la commande ffmpeg (-threads 0) et égalité binaire du décodage.
3. Cohérence et stabilité de l'extraction des représentants et des embeddings.
"""

from __future__ import annotations

import os
import subprocess
from unittest.mock import patch, MagicMock
import numpy as np
import pytest


def test_zcr_vectorized_synthetic_cases():
    """Vérifie l'équivalence entre le ZCR vectorisé et librosa sur divers signaux de test."""
    import librosa

    signals = {
        "constant_pos": np.ones(32000, dtype=np.float32),
        "constant_neg": -np.ones(32000, dtype=np.float32),
        "constant_zero": np.zeros(32000, dtype=np.float32),
        "alternating": np.tile([1.0, -1.0], 16000).astype(np.float32),
        "zeros_in_between": np.tile([1.0, 0.0, -1.0, 0.0], 8000).astype(np.float32),
        "sine_440": np.sin(2 * np.pi * 440 * np.linspace(0, 1, 32000)).astype(np.float32),
        "random": np.random.RandomState(42).randn(32000).astype(np.float32),
    }

    for name, sig in signals.items():
        zcr_librosa = float(np.mean(librosa.feature.zero_crossing_rate(sig)))
        zcr_vectorized = float(np.mean(np.abs(np.diff(np.signbit(sig)))))

        if "constant" in name:
            assert zcr_vectorized == 0.0
            assert zcr_librosa == 0.0
        else:
            # Tolérance numérique : librosa applique un padding de bord de 1024 échantillons
            # aux deux extrémités (mode='edge'), créant un écart d'environ 1-2% sur les signaux
            # courts de 32000 échantillons à transitions fréquentes.
            assert abs(zcr_librosa - zcr_vectorized) < 0.03, (
                f"Écart ZCR trop grand pour '{name}': {zcr_librosa} vs {zcr_vectorized}"
            )


def test_load_audio_command_includes_threads_flag():
    """Vérifie que load_audio inclut bien le drapeau '-threads 0' dans la commande ffmpeg."""
    from extraction import load_audio

    with patch("subprocess.run") as mock_run:
        fake_stdout = np.zeros(1600, dtype=np.float32).tobytes()
        mock_run.return_value = MagicMock(stdout=fake_stdout, returncode=0)

        audio = load_audio("dummy_test.mp3", sr=16000)

        assert mock_run.called
        cmd_called = mock_run.call_args[0][0]
        assert "-threads" in cmd_called
        idx = cmd_called.index("-threads")
        assert cmd_called[idx + 1] == "0"
        assert len(audio) == 1600


def test_load_audio_bit_exactness_with_real_file_if_available():
    """Vérifie que l'ajout de -threads 0 produit un résultat audio bit-exact sur un fichier réel s'il existe."""
    sample_file = r"C:\Users\HP\Music\musique 1\Musique_Traitee\Andrew Prishchecnko - Track 14.mp3"
    if not os.path.exists(sample_file):
        pytest.skip("Fichier de test réel non présent sur cette machine.")

    from extraction import load_audio

    # Décodage via load_audio actuel (avec -threads 0)
    audio_opt = load_audio(sample_file, sr=16000)

    # Décodage baseline sans -threads 0
    cmd_base = [
        "ffmpeg", "-nostdin", "-loglevel", "error", "-i", sample_file,
        "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-acodec", "pcm_f32le", "-"
    ]
    res_base = subprocess.run(cmd_base, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    audio_base = np.frombuffer(res_base.stdout, dtype=np.float32)

    assert len(audio_opt) == len(audio_base)
    assert np.max(np.abs(audio_opt - audio_base)) == 0.0


def test_extract_representative_batch_format_and_clustering():
    """Vérifie que extract_representative_batch fonctionne correctement et produit le format attendu."""
    from extraction import extract_representative_batch

    sr = 16000
    duration_sec = 25
    # Signal stérillement modulé pour avoir plusieurs segments distincts
    t = np.linspace(0, duration_sec, sr * duration_sec, dtype=np.float32)
    audio = 0.5 * np.sin(2 * np.pi * 220 * t) + 0.3 * np.cos(2 * np.pi * 440 * t)

    reps = extract_representative_batch(audio, sr=sr, segment_duration=10, n_segments=3)

    assert reps is not None
    assert reps.ndim == 2
    assert reps.shape[0] <= 3
    assert reps.shape[1] == 10 * sr
    assert reps.dtype == np.float32


def test_compute_embedding_real_track_if_available():
    """Vérifie que compute_embedding produit un embedding valide et normalisé sur un fichier réel."""
    sample_file = r"C:\Users\HP\Music\musique 1\Musique_Traitee\Andrew Prishchecnko - Track 14.mp3"
    if not os.path.exists(sample_file):
        pytest.skip("Fichier de test réel non présent sur cette machine.")

    from extraction import compute_embedding, load_musicnn

    session = load_musicnn()
    emb, taggram = compute_embedding(sample_file, session)

    assert emb is not None
    assert emb.shape == (200,)
    assert taggram.shape == (50,)
    assert abs(np.linalg.norm(emb) - 1.0) < 1e-4

