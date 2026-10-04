from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OLV_", env_file=".env", extra="ignore")

    bind_host: str = "127.0.0.1"
    bind_port: int = 8765

    local_llm_base_url: str = "http://127.0.0.1:8085/v1"
    local_llm_api_key: str = "dummy"
    local_llm_model: str = "qwen3.5-4b"
    local_llm_timeout_s: float = 4.0

    opencode_base_url: str = "http://127.0.0.1:4096"
    opencode_timeout_s: float = 5.0

    tts_backend: str = "stdout"
    piper_voice: str | None = None
    tts_command: str | None = None

    stt_backend: str = "whisper_cpp"
    whisper_cli: str = "whisper-cli"
    whisper_model: str = "~/.local/share/whisper-cpp/ggml-large-v3-turbo-q5_0.bin"

    coalesce_ms: int = 450
    max_recent_events: int = 12


settings = Settings()
