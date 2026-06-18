"""Environmental noise cancellation (ENC) for inbound audio using RNNoise."""

from __future__ import annotations

import sys
from functools import lru_cache

from loguru import logger

from api.constants import APP_ROOT_DIR

_NATIVE_RNNOISE_LIB = APP_ROOT_DIR / "native" / "rnnoise" / "librnnoise.so"


@lru_cache(maxsize=1)
def _preload_native_rnnoise() -> None:
    """Preload bundled RNNoise on Linux deployments that ship ``native/rnnoise``."""
    if sys.platform != "linux" or not _NATIVE_RNNOISE_LIB.is_file():
        return
    try:
        import ctypes

        ctypes.CDLL(str(_NATIVE_RNNOISE_LIB))
    except OSError as exc:
        logger.debug(f"Could not preload bundled RNNoise library: {exc}")


def create_noise_cancellation_filter():
    """Return an RNNoise input filter, or ``None`` if unavailable."""
    _preload_native_rnnoise()
    try:
        from pipecat.audio.filters.rnnoise_filter import RNNoiseFilter

        return RNNoiseFilter()
    except Exception as exc:
        logger.warning(f"RNNoise noise cancellation unavailable: {exc}")
        return None
