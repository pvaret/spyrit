from PySide6.QtCore import QSize
from PySide6.QtGui import QFont

from spyrit.settings.serializers import Font, IntList, Size


def test_int_list_serializer() -> None:
    serializer = IntList()

    assert serializer.fromStr("") == []
    assert serializer.fromStr(" 1 ") == [1]
    assert serializer.fromStr("2  ,3,4") == [2, 3, 4]
    assert serializer.fromStr("1,,3") == [1, 3]
    assert serializer.fromStr("5,six,7") is None
    assert serializer.fromStr("5,6.0,7") is None

    assert serializer.toStr([]) == ""
    assert serializer.toStr([1]) == "1"
    assert serializer.toStr([2, 3, 4]) == "2, 3, 4"


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
