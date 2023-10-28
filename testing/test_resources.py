from PySide6.QtCore import QFile

from spyrit.resources.loader import load


class TestResources:
    def test_resources_load(self) -> None:
        assert load()

    def test_all_resources_present(self) -> None:
        load()
        for filename in (
            ":/fonts/NotoSansMono.ttf",
            ":/logos/spyrit-logo.svg",
            ":/icons/input-field.svg",
            ":/icons/search.svg",
        ):
            assert QFile(filename).exists()
