"""Tests for OpenAI TTS configuration schema and service factory wiring."""

from types import SimpleNamespace

from api.services.configuration.registry import (
    OPENAI_TTS_LEGACY_VOICES,
    OPENAI_TTS_MODELS,
    OPENAI_TTS_VOICES,
    OpenAITTSService,
    ServiceProviders,
)
from api.services.pipecat.service_factory import create_tts_service


class TestOpenAITTSConfiguration:
    def test_json_schema_has_model_and_voice_examples(self):
        schema = OpenAITTSService.model_json_schema()
        assert schema["properties"]["model"]["examples"] == OPENAI_TTS_MODELS
        voice_field = schema["properties"]["voice"]
        assert voice_field["examples"] == OPENAI_TTS_VOICES
        assert voice_field["model_options"]["gpt-4o-mini-tts"] == OPENAI_TTS_VOICES
        assert voice_field["model_options"]["tts-1"] == OPENAI_TTS_LEGACY_VOICES

    def test_voice_persists_on_model(self):
        cfg = OpenAITTSService(api_key="test-key", voice="coral", model="gpt-4o-mini-tts")
        assert cfg.voice == "coral"


class TestOpenAITTSServiceFactory:
    def test_create_tts_service_uses_configured_voice(self, monkeypatch):
        monkeypatch.setattr("api.utils.url_security.DEPLOYMENT_MODE", "oss")
        for voice in ("coral", "onyx", "shimmer"):
            user_config = SimpleNamespace(
                tts=SimpleNamespace(
                    provider=ServiceProviders.OPENAI.value,
                    api_key="test-key",
                    model="gpt-4o-mini-tts",
                    voice=voice,
                    speed=1.0,
                    base_url="https://api.openai.com/v1",
                )
            )
            service = create_tts_service(user_config, audio_config=None)
            assert service._settings.voice == voice
