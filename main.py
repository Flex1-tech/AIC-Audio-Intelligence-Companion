"""Point d'entrée de l'application et initialisation de l'interface Flet."""

import datetime
import os
import pathlib
import sys
import traceback


def trace(msg: str) -> None:
    """Traceur de diagnostic bas-niveau : écrit immédiatement chaque étape sur disque."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    pid = os.getpid()
    log_line = f"[{timestamp}] [PID {pid}] {msg}\n"
    print(log_line, end="", flush=True)

    targets = [
        pathlib.Path("aic_boot_trace.log"),
        pathlib.Path.home() / "aic_boot_trace.log",
    ]
    appdata = os.environ.get("APPDATA")
    if appdata:
        targets.append(pathlib.Path(appdata) / "AIC" / "logs" / "aic_boot_trace.log")

    for dest in targets:
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "a", encoding="utf-8") as f:
                f.write(log_line)
                f.flush()
                os.fsync(f.fileno())
        except Exception:
            pass


trace("=== DIAGNOSTIC BOOT START ===")
trace(f"STEP 00: Python executable = {sys.executable}")
trace(f"STEP 01: Python version = {sys.version}")
trace(f"STEP 02: CWD = {pathlib.Path.cwd()}")
trace(f"STEP 03: sys.path = {sys.path}")

# Enregistrement dynamique des répertoires DLL pour C-extensions sous Windows (Python 3.8+)
if os.name == "nt":
    trace("STEP 04: Scanning & registering DLL directories for C-extensions...")
    for p in sys.path:
        p_path = pathlib.Path(p)
        if p_path.is_dir():
            try:
                os.add_dll_directory(str(p_path))
            except Exception:
                pass
            try:
                for sub in p_path.iterdir():
                    if sub.is_dir():
                        try:
                            os.add_dll_directory(str(sub))
                        except Exception:
                            pass
            except Exception:
                pass
    trace("STEP 04: DLL directories registered OK")


def _early_crash_handler(exc_type, exc_value, exc_tb):
    lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    trace(f"FATAL UNCAUGHT EXCEPTION:\n{''.join(lines)}")
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _early_crash_handler

# ── Imports applicatifs instrumentés ─────────────────────────────────────────
trace("STEP 05: Importing threading...")
import threading  # noqa: E402

trace("STEP 06: Importing flet...")
import flet as ft  # noqa: E402

trace("STEP 07: Importing blake3...")
import blake3  # noqa: E402, F401

trace("STEP 08: Importing fleep...")
import fleep  # noqa: E402, F401

trace("STEP 09: Importing numpy...")
import numpy  # noqa: E402, F401

trace("STEP 10: Importing onnxruntime...")
import onnxruntime  # noqa: E402, F401

trace("STEP 11: Importing lancedb...")
import lancedb  # noqa: E402, F401

trace("STEP 12: Patching lazy_loader & importing librosa...")
try:
    import ast
    import lazy_loader

    _LIBROSA_STUBS = {
        "librosa": """from . import core, beat, decompose, display, effects, feature, filters, onset, segment, sequence, util
from ._cache import cache as cache
from .util.exceptions import LibrosaError as LibrosaError, ParameterError as ParameterError
from .util.files import example as example, ex as ex, cite as cite
from .version import show_versions as show_versions
from .core import (
    frames_to_samples as frames_to_samples, frames_to_time as frames_to_time,
    samples_to_frames as samples_to_frames, samples_to_time as samples_to_time,
    time_to_samples as time_to_samples, time_to_frames as time_to_frames,
    blocks_to_samples as blocks_to_samples, blocks_to_frames as blocks_to_frames,
    blocks_to_time as blocks_to_time, note_to_hz as note_to_hz,
    note_to_midi as note_to_midi, midi_to_hz as midi_to_hz,
    midi_to_note as midi_to_note, hz_to_note as hz_to_note,
    hz_to_midi as hz_to_midi, hz_to_mel as hz_to_mel,
    hz_to_octs as hz_to_octs, hz_to_fjs as hz_to_fjs,
    mel_to_hz as mel_to_hz, octs_to_hz as octs_to_hz,
    A4_to_tuning as A4_to_tuning, tuning_to_A4 as tuning_to_A4,
    fft_frequencies as fft_frequencies, cqt_frequencies as cqt_frequencies,
    mel_frequencies as mel_frequencies, tempo_frequencies as tempo_frequencies,
    fourier_tempo_frequencies as fourier_tempo_frequencies,
    A_weighting as A_weighting, B_weighting as B_weighting,
    C_weighting as C_weighting, D_weighting as D_weighting,
    Z_weighting as Z_weighting, frequency_weighting as frequency_weighting,
    multi_frequency_weighting as multi_frequency_weighting,
    samples_like as samples_like, times_like as times_like,
    midi_to_svara_h as midi_to_svara_h, midi_to_svara_c as midi_to_svara_c,
    note_to_svara_h as note_to_svara_h, note_to_svara_c as note_to_svara_c,
    hz_to_svara_h as hz_to_svara_h, hz_to_svara_c as hz_to_svara_c,
    load as load, stream as stream, to_mono as to_mono,
    resample as resample, get_duration as get_duration,
    get_samplerate as get_samplerate, autocorrelate as autocorrelate,
    lpc as lpc, zero_crossings as zero_crossings,
    clicks as clicks, tone as tone, chirp as chirp,
    mu_compress as mu_compress, mu_expand as mu_expand,
    stft as stft, istft as istft, magphase as magphase,
    iirt as iirt, reassigned_spectrogram as reassigned_spectrogram,
    phase_vocoder as phase_vocoder, perceptual_weighting as perceptual_weighting,
    power_to_db as power_to_db, db_to_power as db_to_power,
    amplitude_to_db as amplitude_to_db, db_to_amplitude as db_to_amplitude,
    fmt as fmt, pcen as pcen, griffinlim as griffinlim,
    estimate_tuning as estimate_tuning, pitch_tuning as pitch_tuning,
    piptrack as piptrack, yin as yin, pyin as pyin,
    cqt as cqt, hybrid_cqt as hybrid_cqt, pseudo_cqt as pseudo_cqt,
    icqt as icqt, griffinlim_cqt as griffinlim_cqt,
    vqt as vqt, salience as salience, interp_harmonics as interp_harmonics,
    f0_harmonics as f0_harmonics, get_fftlib as get_fftlib,
    set_fftlib as set_fftlib, key_to_degrees as key_to_degrees,
    key_to_notes as key_to_notes, mela_to_degrees as mela_to_degrees,
    mela_to_svara as mela_to_svara, thaat_to_degrees as thaat_to_degrees,
    list_mela as list_mela, list_thaat as list_thaat,
    fifths_to_note as fifths_to_note, interval_to_fjs as interval_to_fjs,
    interval_frequencies as interval_frequencies,
    pythagorean_intervals as pythagorean_intervals,
    plimit_intervals as plimit_intervals
)""",
        "librosa.core": """from .convert import (
    frames_to_samples as frames_to_samples, frames_to_time as frames_to_time,
    samples_to_frames as samples_to_frames, samples_to_time as samples_to_time,
    time_to_samples as time_to_samples, time_to_frames as time_to_frames,
    blocks_to_samples as blocks_to_samples, blocks_to_frames as blocks_to_frames,
    blocks_to_time as blocks_to_time, note_to_hz as note_to_hz,
    note_to_midi as note_to_midi, midi_to_hz as midi_to_hz,
    midi_to_note as midi_to_note, hz_to_note as hz_to_note,
    hz_to_midi as hz_to_midi, hz_to_mel as hz_to_mel,
    hz_to_octs as hz_to_octs, hz_to_fjs as hz_to_fjs,
    mel_to_hz as mel_to_hz, octs_to_hz as octs_to_hz,
    A4_to_tuning as A4_to_tuning, tuning_to_A4 as tuning_to_A4,
    fft_frequencies as fft_frequencies, cqt_frequencies as cqt_frequencies,
    mel_frequencies as mel_frequencies, tempo_frequencies as tempo_frequencies,
    fourier_tempo_frequencies as fourier_tempo_frequencies,
    A_weighting as A_weighting, B_weighting as B_weighting,
    C_weighting as C_weighting, D_weighting as D_weighting,
    Z_weighting as Z_weighting, frequency_weighting as frequency_weighting,
    multi_frequency_weighting as multi_frequency_weighting,
    samples_like as samples_like, times_like as times_like,
    midi_to_svara_h as midi_to_svara_h, midi_to_svara_c as midi_to_svara_c,
    note_to_svara_h as note_to_svara_h, note_to_svara_c as note_to_svara_c,
    hz_to_svara_h as hz_to_svara_h, hz_to_svara_c as hz_to_svara_c
)
from .audio import (
    load as load, stream as stream, to_mono as to_mono, resample as resample,
    get_duration as get_duration, get_samplerate as get_samplerate,
    autocorrelate as autocorrelate, lpc as lpc, zero_crossings as zero_crossings,
    clicks as clicks, tone as tone, chirp as chirp, mu_compress as mu_compress, mu_expand as mu_expand
)
from .spectrum import (
    stft as stft, istft as istft, magphase as magphase, iirt as iirt,
    reassigned_spectrogram as reassigned_spectrogram, phase_vocoder as phase_vocoder,
    perceptual_weighting as perceptual_weighting, power_to_db as power_to_db,
    db_to_power as db_to_power, amplitude_to_db as amplitude_to_db,
    db_to_amplitude as db_to_amplitude, fmt as fmt, pcen as pcen, griffinlim as griffinlim
)
from .pitch import estimate_tuning as estimate_tuning, pitch_tuning as pitch_tuning, piptrack as piptrack, yin as yin, pyin as pyin
from .constantq import cqt as cqt, hybrid_cqt as hybrid_cqt, pseudo_cqt as pseudo_cqt, icqt as icqt, griffinlim_cqt as griffinlim_cqt, vqt as vqt
from .harmonic import salience as salience, interp_harmonics as interp_harmonics, f0_harmonics as f0_harmonics
from .fft import get_fftlib as get_fftlib, set_fftlib as set_fftlib
from .notation import (
    key_to_degrees as key_to_degrees, key_to_notes as key_to_notes, mela_to_degrees as mela_to_degrees,
    mela_to_svara as mela_to_svara, thaat_to_degrees as thaat_to_degrees, list_mela as list_mela,
    list_thaat as list_thaat, fifths_to_note as fifths_to_note, interval_to_fjs as interval_to_fjs
)
from .intervals import interval_frequencies as interval_frequencies, pythagorean_intervals as pythagorean_intervals, plimit_intervals as plimit_intervals
""",
        "librosa.feature": """from .utils import delta as delta, stack_memory as stack_memory
from .spectral import (
    spectral_centroid as spectral_centroid, spectral_bandwidth as spectral_bandwidth,
    spectral_contrast as spectral_contrast, spectral_rolloff as spectral_rolloff,
    spectral_flatness as spectral_flatness, poly_features as poly_features,
    rms as rms, zero_crossing_rate as zero_crossing_rate, chroma_stft as chroma_stft,
    chroma_cqt as chroma_cqt, chroma_cens as chroma_cens, chroma_vqt as chroma_vqt,
    melspectrogram as melspectrogram, mfcc as mfcc, tonnetz as tonnetz
)
from .rhythm import tempogram as tempogram, fourier_tempogram as fourier_tempogram, tempo as tempo, tempogram_ratio as tempogram_ratio
from . import inverse as inverse
""",
        "librosa.util": """from . import decorators, exceptions
from .files import find_files as find_files, example as example, ex as ex, list_examples as list_examples, example_info as example_info, cite as cite
from .matching import match_intervals as match_intervals, match_events as match_events
from .deprecation import Deprecated as Deprecated, rename_kw as rename_kw
from ._nnls import nnls as nnls
from .utils import (
    MAX_MEM_BLOCK as MAX_MEM_BLOCK, frame as frame, pad_center as pad_center,
    expand_to as expand_to, fix_length as fix_length, valid_audio as valid_audio,
    valid_int as valid_int, is_positive_int as is_positive_int, valid_intervals as valid_intervals,
    fix_frames as fix_frames, axis_sort as axis_sort, localmax as localmax,
    localmin as localmin, normalize as normalize, peak_pick as peak_pick,
    sparsify_rows as sparsify_rows, shear as shear, stack as stack,
    fill_off_diagonal as fill_off_diagonal, index_to_slice as index_to_slice,
    sync as sync, softmask as softmask, buf_to_float as buf_to_float,
    tiny as tiny, cyclic_gradient as cyclic_gradient, dtype_r2c as dtype_r2c,
    dtype_c2r as dtype_c2r, count_unique as count_unique, is_unique as is_unique,
    abs2 as abs2, phasor as phasor
)""",
    }

    _orig_attach_stub = lazy_loader.attach_stub

    def _safe_attach_stub(package_name: str, filename: str):
        stubfile = filename if filename.endswith("i") else f"{os.path.splitext(filename)[0]}.pyi"
        if not os.path.exists(stubfile):
            if package_name in _LIBROSA_STUBS:
                stub_node = ast.parse(_LIBROSA_STUBS[package_name])
                visitor = lazy_loader._StubVisitor()
                visitor.visit(stub_node)
                return lazy_loader.attach(package_name, visitor._submodules, visitor._submod_attrs)
        return _orig_attach_stub(package_name, filename)

    lazy_loader.attach_stub = _safe_attach_stub
except Exception as patch_err:
    trace(f"lazy_loader patch warning: {patch_err}")

import librosa  # noqa: E402, F401

trace("STEP 13: Importing core.state...")
from core.state import app_state  # noqa: E402

trace("STEP 14: Importing controllers...")
from controllers.library_controller import LibraryController  # noqa: E402
from controllers.recommendation_controller import RecommendationController  # noqa: E402

trace("STEP 15: Importing services...")
from services.ai_engine_service import AIEngineService  # noqa: E402
from services.database_service import DatabaseService  # noqa: E402

trace("STEP 16: Importing UI components...")
from ui.components.result_dialog import ResultDialog  # noqa: E402
from ui.components.splash_screen import SplashScreen  # noqa: E402
from ui.design_system import get_dark_theme, get_light_theme  # noqa: E402
from ui.design_system.colors import ObsidianColors  # noqa: E402
from ui.views.main_layout import MainLayout  # noqa: E402
from utils.path_utils import setup_logging, get_asset_path, write_crash_log  # noqa: E402

trace("STEP 17: All imports completed successfully OK")

# Initialisation du logger applicatif
logger = setup_logging()


def _handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Hook enrichi : log via le logger ET via write_crash_log."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # Écriture systématique dans aic_crash.log (%APPDATA%/AIC/logs/aic_crash.log, CWD, Home)
    write_crash_log(exc_type, exc_value, exc_traceback, origin="UNCAUGHT_MAIN_PROCESS")
    # Écriture dans aic.log (logger applicatif)
    logger.critical("Uncaught exception in main process:", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = _handle_uncaught_exception


def _handle_thread_exception(args):
    write_crash_log(args.exc_type, args.exc_value, args.exc_traceback, origin="UNCAUGHT_THREAD_EXCEPTION")
    logger.error(
        "Uncaught exception in background thread:", exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
    )


threading.excepthook = _handle_thread_exception


def main(page: ft.Page) -> None:
    """Initialise la page Flet, les services et les événements UI."""
    trace("MAIN STEP 0: Entering main(page)")
    try:
        trace("MAIN STEP 1: Setting page title & theme mode...")
        page.title = "AIC — Audio Intelligence Companion"
        page.theme_mode = ft.ThemeMode.DARK

        trace("MAIN STEP 2: Registering fonts in page.fonts...")
        page.fonts = {
            "Cinzel Decorative Bold": "fonts/CinzelDecorative-Bold.ttf",
            "Cinzel Decorative Regular": "fonts/CinzelDecorative-Regular.ttf",
        }

        trace("MAIN STEP 3: Resolving window icon...")
        icon_path = get_asset_path("icon.ico") or get_asset_path("icon.png")
        if icon_path and icon_path.exists():
            try:
                page.window.icon = str(icon_path)
            except Exception as e:
                logger.warning(f"Impossible de définir l'icône de fenêtre : {e}")

        trace("MAIN STEP 4: Updating page themes and dimensions...")
        page.update()
        page.theme = get_light_theme()
        page.dark_theme = get_dark_theme()
        page.window.width = app_state.session.window_width
        page.window.height = app_state.session.window_height
        page.window.min_width = 850
        page.window.min_height = 600
        page.padding = 0

        trace("MAIN STEP 5: Instantiating AIEngineService...")
        ai_service = AIEngineService()
        trace("MAIN STEP 6: Instantiating DatabaseService...")
        db_service = DatabaseService()
        trace("MAIN STEP 7: Instantiating Controllers...")
        library_controller = LibraryController()
        rec_controller = RecommendationController()

        trace("MAIN STEP 8: Appending FilePicker service...")
        file_picker = ft.FilePicker()
        page.services.append(file_picker)

        def _show_toast(message: str, is_error: bool = False) -> None:
            """Affiche une notification toast sur le thread UI avec contraste WCAG optimisé."""
            snack = ft.SnackBar(
                content=ft.Text(
                    message,
                    color=ObsidianColors.TEXT_WHITE if is_error else ObsidianColors.BG_DARK,
                ),
                bgcolor=ObsidianColors.ERROR_BG if is_error else ObsidianColors.PRIMARY,
                duration=4000,
            )
            page.overlay.append(snack)
            snack.open = True
            try:
                page.update()
            except Exception:
                pass

        async def handle_pick_files() -> None:
            layout.library_view.set_loading(True)
            files = await file_picker.pick_files(
                allow_multiple=True,
                dialog_title="Sélectionner des fichiers audio pour AIC",
            )
            if not files:
                layout.library_view.set_loading(False)
                return

            file_paths = [f.path for f in files if f.path]
            if not file_paths:
                layout.library_view.set_loading(False)
                return

            _show_toast(f"Importation de {len(file_paths)} fichier(s)…")

            def on_complete_files(valid_count: int, invalid_count: int) -> None:
                async def _finish() -> None:
                    layout.library_view.set_loading(False)
                    _show_toast(f"{valid_count} morceau(x) ajouté(s) ({invalid_count} ignoré(s))")
                    app_state.notify()

                page.run_task(_finish)

            library_controller.import_files_async(file_paths, on_complete=on_complete_files)

        async def handle_pick_folder() -> None:
            layout.library_view.set_loading(True)
            folder_path = await file_picker.get_directory_path(
                dialog_title="Sélectionner un dossier musical pour AIC",
            )
            if not folder_path:
                layout.library_view.set_loading(False)
                return

            _show_toast(f"Balayage du dossier : {folder_path}…")

            def on_complete_folder(valid_count: int, invalid_count: int) -> None:
                async def _finish() -> None:
                    layout.library_view.set_loading(False)
                    _show_toast(f"{valid_count} morceau(x) indexé(s) depuis le dossier ({invalid_count} ignoré(s))")
                    app_state.notify()

                page.run_task(_finish)

            library_controller.import_folder_async(folder_path, on_complete=on_complete_folder)

        def handle_like_track(file_path: str) -> None:
            library_controller.toggle_like(file_path)

        def handle_delete_track(file_path: str) -> None:
            library_controller.remove_track(file_path)

        def handle_search(query: str) -> None:
            library_controller.set_search_query(query)

        def handle_reset() -> None:
            library_controller.reset_library()
            _show_toast("Bibliothèque réinitialisée.")

        def handle_theme_toggle(_e) -> None:
            page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
            page.update()

        def handle_start_recommendation() -> None:
            def on_success(playlist_paths: list) -> None:
                async def _open_modal() -> None:
                    dialog = ResultDialog(
                        count=len(playlist_paths),
                        file_path=app_state.session.last_generated_playlist_path,
                        on_launch_vlc=_launch_vlc,
                        on_close=lambda: page.pop_dialog(),
                    )
                    page.show_dialog(dialog)

                page.run_task(_open_modal)

            def on_error(err: str) -> None:
                async def _show_err() -> None:
                    _show_toast(f"Erreur : {err}", is_error=True)

                page.run_task(_show_err)

            rec_controller.run_recommendation_async(on_success=on_success, on_error=on_error)

        def _launch_vlc() -> None:
            success, msg = rec_controller.launch_vlc()
            _show_toast(msg, is_error=not success)

        trace("MAIN STEP 9: Instantiating MainLayout...")
        layout = MainLayout(
            on_pick_files=handle_pick_files,
            on_pick_folder=handle_pick_folder,
            on_like_track=handle_like_track,
            on_delete_track=handle_delete_track,
            on_search=handle_search,
            on_start_recommendation=handle_start_recommendation,
            on_reset=handle_reset,
            on_theme_toggle=handle_theme_toggle,
        )

        def on_state_change() -> None:
            try:
                layout.update_all()
                page.update()
            except Exception:
                pass

        trace("MAIN STEP 10: Subscribing to app_state...")
        app_state.subscribe(on_state_change)

        # ── Intégration du Splash Screen & Main Layout ────────────────────────
        def finish_splash() -> None:
            try:
                if splash_screen in root_stack.controls:
                    root_stack.controls.remove(splash_screen)
                    root_stack.update()
            except Exception:
                pass

        trace("MAIN STEP 11: Instantiating SplashScreen...")
        splash_screen = SplashScreen(page=page, on_complete=finish_splash)

        trace("MAIN STEP 12: Creating root_stack...")
        root_stack = ft.Stack(
            [
                layout,
                splash_screen,
            ],
            expand=True,
        )

        trace("MAIN STEP 13: Adding root_stack to page...")
        page.add(root_stack)

        trace("MAIN STEP 14: Scheduling splash animation task...")

        async def run_splash_task() -> None:
            try:
                trace("SPLASH TASK: Starting animation...")
                await splash_screen.start_animation_async()
                trace("SPLASH TASK: Animation complete OK")
            except Exception as splash_err:
                trace(f"SPLASH TASK ERROR: {splash_err}")
                write_crash_log(type(splash_err), splash_err, splash_err.__traceback__, origin="SPLASH_ANIMATION_ERROR")
                logger.error(f"Erreur animation Splash Screen : {splash_err}", exc_info=True)

        page.run_task(run_splash_task)

        trace("MAIN STEP 15: Starting background preload thread...")

        def preload_background() -> None:
            try:
                trace("PRELOAD THREAD: Preloading AI & Database resources...")
                ai_service.preload_resources()
                db_service.initialize_db()
                app_state.notify()
                trace("PRELOAD THREAD: Preload complete OK")
            except Exception as e:
                trace(f"PRELOAD THREAD ERROR: {e}")
                write_crash_log(type(e), e, e.__traceback__, origin="PRELOAD_BACKGROUND_ERROR")
                logger.error(f"Erreur lors du préchargement en arrière-plan : {e}", exc_info=True)

        threading.Thread(target=preload_background, daemon=True).start()
        trace("MAIN STEP 16: main(page) initialization loop completed successfully OK")

    except Exception as fatal_err:
        log_file_path = write_crash_log(
            type(fatal_err), fatal_err, fatal_err.__traceback__, origin="FATAL_STARTUP_ERROR"
        )
        logger.critical("Erreur fatale au démarrage d'AIC:", exc_info=True)
        try:
            page.clean()
            page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINED, color=ObsidianColors.ERROR, size=48),
                            ft.Text(
                                "Erreur lors du démarrage d'AIC",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ObsidianColors.TEXT_PRIMARY,
                            ),
                            ft.Text(
                                f"Détails de l'erreur : {fatal_err}",
                                size=13,
                                color=ObsidianColors.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                f"Le journal détaillé a été enregistré dans :\n{log_file_path}",
                                size=12,
                                color=ObsidianColors.TEXT_MUTED,
                                font_family="monospace",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=30,
                    expand=True,
                )
            )
        except Exception:
            pass


if __name__ == "__main__":
    try:
        ft.run(main)
    except Exception as main_run_err:
        write_crash_log(type(main_run_err), main_run_err, main_run_err.__traceback__, origin="FT_RUN_MAIN_ERROR")
        sys.exit(1)
