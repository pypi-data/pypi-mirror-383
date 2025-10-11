import delta


def test_version():
    version = delta.__version__
    assert isinstance(version, str)
    assert "." in version
