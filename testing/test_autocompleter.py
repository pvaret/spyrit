from typing import Iterator

from pytest import MonkeyPatch, FixtureDef, fixture
from pytest_mock import MockerFixture

from PySide6.QtGui import QTextCursor, QTextDocument

from spyrit.network.fragments import (
    FlowControlCode,
    FlowControlFragment,
    TextFragment,
)
from spyrit.resources.file import ResourceFile
from spyrit.resources.resources import Misc
from spyrit.ui.autocompleter import (
    Autocompleter,
    Case,
    CompletionModel,
    StaticWordList,
    Tokenizer,
)
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


class TestTokenizer:
    def test_tokenize(self) -> None:
        output: list[str] = []
        t = Tokenizer()
        t.tokenFound.connect(output.append)
        CRLF = FlowControlFragment(FlowControlCode.LF)

        t.processFragments([TextFragment("test"), CRLF])
        assert output == ["test"]

        output.clear()
        t.processFragments([TextFragment("te"), TextFragment("st"), CRLF])
        assert output == ["test"]

        output.clear()
        t.processFragments([TextFragment("test test"), CRLF])
        assert output == ["test", "test"]

        output.clear()
        t.processFragments([TextFragment("testé"), CRLF])
        assert output == ["testé"]

        output.clear()
        t.processFragments([TextFragment("'test'"), CRLF])
        assert output == ["test"]

        output.clear()
        t.processFragments([TextFragment(" test 'test' "), CRLF])
        assert output == ["test", "test"]

        output.clear()
        t.processFragments([TextFragment("don't"), CRLF])
        assert output == ["don't"]

        output.clear()
        text = '''And then he said, "I've got a bad feeling about this!"'''
        t.processFragments([TextFragment(text), CRLF])
        assert output == [
            "And",
            "then",
            "he",
            "said",
            "I've",
            "got",
            "a",
            "bad",
            "feeling",
            "about",
            "this",
        ]

    def test_only_alnum_and_single_valid_inner_chars_tokenized(self) -> None:
        output: list[str] = []
        t = Tokenizer()
        t.tokenFound.connect(output.append)
        CRLF = FlowControlFragment(FlowControlCode.LF)

        t.processFragments([TextFragment(""), CRLF])
        assert output == []

        t.processFragments([TextFragment("!?"), CRLF])
        assert output == []

        output.clear()
        t.processFragments([TextFragment(" test test "), CRLF])
        assert output == ["test", "test"]

        output.clear()
        t.processFragments([TextFragment("$test!test?"), CRLF])
        assert output == ["test", "test"]

        output.clear()
        t.processFragments([TextFragment("test1/test2"), CRLF])
        assert output == ["test1", "test2"]

        output.clear()
        t.processFragments([TextFragment("test_test"), CRLF])
        assert output == ["test_test"]

        output.clear()
        t.processFragments([TextFragment("_test_test_"), CRLF])
        assert output == ["test_test"]

        output.clear()
        t.processFragments([TextFragment("'"), CRLF])
        assert output == []

        output.clear()
        t.processFragments([TextFragment("test'test test''test"), CRLF])
        assert output == ["test'test", "test", "test"]


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

    def test_extra_words_get_matched(self) -> None:
        model = CompletionModel(["Po-TAH-to", "Po-TAY-to"])
        assert model.findMatches("po-") == ["Po-TAH-to", "Po-TAY-to"]

        model.addExtraWord("Po-TAY-ter")
        assert model.findMatches("po-") == [
            "Po-TAH-to",
            "Po-TAY-ter",
            "Po-TAY-to",
        ]

        # Adding the same word should not result in more matches, regardless of case.

        model.addExtraWord("po-tay-ter")
        assert model.findMatches("po-") == [
            "Po-TAH-to",
            "Po-TAY-ter",
            "Po-TAY-to",
        ]

        # Adding a word already in the static list should not result in more
        # matches.

        model.addExtraWord("Po-TAH-to")
        assert model.findMatches("po-") == [
            "Po-TAH-to",
            "Po-TAY-ter",
            "Po-TAY-to",
        ]


class TestCompleter:
    def _select_completable_word(self, text: str, *, pos: int) -> str:
        doc = QTextDocument(text)
        cursor = QTextCursor(doc)
        cursor.setPosition(pos)

        Autocompleter.selectCompletableWord(cursor)

        return cursor.selectedText()

    def test_selection(self) -> None:
        assert self._select_completable_word("", pos=0) == ""
        assert self._select_completable_word("test", pos=0) == "test"
        assert self._select_completable_word("test ", pos=4) == "test"
        assert self._select_completable_word(" test ", pos=5) == "test"
        assert self._select_completable_word(" test", pos=5) == "test"
        assert self._select_completable_word("test1 test2", pos=2) == "test1"
        assert self._select_completable_word("test1 test2", pos=6) == "test2"
        assert self._select_completable_word("'test", pos=0) == ""
        assert self._select_completable_word("'test", pos=1) == "test"
        assert self._select_completable_word(" 'test", pos=1) == ""
        assert self._select_completable_word(" 'test", pos=2) == "test"
        assert self._select_completable_word("test'", pos=0) == "test'"
        assert self._select_completable_word("test'", pos=4) == "test'"
        assert self._select_completable_word("test'", pos=5) == "test'"
        assert self._select_completable_word("test' ", pos=0) == "test'"
        assert self._select_completable_word("test' ", pos=4) == "test'"
        assert self._select_completable_word("test' ", pos=5) == "test'"
        assert self._select_completable_word("test'test", pos=0) == "test'test"
        assert self._select_completable_word("test'test", pos=3) == "test'test"
        assert self._select_completable_word("test'test", pos=4) == "test'test"
        assert self._select_completable_word("test'test", pos=5) == "test'test"
        assert self._select_completable_word("test'test", pos=6) == "test'test"
        assert self._select_completable_word("test1''test2", pos=5) == "test1'"
        assert self._select_completable_word("test1''test2", pos=6) == "test1'"
        assert self._select_completable_word("test1''test2", pos=7) == "test2"
        assert self._select_completable_word("test1''test2", pos=8) == "test2"
        assert self._select_completable_word("test 'test", pos=8) == "test"
        assert (
            self._select_completable_word(
                '"Well then, this is awkward!"', pos=0
            )
            == ""
        )
        assert (
            self._select_completable_word(
                '"Well then, this is awkward!"', pos=1
            )
            == "Well"
        )
        assert (
            self._select_completable_word(
                '"Well then, this is awkward!"', pos=6
            )
            == "then"
        )
        assert (
            self._select_completable_word(
                '"Well then, this is awkward!"', pos=21
            )
            == "awkward"
        )
