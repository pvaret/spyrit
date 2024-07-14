from spyrit.network.pattern import (
    find_matches,
    match_fragment_to_text,
)
from spyrit.settings.pattern import Pattern, PatternScope, PatternType
from spyrit.ui.format import FormatUpdate


def _all_fragment_matches(
    pattern: Pattern.Fragment,
    text: str,
    pos: int = 0,
) -> list[str]:
    matches = match_fragment_to_text(pattern, text, pos)
    return [text[m[0] : m[1]] for m in matches]


def _all_pattern_matches(pattern: Pattern, text: str) -> list[str]:
    matches = find_matches(pattern, text)
    return [text[m[0] : m[1]] for m in matches]


class TestPattern:
    def test_pattern_anything(self) -> None:
        pattern = Pattern.Fragment()
        pattern.type.set(PatternType.ANYTHING)

        assert _all_fragment_matches(pattern, "12345") == [
            "",
            "1",
            "12",
            "123",
            "1234",
            "12345",
        ]
        assert _all_fragment_matches(pattern, "12345", 3) == ["", "4", "45"]

    def test_pattern_exact_match(self) -> None:
        pattern = Pattern.Fragment()
        pattern.type.set(PatternType.EXACT_MATCH)
        pattern.pattern_text.set("abCde")

        assert _all_fragment_matches(pattern, "aabcdee") == []
        assert _all_fragment_matches(pattern, "aabcdee", 1) == ["abcde"]
        assert _all_fragment_matches(pattern, "abcdee") == ["abcde"]
        assert _all_fragment_matches(pattern, "abcde") == ["abcde"]
        assert _all_fragment_matches(pattern, "abcDee") == ["abcDe"]

    def test_pattern_any_of(self) -> None:
        pattern = Pattern.Fragment()
        pattern.type.set(PatternType.ANY_OF)
        pattern.pattern_text.set("abCde")

        assert _all_fragment_matches(pattern, "11aaac1") == []
        assert _all_fragment_matches(pattern, "aaac1") == [
            "aaac",
            "aaa",
            "aa",
            "a",
        ]
        assert _all_fragment_matches(pattern, "11aaac1", 2) == [
            "aaac",
            "aaa",
            "aa",
            "a",
        ]
        assert _all_fragment_matches(pattern, "aAa") == ["aAa", "aA", "a"]

    def test_pattern_any_not_of(self) -> None:
        pattern = Pattern.Fragment()
        pattern.type.set(PatternType.ANY_NOT_IN)
        pattern.pattern_text.set("abCde")

        assert _all_fragment_matches(pattern, "cba123a") == []
        assert _all_fragment_matches(pattern, "123a") == ["123", "12", "1"]
        assert _all_fragment_matches(pattern, "cba123a", 3) == [
            "123",
            "12",
            "1",
        ]
        assert _all_fragment_matches(pattern, "12A") == ["12", "1"]

    def test_pattern_regex(self) -> None:
        pattern = Pattern.Fragment()
        pattern.type.set(PatternType.REGEX)
        pattern.pattern_text.set("a{4,5}")

        assert _all_fragment_matches(pattern, "baaaaaaa") == []
        assert _all_fragment_matches(pattern, "aaaaaaa") == ["aaaaa", "aaaa"]
        assert _all_fragment_matches(pattern, "aaaa") == ["aaaa"]
        assert _all_fragment_matches(pattern, "aaaaa") == ["aaaaa", "aaaa"]
        assert _all_fragment_matches(pattern, "baaaaaaa", 1) == [
            "aaaaa",
            "aaaa",
        ]
        assert _all_fragment_matches(pattern, "aaaAaaa") == []


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

        matches = find_matches(pattern, "1234xxx1234")
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
