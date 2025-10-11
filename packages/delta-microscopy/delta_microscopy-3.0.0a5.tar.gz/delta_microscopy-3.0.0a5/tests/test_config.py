import tempfile
from pathlib import Path

import pytest

import delta


@pytest.mark.parametrize("presets", ["2D", "mothermachine"])
def test_read_write_tomlconfig(presets):
    config = delta.config.Config.default(presets)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "config.toml"
        with pytest.raises(FileNotFoundError):
            delta.config.Config.read(path)
        config.write(path)
        cfg = delta.config.Config.read(path)
        assert config == cfg


@pytest.mark.xfail
def test_print_config():
    config = delta.config.Config.default("2D")
    lines = str(config).splitlines()
    assert lines[0] == "DeLTA config"
    assert all(line.startswith(" ├─ ") for line in lines[1:-1])
    assert all(": " in line for line in lines[1:-1])
    assert lines[-1] == " └─ All other parameters are None."
