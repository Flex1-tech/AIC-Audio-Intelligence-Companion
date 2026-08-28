"""Pipeline d'extraction de caractéristiques audio et base vectorielle LanceDB."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING, Optional

import numpy as np

from utils.path_utils import get_asset_path

if TYPE_CHECKING:
    import lancedb
    import onnxruntime as ort


def extract_representative_batch(
    audio: np.ndarray,
    sr: int = 32000,
    segment_duration: int = 10,
    n_segments: int = 3,
    overlap: float = 0.5,
    rms_threshold_ratio: float = 0.1,
) -> np.ndarray:
    """Extrait les segments audio les plus représentatifs via un clustering léger."""
    import librosa
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    # SECURITE
    if audio is None or len(audio) == 0:
        return None

    audio = audio.astype(np.float32)

    # PARAMETRES
    samples_per_segment = int(sr * segment_duration)
    hop_size = int(samples_per_segment * (1.0 - overlap))

    if hop_size <= 0:
        raise ValueError("overlap trop élevé")

    # PADDING MINIMAL

    min_required = samples_per_segment

    if len(audio) < min_required:

        padding = min_required - len(audio)

        audio = np.pad(audio, (0, padding), mode="reflect")

    # SEGMENTATION AVEC OVERLAP

    segments = []

    for start in range(0, len(audio) - samples_per_segment + 1, hop_size):

        end = start + samples_per_segment

        segment = audio[start:end]

        segments.append(segment)

    segments = np.array(segments, dtype=np.float32)

    # FALLBACK

    if len(segments) == 0:

        padded = np.pad(audio, (0, max(0, samples_per_segment - len(audio))), mode="reflect")

        return padded[:samples_per_segment][None, :]

    # FILTRAGE DES SEGMENTS TROP SILENCIEUX

    rms_values = np.sqrt(np.mean(segments**2, axis=1))

    max_rms = np.max(rms_values)

    threshold = max_rms * rms_threshold_ratio

    valid_mask = rms_values > threshold

    valid_segments = segments[valid_mask]

    valid_rms = rms_values[valid_mask]

    # Fallback sécurité
    if len(valid_segments) == 0:

        valid_segments = segments

        valid_rms = rms_values

    # EXTRACTION FEATURES

    features = []

    for segment, rms in zip(valid_segments, valid_rms):

        # STFT unique

        stft = np.abs(librosa.stft(segment, n_fft=1024, hop_length=512))

        # Spectral Flux

        spectral_flux = np.mean(np.sqrt(np.sum(np.diff(stft, axis=1) ** 2, axis=0)))

        # MFCC

        mel_spec = librosa.feature.melspectrogram(S=stft**2, sr=sr, n_mels=40)

        log_mel = librosa.power_to_db(mel_spec, ref=np.max)

        mfcc = librosa.feature.mfcc(S=log_mel, n_mfcc=6)

        mfcc_1 = np.mean(mfcc[0])
        mfcc_3 = np.mean(mfcc[2])
        mfcc_5 = np.mean(mfcc[4])

        # Chroma (ajout important)

        chroma = librosa.feature.chroma_stft(S=stft, sr=sr)

        chroma_mean = np.mean(chroma)

        # Zero Crossing Rate

        zcr = np.mean(librosa.feature.zero_crossing_rate(segment))

        # Feature Vector

        feature_vector = [
            rms,
            spectral_flux,
            mfcc_1,
            mfcc_3,
            mfcc_5,
            chroma_mean,
            zcr,
        ]

        features.append(feature_vector)

    features = np.array(features, dtype=np.float32)

    # CAS TRIVIAL

    if len(valid_segments) <= n_segments:

        # Complète si besoin
        selected = list(valid_segments)

        while len(selected) < n_segments:
            selected.append(valid_segments[-1])

        return np.array(selected[:n_segments], dtype=np.float32)

    # NORMALISATION

    scaler = StandardScaler()

    features_scaled = scaler.fit_transform(features)

    # CLUSTERING

    kmeans = KMeans(
        init="k-means++",
        n_clusters=n_segments,
        random_state=42,
        n_init="auto",
    )

    labels = kmeans.fit_predict(features_scaled)

    centroids = kmeans.cluster_centers_

    # SELECTION REPRESENTATIVE

    selected_indices = []

    for cluster_id in range(n_segments):

        cluster_indices = np.where(labels == cluster_id)[0]

        if len(cluster_indices) == 0:
            continue

        cluster_features = features_scaled[cluster_indices]

        centroid = centroids[cluster_id]

        distances = np.linalg.norm(cluster_features - centroid, axis=1)

        best_local_index = np.argmin(distances)

        best_global_index = cluster_indices[best_local_index]

        selected_indices.append(best_global_index)

    # FALLBACK SECURITE

    if len(selected_indices) == 0:

        top_indices = np.argsort(valid_rms)[-n_segments:]

        selected_indices = top_indices.tolist()

    while len(selected_indices) < n_segments:
        selected_indices.append(selected_indices[-1])

    # TRI TEMPOREL

    selected_indices = sorted(selected_indices)

    # BATCH FINAL

    batch = valid_segments[selected_indices]

    return batch.astype(np.float32)


def has_vector_index(table):
    return any(hasattr(idx, "columns") and "vector" in idx.columns for idx in table.list_indices())


def get_file_hash(filepath: str):
    from blake3 import blake3

    hasher = blake3()
    hasher.update_mmap(filepath)
    return hasher.hexdigest()


def resolve_onnx_model_path(filename: str = "msd-musicnn-1.onnx") -> str:
    """Résout le chemin absolu déterministe du fichier modèle ONNX via multi-fallback cross-plateforme.

    Raises:
        FileNotFoundError: Si le fichier modèle n'existe dans aucun emplacement.
    """
    resolved = get_asset_path(filename)
    if resolved and resolved.is_file():
        return str(resolved)

    raise FileNotFoundError(
        f"Fichier modèle ONNX introuvable : '{filename}'. "
        "Vérifiez qu'il est présent dans assets/ ou dans le bundle de l'application."
    )


def load_musicnn(onnx_path: str = "msd-musicnn-1.onnx") -> ort.InferenceSession:
    """Charge la session d'inférence ONNX Runtime pour le modèle MusiCNN."""
    import onnxruntime as ort

    resolved_path = resolve_onnx_model_path(onnx_path)

    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

    cpu = os.cpu_count() or 2

    so.intra_op_num_threads = max(1, cpu // 2)
    so.inter_op_num_threads = 1

    so.enable_mem_pattern = True
    so.enable_cpu_mem_arena = True

    session = ort.InferenceSession(resolved_path, sess_options=so, providers=["CPUExecutionProvider"])

    return session


def load_audio(path: str, sr: int = 16000) -> np.ndarray:

    cmd = [
        "ffmpeg",
        "-nostdin",
        "-loglevel",
        "error",
        "-i",
        path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        str(sr),
        "-f",
        "f32le",
        "-acodec",
        "pcm_f32le",
        "-",
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        audio = np.frombuffer(result.stdout, dtype=np.float32)

        return audio

    except (subprocess.CalledProcessError, FileNotFoundError):
        return np.array([], dtype=np.float32)


def l2_normalize(v):
    return v / (np.linalg.norm(v) + 1e-10)


def get_existing_embeddings(hashes: list[str], table: lancedb.table.Table) -> dict[str, dict]:
    """Retourne un dict {hash: row} pour tous les hashes trouvés en base."""
    if not hashes:
        return {}

    hash_list = ", ".join(f"'{h}'" for h in hashes)
    rows = table.search().where(f"file_hash IN ({hash_list})").limit(len(hashes)).to_list()

    return {row["file_hash"]: row for row in rows}


def process_files_batch(
    path_dict: dict, session: ort.InferenceSession, table: lancedb.table.Table
) -> dict[str, np.ndarray]:
    """
    Traite tous les fichiers en batch :
    - 1 seule requête DB pour récupérer les embeddings existants
    - Calcul ONNX uniquement pour les nouveaux
    - 1 seul insert pour tous les nouveaux
    """
    # 1. Hash tous les fichiers
    file_metas = {}
    for path in path_dict:
        f = Path(path)
        if not f.is_file():
            continue
        file_metas[path] = {"hash": get_file_hash(path), "file": f}

    # 2. Une seule requête pour tout ce qui est déjà en base
    all_hashes = [m["hash"] for m in file_metas.values()]
    existing = get_existing_embeddings(all_hashes, table)  # {hash: row}

    # 3. Sépare connus / inconnus
    results = {}  # {path: vector}
    to_insert = []

    for path, meta in file_metas.items():
        h = meta["hash"]
        if h in existing:
            row = existing[h]
            # Mise à jour chemin si besoin
            if row["file_path"] != path:
                table.update(where=f"file_hash = '{h}'", values={"file_path": path})
            results[path] = np.array(row["vector"], dtype=np.float32)
        else:
            # À calculer — retourne (embedding, taggram)
            result = compute_embedding(path, session)
            if result is not None:
                vector, taggram = result
                results[path] = vector
                to_insert.append(
                    {
                        "file_name": meta["file"].name,
                        "file_path": path,
                        "file_hash": h,
                        "file_size_bytes": meta["file"].stat().st_size,
                        "taggram": taggram,
                        "vector": vector,
                    }
                )

    # 4. Un seul insert pour tous les nouveaux
    if to_insert:
        table.add(to_insert)

        if not has_vector_index(table) and len(table) >= 500:
            table.create_index(vector_column_name="vector", metric="cosine")

    return results  # {path: vector}


def audio_to_musicnn_batch(
    audio: np.ndarray,
    sr: int = 16000,
    n_fft: int = 512,
    hop_length: int = 256,
    n_mels: int = 96,
    patch_size: int = 187,
    patch_overlap: float = 0.5,
) -> np.ndarray:
    """
    Convertit un segment audio en batch MusiCNN.

    Retour :
        shape = (n_patches, 187, 96)
    """

    if not (0.0 <= patch_overlap < 1.0):
        raise ValueError("patch_overlap must be in [0,1)")

    import librosa

    # MEL SPECTROGRAM

    mel = librosa.feature.melspectrogram(y=audio, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels, power=2.0)

    # LOG COMPRESSION

    mel = librosa.power_to_db(mel, ref=1.0)

    # Normalisation approximative entre 0 et 1
    mel = np.clip((mel + 80.0) / 80.0, 0.0, 1.0)

    # PATCH EXTRACTION

    patches = []

    total_frames = mel.shape[1]

    if total_frames < patch_size:

        padding = patch_size - total_frames

        mel = np.pad(mel, ((0, 0), (0, padding)), mode="constant")

        total_frames = mel.shape[1]

    patch_hop = max(1, int(patch_size * (1.0 - patch_overlap)))
    for start in range(0, total_frames - patch_size + 1, patch_hop):

        patch = mel[:, start : start + patch_size]

        # IMPORTANT
        # (96,187) -> (187,96)
        patch = patch.T

        patches.append(patch)

    patches = np.array(patches, dtype=np.float32)

    return patches


def compute_embedding(path: str, session: ort.InferenceSession) -> Optional[tuple[np.ndarray, np.ndarray]]:
    """Calcule l'embedding et le taggram d'une piste audio via MusiCNN.

    Returns
    -------
    tuple[np.ndarray, np.ndarray] | None
        (embedding L2-normalisé dim=200, taggram moyenné dim=50),
        ou None si le fichier est invalide ou vide.
    """

    file = Path(path)

    if not file.is_file():
        return None

    # LOAD AUDIO

    audio = load_audio(path, sr=16000)

    # GLOBAL RMS NORMALIZATION

    target_rms = 0.1

    global_rms = np.sqrt(np.mean(audio**2))

    if global_rms > 1e-8:
        audio = audio * (target_rms / global_rms)

        max_peak = np.max(np.abs(audio))

        if max_peak > 0.95:
            audio = audio * (0.95 / max_peak)

        if audio is None or audio.size == 0:
            return None

    # SEGMENTS REPRESENTATIFS

    segments = extract_representative_batch(audio, sr=16000, segment_duration=10)

    if segments is None:
        return None

    input_name = session.get_inputs()[0].name
    # Sortie 0 : taggram (50 tags MSD) — Sortie 1 : embedding latent (200 dims)
    taggram_name = session.get_outputs()[0].name
    embedding_name = session.get_outputs()[1].name

    # CHAQUE SEGMENT
    all_patches = []
    patch_counts = []

    for segment in segments:

        # audio -> musicnn patches
        patches = audio_to_musicnn_batch(segment, sr=16000)

        # Stockage pour batch ONNX global
        all_patches.append(patches)
        patch_counts.append(patches.shape[0])

    # CONCATENATION GLOBALE (pour éviter les appels multiples à ONNX Runtime)
    all_patches = np.concatenate(all_patches, axis=0)

    # ONNX — récupération des deux sorties en un seul appel
    raw_taggrams, raw_embeddings = session.run([taggram_name, embedding_name], {input_name: all_patches})

    # Moyenne par segment puis moyenne globale
    segment_embeddings = []
    segment_taggrams = []

    start = 0

    for count in patch_counts:

        end = start + count

        segment_embeddings.append(np.mean(raw_embeddings[start:end], axis=0))
        segment_taggrams.append(np.mean(raw_taggrams[start:end], axis=0))

        start = end

    # MOYENNE GLOBALE
    final_embedding = np.mean(segment_embeddings, axis=0)
    final_taggram = np.mean(segment_taggrams, axis=0)

    return (
        l2_normalize(final_embedding.astype(np.float32)),
        final_taggram.astype(np.float32),
    )


def mmr_ranking(
    query_vector: np.ndarray,
    candidates: list[dict],
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Classe TOUS les candidats par ordre MMR (du meilleur au pire).

    Args:
        query_vector: Vecteur moyen des likés
        candidates: Liste de dicts avec 'file_path' et 'vector'
        lambda_param: 0.7 = 70% pertinence, 30% diversité

    Returns:
        Liste des candidats classés par MMR (tous les candidats, reordonnés)
    """
    if not candidates:
        return []

    n = len(candidates)

    # Convertir les vecteurs en matrice numpy
    candidate_vectors = np.stack([c["vector"] for c in candidates])

    # Similarité cosinus avec le query (produit scalaire car L2-normalisé)
    query_sims = candidate_vectors @ query_vector  # shape: (n_candidates,)

    # Matrice de similarité entre candidats
    sim_matrix = candidate_vectors @ candidate_vectors.T  # shape: (n, n)
    np.fill_diagonal(sim_matrix, -np.inf)  # s'auto-exclure

    selected = []
    selected_indices = set()
    remaining = set(range(n))

    # Itérativement : à chaque tour, choisir le meilleur MMR parmi les restants
    while remaining:
        best_mmr_score = -np.inf
        best_idx = None

        for idx in remaining:
            # Pertinence : similitude avec le query
            relevance = query_sims[idx]

            # Diversité : max similitude avec les déjà sélectionnés
            # Si c'est le premier, diversity = 0 (pas encore de sélectionnés)
            if selected_indices:
                diversity = np.max(sim_matrix[idx, list(selected_indices)])
            else:
                diversity = 0.0

            # Score MMR
            mmr_score = lambda_param * relevance - (1 - lambda_param) * diversity

            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_idx = idx

        if best_idx is not None:
            selected.append(candidates[best_idx])
            selected_indices.add(best_idx)
            remaining.remove(best_idx)

    return selected


def recommend_playlist(
    path_dict: dict,
    session: ort.InferenceSession,
    table: lancedb.table.Table,
    lambda_mmr: float = 0.7,
) -> list[str]:
    """
    Génère une playlist complète (tous les non-likés du dictionnaire)
    classée par MMR à partir du vecteur moyen des likés.

    Args:
        path_dict: {chemin_fichier: is_liked (bool)}
        session: Session ONNX Runtime
        table: Table LanceDB
        lambda_mmr: Ratio MMR (0.7 = 70% pertinence, 30% diversité)

    Returns:
        Liste des chemins des chansons recommandées (tous les non-likés, classés)
    """

    # Traite tous les fichiers en batch pour récupérer ou calculer leurs
    # vecteurs, et les stocker en base si besoin
    all_vectors = process_files_batch(path_dict, session, table)  # {path: vector}
    liked_vectors = [all_vectors[path] for path, liked in path_dict.items() if liked and path in all_vectors]

    if not liked_vectors:
        return []  # Pas de likés, pas de recommandations

    # Calcule le vecteur moyen des likés
    mean_vector = l2_normalize(np.mean(np.stack(liked_vectors), axis=0))

    # Construit la liste de tous les fichiers avec leurs vecteurs
    candidates = [{"file_path": path, "vector": all_vectors[path]} for path in path_dict.keys()]

    # Applique MMR pour classer TOUS les fichiers
    ranked = mmr_ranking(mean_vector, candidates, lambda_param=lambda_mmr)

    # 6. Retourne les chemins dans l'ordre MMR
    playlist_paths = [c["file_path"] for c in ranked]

    return playlist_paths


def _get_existing_tables(db) -> list[str]:
    """Helper pour récupérer la liste des tables LanceDB sans déclencher de DeprecationWarning."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        if hasattr(db, "table_names"):
            return list(db.table_names())
    return []


def _detect_schema_version(table) -> str:
    """Détecte la version du schéma de la table LanceDB.

    Returns:
        'v1' : ancien schéma (title, artist, duration_seconds, pas de taggram)
        'v2' : nouveau schéma (taggram[50], pas de title/artist/duration_seconds)
        'unknown' : schéma non reconnu
    """
    col_names = {field.name for field in table.schema}
    has_taggram = "taggram" in col_names
    has_legacy = "title" in col_names or "artist" in col_names or "duration_seconds" in col_names

    if has_taggram and not has_legacy:
        return "v2"
    if has_legacy and not has_taggram:
        return "v1"
    if has_taggram and has_legacy:
        return "v1_mixed"  # Transition partielle
    return "unknown"


def _migrate_v1_to_v2(db, table) -> "lancedb.table.Table":
    """Migre la table audio_embeddings du schéma v1 (legacy) vers le schéma v2 (actuel).

    Stratégie :
        1. Sauvegarde de l'ancienne table sous audio_embeddings_backup_v1
        2. Récupération de toutes les lignes migrables (celles qui ont un vecteur valide)
        3. Suppression de l'ancienne table
        4. Recréation avec le nouveau schéma via TrackEmbeddingModel
        5. Insertion des lignes récupérées avec un taggram vide (zeros)
        6. En cas d'échec, la sauvegarde reste intacte pour rollback manuel

    Returns:
        La nouvelle table migrée.
    """
    import logging

    log = logging.getLogger("aic.migration")

    log.info("[MIGRATION] Schéma v1 détecté. Début de la migration vers v2...")

    # 1. Sauvegarde : copie vers une table backup
    backup_name = "audio_embeddings_backup_v1"
    try:
        existing_tables = _get_existing_tables(db)
        if backup_name in existing_tables:
            log.info(f"[MIGRATION] Backup '{backup_name}' déjà présent — sauvegarde ignorée.")
        else:
            old_rows = table.search().limit(100_000).to_list()
            if old_rows:
                db.create_table(backup_name, data=old_rows, exist_ok=True)
                log.info(f"[MIGRATION] {len(old_rows)} lignes sauvegardées dans '{backup_name}'.")
            else:
                log.info("[MIGRATION] Table vide, pas de sauvegarde nécessaire.")
    except Exception as backup_err:
        log.warning(f"[MIGRATION] Sauvegarde échouée (non bloquant) : {backup_err}")

    # 2. Récupération des lignes migrables
    migrated_rows = []
    try:
        old_rows = table.search().limit(100_000).to_list()
        for row in old_rows:
            vec = row.get("vector")
            if vec is None:
                continue
            vec_arr = np.array(vec, dtype=np.float32)
            if vec_arr.shape != (200,):
                continue
            # Taggram vide (zeros) — sera recalculé lors de la prochaine recommandation
            taggram = np.zeros(50, dtype=np.float32)
            migrated_rows.append(
                {
                    "file_hash": row.get("file_hash", ""),
                    "file_name": row.get("file_name", ""),
                    "file_path": row.get("file_path", ""),
                    "file_size_bytes": int(row.get("file_size_bytes", 0)),
                    "taggram": taggram,
                    "vector": vec_arr,
                }
            )
        log.info(f"[MIGRATION] {len(migrated_rows)}/{len(old_rows)} lignes récupérées pour migration.")
    except Exception as read_err:
        log.error(f"[MIGRATION] Erreur lecture ancienne table : {read_err}")
        migrated_rows = []

    # 3. Suppression de l'ancienne table et recréation avec le nouveau schéma
    try:
        db.drop_table("audio_embeddings")
    except Exception as drop_err:
        log.error(f"[MIGRATION] Impossible de supprimer l'ancienne table : {drop_err}")
        raise RuntimeError(f"Migration annulée : suppression échouée — {drop_err}")

    from schema import TrackEmbeddingModel

    new_table = db.create_table("audio_embeddings", schema=TrackEmbeddingModel, exist_ok=False)

    # 4. Insertion des lignes migrées
    if migrated_rows:
        try:
            new_table.add(migrated_rows)
            log.info(f"[MIGRATION] {len(migrated_rows)} lignes insérées dans la nouvelle table v2.")
            log.info(f"[MIGRATION] Migration terminée : {len(migrated_rows)} entrées conservées.")
        except Exception as insert_err:
            log.error(f"[MIGRATION] Insertion échouée : {insert_err}")
            # La table est vide mais valide — pas de rollback automatique
            log.warning(
                f"[MIGRATION] AVERTISSEMENT : Insertion échouée ({insert_err}). La table est vide. Rollback : renommer {backup_name}."
            )
    else:
        log.info("[MIGRATION] Aucune ligne à migrer. Nouvelle table vide créée.")

    return new_table


def initialize_database(db_path: str) -> lancedb.table.Table:
    """
    Initialise la connexion à LanceDB et retourne la table d'embeddings.

    Gestion du cycle de vie complet :
    - Si la table n'existe pas → création avec le schéma actuel (v2)
    - Si la table existe avec le schéma v1 (legacy) → migration automatique vers v2
    - Si la table existe avec le schéma v2 → ouverture directe (idempotent)

    Migration v1→v2 :
    - v1 : file_hash, file_name, file_path, file_size_bytes, vector[200], title, artist, duration_seconds
    - v2 : file_hash, file_name, file_path, file_size_bytes, taggram[50], vector[200]
    """
    import lancedb
    from lancedb.index import BTree
    from schema import TrackEmbeddingModel

    db = lancedb.connect(db_path)
    existing_tables = _get_existing_tables(db)

    if "audio_embeddings" not in existing_tables:
        # Première utilisation : création directe avec le schéma v2
        table = db.create_table("audio_embeddings", schema=TrackEmbeddingModel, exist_ok=True)
    else:
        table = db.open_table("audio_embeddings")
        version = _detect_schema_version(table)

        if version in ("v1", "v1_mixed", "unknown"):
            # Migration nécessaire
            table = _migrate_v1_to_v2(db, table)
        # version == "v2" → table déjà à jour, rien à faire

    # Index scalaire sur file_hash (idempotent, <1ms si déjà indexé)
    if not any("file_hash" in idx.columns for idx in table.list_indices()):
        table.create_index("file_hash", config=BTree(), replace=True)

    return table


def make_m3u(playlist_paths: list[str], output_path: str) -> None:
    """Génère un fichier .m3u à partir d'une liste de chemins de fichiers audio."""
    from services.playlist_export_service import make_m3u as _make_m3u

    _make_m3u(playlist_paths, output_path)
