from typing import Iterator

from pytest import MonkeyPatch, FixtureDef, fixture
from pytest_mock import MockerFixture

from spyrit.resources.file import ResourceFile
from spyrit.resources.resources import Misc
from spyrit.ui.autocompleter import Case, CompletionModel, StaticWordList
from spyrit.ui.autocompleter import _apply_case, _compute_case  # type: ignore

StaticWordListFixture = FixtureDef[None]


@fixture
def reset_static_word_list() -> Iterator[None]:
    """
    This fixture resets the static word list's contents after each test.
    """
    yield
    StaticWordList.reset()


class TestCase:
    def test_compute_case(self) -> None:
        assert _compute_case("") == Case.UNSPECIFIED
        assert _compute_case("a") == Case.UNSPECIFIED
        assert _compute_case("A") == Case.CAPITALIZED
        assert _compute_case("-") == Case.UNSPECIFIED
        assert _compute_case("WHEE") == Case.ALL_CAPS
        assert _compute_case("Whee") == Case.CAPITALIZED
        assert _compute_case("whee") == Case.UNSPECIFIED
        assert _compute_case("whEe") == Case.UNSPECIFIED
        assert _compute_case("Élan") == Case.CAPITALIZED

    def test_apply_case(self) -> None:
        assert _apply_case(Case.UNSPECIFIED, "example") == "example"
        assert _apply_case(Case.UNSPECIFIED, "exaMPLE") == "exaMPLE"
        assert _apply_case(Case.UNSPECIFIED, "ExaMPLE") == "ExaMPLE"

        assert _apply_case(Case.CAPITALIZED, "example") == "Example"
        assert _apply_case(Case.CAPITALIZED, "ExamPLE") == "ExamPLE"

        assert _apply_case(Case.ALL_CAPS, "example") == "EXAMPLE"
        assert _apply_case(Case.ALL_CAPS, "ExamPLE") == "EXAMPLE"
        assert _apply_case(Case.ALL_CAPS, "é") == "É"


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
        assert "PO-TAY-TO" in words
        assert "po-tay-to" in words
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

    def test_prefix_case_becomes_match_case(self) -> None:
        model = CompletionModel(["fiancé", "lower", "Po-TAH-to", "Po-TAY-to"])
        assert model.findMatches("low") == ["lower"]
        assert model.findMatches("Low") == ["Lower"]
        assert model.findMatches("LOW") == ["LOWER"]
        assert model.findMatches("po-ta") == ["Po-TAH-to", "Po-TAY-to"]
        assert model.findMatches("Po-ta") == ["Po-TAH-to", "Po-TAY-to"]
        assert model.findMatches("PO-TA") == ["PO-TAH-TO", "PO-TAY-TO"]
        assert model.findMatches("FIA") == ["FIANCÉ"]
