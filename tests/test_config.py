import pytest

from src.config import Config, DEFAULT_MODEL

CONFIG_YAML = """
model: "claude-custom-model"
selection:
  min_score: 40
nested:
  deeper:
    value: 42
"""

CONFIG_YAML_NO_MODEL = """
selection:
  min_score: 40
"""


def write_config(tmp_path, content: str) -> Config:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(content)
    return Config(str(config_path))


def test_get_dot_notation_present_key(tmp_path):
    config = write_config(tmp_path, CONFIG_YAML)
    assert config.get("nested.deeper.value") == 42
    assert config.get("selection.min_score") == 40


def test_get_dot_notation_missing_key_returns_default(tmp_path):
    config = write_config(tmp_path, CONFIG_YAML)
    assert config.get("nested.deeper.missing", "fallback") == "fallback"
    assert config.get("totally.missing") is None


def test_get_model_uses_configured_value(tmp_path):
    config = write_config(tmp_path, CONFIG_YAML)
    assert config.get_model() == "claude-custom-model"


def test_get_model_default_when_absent(tmp_path):
    config = write_config(tmp_path, CONFIG_YAML_NO_MODEL)
    assert config.get_model() == DEFAULT_MODEL


def test_missing_config_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        Config(str(tmp_path / "does_not_exist.yaml"))
