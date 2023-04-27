import pytest

from spyrit.platform import get_default_paths


def test_all_platforms(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPDATA", "")

    for platform in ("linux", "win32", "darwin"):
        paths = get_default_paths(platform)
        assert paths.getConfigFilePath()
        assert paths.getStateFilePath()
        assert paths.getPidFilePath()

        paths.setConfigFolderPath("/dummy")
        assert paths.getConfigFilePath().as_posix().startswith("/dummy/")
        assert paths.getStateFilePath().as_posix().startswith("/dummy/")
        assert paths.getPidFilePath().as_posix().startswith("/dummy/")

    with pytest.raises(NotImplementedError):
        get_default_paths("INVALID")
