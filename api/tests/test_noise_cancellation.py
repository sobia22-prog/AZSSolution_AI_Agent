from unittest.mock import MagicMock, patch

from api.services.pipecat.run_pipeline import (
    DEFAULT_USER_SPEECH_TIMEOUT,
    DEFAULT_VAD_PARAMS,
    _noise_cancellation_enabled,
)
from api.services.pipecat.transport_params import (
    REALTIME_BOT_VAD_STOP_SECS,
    build_transport_param_overrides,
)


def test_noise_cancellation_enabled_defaults_true():
    assert _noise_cancellation_enabled(None) is True
    assert _noise_cancellation_enabled({}) is True


def test_noise_cancellation_enabled_respects_config():
    assert _noise_cancellation_enabled({"noise_cancellation_enabled": False}) is False
    assert _noise_cancellation_enabled({"noise_cancellation_enabled": True}) is True


def test_build_transport_param_overrides_realtime_only():
    overrides = build_transport_param_overrides(is_realtime=True, noise_cancellation_enabled=False)
    assert overrides == {"bot_vad_stop_secs": REALTIME_BOT_VAD_STOP_SECS}


def test_build_transport_param_overrides_adds_filter_when_available():
    mock_filter = MagicMock()
    with patch(
        "api.services.pipecat.transport_params.create_noise_cancellation_filter",
        return_value=mock_filter,
    ):
        overrides = build_transport_param_overrides(noise_cancellation_enabled=True)
    assert overrides["audio_in_filter"] is mock_filter


def test_build_transport_param_overrides_skips_filter_when_disabled():
    with patch(
        "api.services.pipecat.transport_params.create_noise_cancellation_filter",
    ) as create_filter:
        overrides = build_transport_param_overrides(noise_cancellation_enabled=False)
    create_filter.assert_not_called()
    assert "audio_in_filter" not in overrides


def test_latency_defaults_are_tuned():
    assert DEFAULT_USER_SPEECH_TIMEOUT == 0.25
    assert DEFAULT_VAD_PARAMS.min_volume == 0.60
    assert DEFAULT_VAD_PARAMS.confidence == 0.65
    assert DEFAULT_VAD_PARAMS.stop_secs == 0.10

