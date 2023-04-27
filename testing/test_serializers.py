from PySide6.QtCore import QSize
from PySide6.QtGui import QFont

from spyrit.settings.serializers import Font, Size


def test_font_serializer() -> None:
    font = Font().fromStr("arial,10")
    assert font is not None
    assert font.family() == "arial"
    assert font.pointSize() == 10

    font = QFont("sans serif", 12)
    assert Font().toStr(font).startswith("sans serif,12,")


def test_size_serializer() -> None:
    size = Size().fromStr("12, 34")
    assert size is not None
    assert size.width() == 12
    assert size.height() == 34

    assert Size().toStr(QSize(56, 78)) == "56, 78"
