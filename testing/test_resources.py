from PySide6.QtCore import QFile

from spyrit.resources.loader import load
from spyrit.resources.resources import Resources


class TestResources:
    def test_resources_load(self) -> None:
        assert load()

    def test_all_resources_present(self) -> None:
        for resource_type in Resources:
            for filename in resource_type:
                assert QFile(filename).exists()
