import json
import os
import tempfile
import pytest

from pybg.modules.settings_manager import SettingsManager

pytestmark = pytest.mark.unit


class DummyShell:
    def __init__(self):
        self.settings = {}
        self.saved = False

    def save_settings(self):
        self.saved = True


@pytest.fixture
def schema():
    return {
        "match_length": {
            "type": "int",
            "default": 5,
            "description": "Length of the match",
        },
        "sound": {"type": "bool", "default": True, "description": "Enable sound"},
        "variant": {
            "type": "choice",
            "choices": ["standard", "nackgammon"],
            "default": "standard",
            "description": "Game variant",
        },
    }


@pytest.fixture
def schema_file(schema):
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        json.dump(schema, f)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def settings_file():
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        json.dump({"match_length": 3, "sound": False, "variant": "nackgammon"}, f)
        f.flush()
        yield f.name
    os.unlink(f.name)


def test_initializes_with_existing_settings(schema_file, settings_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file, settings_path=settings_file)
    assert shell.settings["match_length"] == 3
    assert shell.settings["variant"] == "nackgammon"


def test_initializes_with_defaults_and_saves(schema_file):
    shell = DummyShell()
    with tempfile.TemporaryDirectory() as tmpdir:
        settings_path = os.path.join(tmpdir, "settings.json")

        sm = SettingsManager(
            shell, schema_path=schema_file, settings_path=settings_path
        )
        assert shell.settings["match_length"] == 5
        assert shell.settings["variant"] == "standard"
        assert os.path.exists(settings_path)


def test_cmd_set_invalid_args(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    assert sm.cmd_set(["onlyone"]) == "Usage: set <option> <value>"


def test_cmd_set_unknown_key(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    assert sm.cmd_set(["unknown", "value"]) == "Unknown setting: unknown"


def test_cmd_set_valid_int(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    result = sm.cmd_set(["match_length", "7"])
    assert shell.settings["match_length"] == 7
    assert result == "match_length set to 7"
    assert shell.saved


def test_cmd_set_invalid_int(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    result = sm.cmd_set(["match_length", "notanint"])
    assert "Invalid value for match_length" in result


def test_cmd_set_bool_true(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    result = sm.cmd_set(["sound", "on"])
    assert shell.settings["sound"] is True


def test_cmd_set_bool_false(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    result = sm.cmd_set(["sound", "off"])
    assert shell.settings["sound"] is False


def test_cmd_set_invalid_choice(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    result = sm.cmd_set(["variant", "hypergammon"])
    assert "Invalid value for variant" in result


def test_cmd_settings_output_format(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    output = sm.cmd_settings([])
    assert "CURRENT SETTINGS" in output
    assert "SETTING" in output
    assert "match_length" in output


def test_cmd_settings_help_output(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    help_output = sm.cmd_settings_help([])
    assert "SETTINGS HELP" in help_output
    assert "match_length" in help_output


def test_register_returns_expected(schema_file):
    shell = DummyShell()
    sm = SettingsManager(shell, schema_path=schema_file)
    commands, _, help_texts = sm.register()
    assert "set" in commands
    assert "settings" in commands
    assert "settings_help" in commands
    assert "set" in help_texts
