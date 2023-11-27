import hypothesis
import hypothesis.strategies
import pytest

from spyrit.settings.scrambled_text import ScrambledText


def _text_hypothesis() -> hypothesis.strategies.SearchStrategy[str]:
    return hypothesis.strategies.text().filter(lambda s: "\0" not in s)


def _salt_hypothesis() -> hypothesis.strategies.SearchStrategy[bytes]:
    size = ScrambledText.SALT_LENGTH
    return hypothesis.strategies.binary(min_size=size, max_size=size)


class TestScrambledText:
    @hypothesis.given(text=_text_hypothesis(), salt=_salt_hypothesis())
    def test_text_descrambles_to_initial_value(
        self, text: str, salt: bytes
    ) -> None:
        assert ScrambledText(text, salt).plaintext() == text

    @hypothesis.given(text=_text_hypothesis(), salt=_salt_hypothesis())
    def test_fromStr_restores_scrambled_text(
        self, text: str, salt: bytes
    ) -> None:
        cipher = ScrambledText(text, salt).toStr()
        scrambled = ScrambledText.fromStr(cipher)
        assert scrambled is not None and scrambled.plaintext() == text

    @hypothesis.given(text=_text_hypothesis(), salt=_salt_hypothesis())
    def test_scrambled_text_is_scrambled(self, text: str, salt: bytes) -> None:
        assert ScrambledText(text, salt).toStr() != text

    @hypothesis.given(text=_text_hypothesis())
    def test_distinct_instances_with_same_plaintext_have_different_cipher(
        self, text: str
    ) -> None:
        s1 = ScrambledText(text)
        s2 = ScrambledText(text)

        assert s1.toStr() != s2.toStr()

    @hypothesis.given(text=_text_hypothesis(), salt=_salt_hypothesis())
    def test_same_salt_same_cipher(self, text: str, salt: bytes) -> None:
        s1 = ScrambledText(text, salt)
        s2 = ScrambledText(text, salt)

        assert s1.toStr() == s2.toStr()

    @hypothesis.given(
        text=_text_hypothesis(),
        salts=hypothesis.strategies.tuples(
            _salt_hypothesis(), _salt_hypothesis()
        ).filter(lambda salts: salts[0] != salts[1]),
    )
    def test_different_salt_different_cipher(
        self, text: str, salts: tuple[bytes, bytes]
    ) -> None:
        s1 = ScrambledText(text, salts[0])
        s2 = ScrambledText(text, salts[1])

        assert s1.toStr() != s2.toStr()

    @hypothesis.given(value=hypothesis.strategies.text())
    def test_fromStr_doesnt_crash_on_bogus_input(self, value: str) -> None:
        s = ScrambledText.fromStr(value)
        assert isinstance(s, (ScrambledText, type(None)))

    @hypothesis.given(
        salt=hypothesis.strategies.binary(min_size=1).filter(
            lambda b: len(b) != ScrambledText.SALT_LENGTH
        )
    )
    def test_invalid_salt_length_raises_assertion(self, salt: bytes) -> None:
        with pytest.raises(AssertionError):
            ScrambledText("", salt)

    @hypothesis.given(salt=_salt_hypothesis())
    def test_very_long_text_is_scrambled(self, salt: bytes) -> None:
        text = "0" * 1024
        s = ScrambledText(text, salt)
        assert s.plaintext() == text
        assert "0" * 128 not in s.toStr()