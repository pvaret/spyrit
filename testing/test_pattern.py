import hypothesis
import hypothesis.strategies

from spyrit.settings.pattern import Pattern, PatternScope, PatternType
from spyrit.ui.format import FormatUpdate


def _all_pattern_matches(pattern: Pattern, text: str) -> list[str]:
    matches = pattern.matches(text)
    return [text[m[0] : m[1]] for m in matches]


def _text_line() -> hypothesis.strategies.SearchStrategy:
    return hypothesis.strategies.text(min_size=1).filter(
        lambda s: "\n" not in s
    )


class TestFragmentMatching:
    @hypothesis.given(text=_text_line())
    def test_anything(self, text: str) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        assert _all_pattern_matches(pattern, text)[0] == text

    @hypothesis.given(text=_text_line())
    def test_any_of(self, text: str) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        fragment = pattern.fragments.appendOne()
        fragment.type.set(PatternType.ANY_OF)
        fragment.pattern_text.set(text)

        assert _all_pattern_matches(pattern, text)[0] == text

    @hypothesis.given(text=_text_line())
    def test_any_not_in(self, text: str) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        fragment_pattern = "".join(
            c
            for c in map(chr, range(32, 256))
            if c.isprintable() and c.lower() not in text.lower()
        )

        fragment = pattern.fragments.appendOne()
        fragment.type.set(PatternType.ANY_NOT_IN)
        fragment.pattern_text.set(fragment_pattern)

        assert _all_pattern_matches(pattern, text)[0] == text


class TestCompoundPatternEntireLine:
    def test_one_pattern(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.ANY_OF)
        f1.pattern_text.set("abcde")

        assert _all_pattern_matches(pattern, "aaaaaaa") == [
            "aaaaaaa",  # pattern
            "aaaaaaa",  # fragment
        ]

    def test_two_patterns(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.ANY_OF)
        f1.pattern_text.set("abcde")

        f2 = pattern.fragments.appendOne()
        f2.type.set(PatternType.ANY_OF)
        f2.pattern_text.set("fghij")

        assert _all_pattern_matches(pattern, "aaaaaaajjjj") == [
            "aaaaaaajjjj",
            "aaaaaaa",
            "jjjj",
        ]

    def test_three_patterns(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.ANY_OF)
        f1.pattern_text.set("abcde")

        f2 = pattern.fragments.appendOne()
        f2.type.set(PatternType.ANYTHING)

        f3 = pattern.fragments.appendOne()
        f3.type.set(PatternType.ANY_OF)
        f3.pattern_text.set("fghij")

        assert _all_pattern_matches(pattern, "aaaaaaazzzjjjj") == [
            "aaaaaaazzzjjjj",
            "aaaaaaa",
            "zzz",
            "jjjj",
        ]

    def test_whole_line_is_matched(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.ANY_OF)
        f1.pattern_text.set("abcde")

        assert _all_pattern_matches(pattern, "aaaaaaaz") == []
        assert _all_pattern_matches(pattern, "zaaaaaaa") == []

    def test_backtracking_occurs_as_needed(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.ANYTHING)

        f2 = pattern.fragments.appendOne()
        f2.type.set(PatternType.REGEX)
        f2.pattern_text.set(r"a{4}")

        assert _all_pattern_matches(pattern, "a" * 9) == [
            "a" * 9,
            "aaaaa",
            "aaaa",
        ]

    def test_simple_wildcards(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("xxx")

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        assert _all_pattern_matches(pattern, "1234xxx1234") == [
            "1234xxx1234",
            "1234",
            "xxx",
            "1234",
        ]

    def test_complex_wildcards(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)
        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)
        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("xxx")

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)
        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)
        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        f2 = pattern.fragments.appendOne()
        f2.type.set(PatternType.EXACT_MATCH)
        f2.pattern_text.set("xxx")

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)
        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)
        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        assert _all_pattern_matches(pattern, "1234xxx1234xxx1234") == [
            "1234xxx1234xxx1234",
            "1234",
            "xxx",
            "1234",
            "xxx",
            "1234",
        ]

    def test_with_empty_anything(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.ANY_OF)
        f1.pattern_text.set("abcde")

        f2 = pattern.fragments.appendOne()
        f2.type.set(PatternType.ANYTHING)

        f3 = pattern.fragments.appendOne()
        f3.type.set(PatternType.ANY_OF)
        f3.pattern_text.set("zyxwv")

        assert _all_pattern_matches(pattern, "aaaaazzzzz") == [
            "aaaaazzzzz",
            "aaaaa",
            "zzzzz",
        ]

    def test_format_line(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ENTIRE_LINE)
        pattern.format.set(match_format := FormatUpdate())

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("xxx")

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        matches = pattern.matches("1234xxx1234")
        assert matches[0][2] is match_format


class TestCompoundPatternAnyWhereInLine:
    def test_pattern_anything(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ANYWHERE_IN_LINE)

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        assert _all_pattern_matches(pattern, "12345") == [
            "1",  # pattern
            "1",  # fragment
            "2",  # pattern
            "2",  # fragment
            "3",  # pattern
            "3",  # fragment
            "4",  # pattern
            "4",  # fragment
            "5",  # pattern
            "5",  # fragment
        ]

    def test_pattern_anywhere(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ANYWHERE_IN_LINE)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("test")

        assert _all_pattern_matches(pattern, "") == []
        assert _all_pattern_matches(pattern, "xxxxx") == []
        assert _all_pattern_matches(pattern, "test") == [
            "test",  # pattern
            "test",  # fragment
        ]
        assert _all_pattern_matches(pattern, "xxxtest") == [
            "test",  # pattern
            "test",  # fragment
        ]
        assert _all_pattern_matches(pattern, "testxxx") == [
            "test",  # pattern
            "test",  # fragment
        ]
        assert _all_pattern_matches(pattern, "testtest") == [
            "test",  # pattern
            "test",  # fragment
            "test",  # pattern
            "test",  # fragment
        ]
        assert _all_pattern_matches(pattern, "xtestxtestx") == [
            "test",  # pattern
            "test",  # fragment
            "test",  # pattern
            "test",  # fragment
        ]

    def test_with_anything(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ANYWHERE_IN_LINE)

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("test")

        pattern.fragments.appendOne().type.set(PatternType.ANYTHING)

        assert _all_pattern_matches(pattern, "") == []
        assert _all_pattern_matches(pattern, "xxxxxx") == []
        assert _all_pattern_matches(pattern, "test") == [
            "test",  # pattern
            "test",  # fragment
        ]
        assert _all_pattern_matches(pattern, "xxxtest") == [
            "xxxtest",
            "xxx",
            "test",
        ]
        assert _all_pattern_matches(pattern, "xxxtestxxxxtest") == [
            "xxxtest",
            "xxx",
            "test",
            "xxxxtest",
            "xxxx",
            "test",
        ]
        assert _all_pattern_matches(pattern, "xxtestxx") == [
            "xxtest",
            "xx",
            "test",
        ]
        assert _all_pattern_matches(pattern, "xxtestxxxtestx") == [
            "xxtest",
            "xx",
            "test",
            "xxxtest",
            "xxx",
            "test",
        ]

    def test_with_any_of(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ANYWHERE_IN_LINE)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.ANY_OF)
        f1.pattern_text.set("x")

        f2 = pattern.fragments.appendOne()
        f2.type.set(PatternType.EXACT_MATCH)
        f2.pattern_text.set("test")

        f3 = pattern.fragments.appendOne()
        f3.type.set(PatternType.ANY_OF)
        f3.pattern_text.set("x")

        assert _all_pattern_matches(pattern, "") == []
        assert _all_pattern_matches(pattern, "test") == []
        assert _all_pattern_matches(pattern, "xxxtestxxx") == [
            "xxxtestxxx",
            "xxx",
            "test",
            "xxx",
        ]
        assert _all_pattern_matches(pattern, "xxxtestxxxxtestxxx") == [
            "xxxtestxxxx",
            "xxx",
            "test",
            "xxxx",
        ]
        assert _all_pattern_matches(pattern, "xxxtestxx xxtestxxx") == [
            "xxxtestxx",
            "xxx",
            "test",
            "xx",
            "xxtestxxx",
            "xx",
            "test",
            "xxx",
        ]

    def test_match_at_start_or_end(self) -> None:
        pattern = Pattern()
        pattern.scope.set(PatternScope.ANYWHERE_IN_LINE)

        f1 = pattern.fragments.appendOne()
        f1.type.set(PatternType.EXACT_MATCH)
        f1.pattern_text.set("x")

        assert _all_pattern_matches(pattern, "x     ") == [
            "x",  # pattern
            "x",  # fragment
        ]
        assert _all_pattern_matches(pattern, "     x") == [
            "x",  # pattern
            "x",  # fragment
        ]
