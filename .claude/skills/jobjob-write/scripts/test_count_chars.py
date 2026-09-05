import unittest
from count_chars import parse_draft, count, check


SAMPLE = """# 테스트회사 개발 자소서 v1

## 1. 지원동기 (20자 이내)
안녕하세요 반갑습니다.
> 이전 보고줄은 무시되어야 함

## 2. 성장과정 (100자 이내)
짧은 글.
"""


class ParseDraftTest(unittest.TestCase):
    def test_parses_sections_with_limits(self):
        sections = parse_draft(SAMPLE)
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0]["number"], 1)
        self.assertEqual(sections[0]["title"], "지원동기")
        self.assertEqual(sections[0]["limit"], 20)
        self.assertEqual(sections[0]["body"], "안녕하세요 반갑습니다.")
        self.assertEqual(sections[1]["limit"], 100)
        self.assertEqual(sections[1]["body"], "짧은 글.")

    def test_limit_with_comma(self):
        text = "## 1. 지원동기 (1,000자 이내)\n본문\n"
        self.assertEqual(parse_draft(text)[0]["limit"], 1000)

    def test_section_without_limit(self):
        text = "## 1. 자유기술\n본문\n"
        self.assertIsNone(parse_draft(text)[0]["limit"])


class CountTest(unittest.TestCase):
    def test_with_and_without_spaces(self):
        with_sp, without_sp = count("안녕하세요 반갑습니다.")
        self.assertEqual(with_sp, 12)
        self.assertEqual(without_sp, 11)

    def test_newlines_not_counted_in_without_spaces(self):
        with_sp, without_sp = count("가나\n다라")
        self.assertEqual(with_sp, 5)
        self.assertEqual(without_sp, 4)


class CheckTest(unittest.TestCase):
    def test_over_limit_warns(self):
        self.assertEqual(check(25, 20), "초과")

    def test_under_85_percent_warns(self):
        self.assertEqual(check(16, 20), "부족")

    def test_within_range_ok(self):
        self.assertEqual(check(18, 20), "적정")

    def test_no_limit_returns_none(self):
        self.assertIsNone(check(18, None))


if __name__ == "__main__":
    unittest.main()
