from typing import Iterator

from pytest import MonkeyPatch, FixtureDef, fixture
from pytest_mock import MockerFixture

from spyrit.resources.file import ResourceFile
from spyrit.resources.resources import Misc
from spyrit.ui.autocompleter import CompletionModel, StaticWordList


StaticWordListFixture = FixtureDef[None]


@fixture
def reset_static_word_list() -> Iterator[None]:
    """
    This fixture resets the static word list's contents after each test.
    """
    yield
    StaticWordList.reset()


class TestStaticWordList:
    def test_word_list_len(
        self, reset_static_word_list: StaticWordListFixture
    ) -> None:
        words = StaticWordList(Misc.TEST_TXT_GZ)
        assert len(words) == 2

    def test_word_list_getitem(
        self, reset_static_word_list: StaticWordListFixture
    ) -> None:
        words = StaticWordList(Misc.TEST_TXT_GZ)
        assert words[0] == "Po-TAH-to"
        assert words[1] == "Po-TAY-to"

    def test_word_list_contains(
        self, reset_static_word_list: StaticWordListFixture
    ) -> None:
        words = StaticWordList(Misc.TEST_TXT_GZ)
        assert "Po-TAH-to" in words
        assert "Po-TAY-to" in words
        assert "turnip" not in words

    def test_costly_functions_only_called_once(
        self,
        reset_static_word_list: StaticWordListFixture,
        mocker: MockerFixture,
        monkeypatch: MonkeyPatch,
    ) -> None:
        data = ResourceFile(Misc.TEST_TXT_GZ).readall()

        readall = mocker.Mock(return_value=data)
        monkeypatch.setattr(ResourceFile, "readall", readall)

        readall.assert_not_called()

        StaticWordList(Misc.TEST_TXT_GZ)
        readall.assert_called_once()
        readall.reset_mock()

        StaticWordList(Misc.TEST_TXT_GZ)
        readall.assert_not_called()


class TestCompletionModel:
    def test_found_single_match_case_insensitive(self) -> None:
        model = CompletionModel(["Po-TAH-to", "Po-TAY-to"])
        assert model.findMatches("po-tay-to") == ["Po-TAY-to"]

    def test_found_all_matches(self) -> None:
        model = CompletionModel(["Po-TAH-to", "Po-TAY-to"])
        assert model.findMatches("po-") == ["Po-TAH-to", "Po-TAY-to"]

    def test_no_match_found(self) -> None:
        model = CompletionModel(["Po-TAH-to", "Po-TAY-to"])
        assert model.findMatches("aaaaa") == []
        assert model.findMatches("zzzzz") == []

    def test_return_no_matches_when_prefix_too_short(self) -> None:
        model = CompletionModel(["Po-TAH-to", "Po-TAY-to"])
        assert model.findMatches("") == []
        assert model.findMatches("po") == []
        assert model.findMatches("po-") != []
