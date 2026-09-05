# jobjob 자소서 생성 시스템 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `C:\jobjob` 아래에 inbox → knowledge/profile/applications 폴더 체계와 두 개의 Claude Code 스킬(jobjob-intake 정리 스킬, jobjob-write 작성 스킬)을 구축해, 재료를 던지면 분류되고 "자소서 써줘"로 검증된 초안이 나오게 한다.

**Architecture:** 스킬은 얇게 유지하고 지식은 폴더에 둔다. jobjob-intake는 inbox 내용을 5개 유형으로 판별해 목적지에 정제본을 쓰고 원본은 processed로 옮긴다. jobjob-write는 profile과 knowledge를 읽어 초안을 만들고, Python 스크립트로 글자 수를 검증한다.

**Tech Stack:** Claude Code skills (SKILL.md), Markdown 지식 파일, Python 3.12 표준 라이브러리 (unittest, 외부 의존성 없음), 기존 anthropic-skills:docx (Word 출력 시)

**Spec:** `docs/superpowers/specs/2026-09-05-jobjob-cover-letter-system-design.md`

**참고:** `C:\jobjob`은 git 저장소가 아니다. Task 1에서 `git init`을 하고 이후 각 Task 끝에 커밋한다.

---

## File Structure

```
C:\jobjob\
├── .gitignore                                   profile/raw, processed 등 개인 원본 제외
├── README.md                                    사용법 한 장
├── inbox\.gitkeep
├── inbox\processed\.gitkeep
├── knowledge\principles.md                      작성 원칙 (기본/선택/상투어) - 시드 내용
├── knowledge\question-patterns.md               문항 유형별 접근법 - 시드 내용
├── knowledge\tips\.gitkeep
├── knowledge\samples\.gitkeep
├── knowledge\companies\.gitkeep
├── profile\resume.md                            빈 템플릿
├── profile\experiences.md                       빈 템플릿 + 경험 카드 양식
├── profile\raw\.gitkeep
├── applications\.gitkeep
├── .claude\skills\jobjob-intake\SKILL.md        정리 스킬
├── .claude\skills\jobjob-intake\references\classification.md   유형 판별표와 정제 규칙
├── .claude\skills\jobjob-write\SKILL.md         작성 스킬
├── .claude\skills\jobjob-write\references\draft-format.md      초안 파일 형식과 검증 보고 형식
├── .claude\skills\jobjob-write\scripts\count_chars.py          글자 수 검사
├── .claude\skills\jobjob-write\scripts\test_count_chars.py     unittest
└── tests\fixtures\                              가상 공고 2개, 가상 프로필 1개 (스킬 수동 테스트용)
    ├── posting-a.md
    ├── posting-b.md
    └── profile-sample\resume.md, experiences.md
```

책임 구분:
- `SKILL.md` 둘 다 200줄 이내. 절차와 "왜"만 담는다. 표나 긴 규칙은 `references/`로.
- `count_chars.py`는 draft 파일 하나를 입력받아 문항별 글자 수와 경고를 출력하는 단일 책임.
- `knowledge/*.md`는 스킬 코드가 아니라 데이터. 사용자 재료가 들어오면 intake 스킬이 갱신한다.

---

### Task 1: 폴더 골격, git 초기화, README

**Files:**
- Create: `C:\jobjob\.gitignore`
- Create: `C:\jobjob\README.md`
- Create: 빈 폴더들 (`.gitkeep`으로 유지)

- [ ] **Step 1: 폴더와 .gitkeep 생성**

```bash
cd /c/jobjob
mkdir -p inbox/processed knowledge/tips knowledge/samples knowledge/companies profile/raw applications tests/fixtures/profile-sample .claude/skills/jobjob-intake/references .claude/skills/jobjob-write/references .claude/skills/jobjob-write/scripts
touch inbox/.gitkeep inbox/processed/.gitkeep knowledge/tips/.gitkeep knowledge/samples/.gitkeep knowledge/companies/.gitkeep profile/raw/.gitkeep applications/.gitkeep
```

- [ ] **Step 2: .gitignore 작성**

개인 원본 파일과 실제 지원 작업물은 저장소에 넣지 않는다. 구조와 스킬만 버전 관리한다.

```gitignore
# 개인 원본 자료
profile/raw/*
!profile/raw/.gitkeep
inbox/*
!inbox/.gitkeep
!inbox/processed/
inbox/processed/*
!inbox/processed/.gitkeep

# 실제 지원 작업물 (개인정보 포함)
applications/*
!applications/.gitkeep

# Python
__pycache__/
*.pyc
```

- [ ] **Step 3: README.md 작성**

```markdown
# jobjob

AI로 한국 기업 신입 공채 자소서를 만드는 개인 작업 공간.

## 쓰는 법

1. 재료를 `inbox\`에 넣는다. 영상 팁 텍스트, 참고 자소서, 채용공고, 내 이력서, 기업 분석 무엇이든.
2. Claude Code에서 `/jobjob-intake` 또는 "inbox 정리해줘". 재료가 분류되어 `knowledge\`, `profile\`, `applications\`로 들어간다.
3. `/jobjob-write` 또는 "○○회사 자소서 써줘". 초안이 `applications\<회사>\draft-v1.md`에 생긴다.
4. 수정 요청하면 v2, v3으로 이어지고, "최종"이라고 하면 `final.md`가 된다. Word가 필요하면 "워드로도 뽑아줘".

## 폴더

| 폴더 | 내용 | 누가 관리 |
|---|---|---|
| `inbox\` | 던지는 곳 | 나 |
| `knowledge\` | 정제된 일반 지식 (원칙, 팁, 샘플, 기업 자료) | 스킬 |
| `profile\` | 내 이력과 경험 카드 | 스킬 (인터뷰로 채움) |
| `applications\` | 회사별 공고 정리와 초안 버전 | 스킬 |

자세한 설계: `docs\superpowers\specs\2026-09-05-jobjob-cover-letter-system-design.md`
```

- [ ] **Step 4: git 초기화 및 커밋**

```bash
cd /c/jobjob
git init
git add .
git commit -m "chore: scaffold jobjob folder structure and README

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

Expected: 커밋 성공. `git status`가 clean.

---

### Task 2: 지식 시드 파일 (principles.md, question-patterns.md)

**Files:**
- Create: `C:\jobjob\knowledge\principles.md`
- Create: `C:\jobjob\knowledge\question-patterns.md`

시드 내용은 널리 알려진 신입 공채 자소서 통념이다. 사용자 팁이 들어오면 intake 스킬이 이 파일을 갱신한다. 시드가 있어야 팁을 하나도 넣기 전에도 작성 스킬이 동작한다.

- [ ] **Step 1: principles.md 작성**

```markdown
# 자소서 작성 원칙

이 파일은 jobjob-write 스킬이 초안을 쓸 때 따르고, 검증 단계에서 체크하는 기준이다.
jobjob-intake 스킬이 새 팁을 받으면 여기에 병합한다. 각 원칙 뒤에 출처를 남긴다.

## 기본 원칙 (모든 문항에 적용, 검증 대상)

1. **두괄식.** 첫 문장에서 문항이 묻는 답을 바로 말한다. 배경 설명으로 시작하지 않는다. (출처: 시드)
2. **경험 하나를 깊게.** 한 문항에 경험 한두 개만 쓰고, 상황·행동·결과·배운 점이 드러나게 한다. 여러 경험 나열은 인상이 남지 않는다. (출처: 시드)
3. **숫자로 증명.** 결과는 가능한 한 수치로 쓴다. "성과를 냈다"가 아니라 "이탈률을 12% 줄였다". 수치가 없으면 비교 가능한 구체적 사실로 대신한다. (출처: 시드)
4. **직무 연결.** 모든 경험은 마지막에 지원 직무에서 어떻게 쓰일지로 이어진다. 회사와 무관한 자랑은 빼도 된다. (출처: 시드)
5. **본인 경험만.** profile/experiences.md에 없는 경험은 쓰지 않는다. 지어내지 않는다. 필요하면 인터뷰로 채운다. (출처: 시드, 시스템 규칙)
6. **글자 수 85~100%.** 제한의 85% 미만은 성의 부족으로 보이고, 초과는 입력이 안 된다. (출처: 시드)

## 선택 원칙 (상황에 따라 적용, 검증 시 참고만)

- 소제목을 쓸지는 회사 입력창 형식에 따른다. 줄바꿈이 보존되는 곳은 소제목이 가독성을 높인다.
- 문장은 짧게. 한 문장 40자 안팎을 기준으로, 두 가지 내용이 한 문장에 있으면 나눈다.

## 팁 충돌 기록

(intake 스킬이 서로 다른 조언을 만나면 여기에 나란히 적고 사용자 결정을 받는다. 결정되면 위 섹션으로 옮긴다.)

## 상투어 목록 (검증 시 걸러냄)

아래 표현이 초안에 있으면 검증 보고에 경고를 띄운다. 구체적 사실로 바꿔 쓴다.

- 누구보다 열정적인
- 뼈를 묻겠습니다
- 귀사의 발전에 이바지
- 어릴 적부터 꿈꿔온
- 성실함이 저의 무기
- 다양한 경험을 통해 성장
- 최선을 다하겠습니다
- 글로벌 인재
- 도전 정신을 바탕으로
- 화목한 가정에서 태어나
```

- [ ] **Step 2: question-patterns.md 작성**

```markdown
# 문항 유형별 접근법

jobjob-write 스킬이 공고의 문항을 아래 유형 중 하나로 분류하고 해당 접근법을 따른다.
유형이 애매하면 가장 가까운 것을 고르고 초안 보고에 "유형: ○○로 판단"이라고 남긴다.

## 1. 지원동기 (왜 이 회사, 왜 이 직무)

- 구조: 직무를 하고 싶은 이유(경험 근거) → 이 회사여야 하는 이유(회사 특성과 연결) → 입사 후 기여
- 재료: knowledge/companies/<회사>.md의 사업, 인재상. 없으면 posting.md의 직무 설명만으로 쓴다.
- 피할 것: 회사 홈페이지 소개문 요약. 회사 칭찬만 있고 본인이 없는 글.

## 2. 성장과정 / 가치관

- 구조: 가치관 한 문장 → 그 가치관이 형성된 경험 하나 → 그 가치관이 직무에서 어떻게 작동할지
- 재료: experiences.md에서 "배운 점"이 뚜렷한 경험.
- 피할 것: 연대기식 서술 (초등학교 때는… 중학교 때는…). 가정환경 묘사.

## 3. 직무역량 / 전문성

- 구조: 직무에 필요한 역량 한 가지 지목 → 그 역량을 증명하는 경험(상황·행동·결과) → 수치
- 재료: posting.md의 자격요건·우대사항과 가장 맞는 경험.
- 피할 것: 역량 이름만 나열. 팀 성과를 본인 성과처럼 쓰기 (본인 역할을 명확히).

## 4. 실패 / 어려움 극복

- 구조: 실패 상황(짧게) → 원인에 대한 본인 분석 → 취한 행동 → 결과와 이후 달라진 행동
- 재료: experiences.md에서 결과가 나빴거나 중간에 꼬였던 경험.
- 피할 것: 실패가 아닌 것을 실패로 포장. 남 탓. 극복 과정 없이 교훈만 말하기.

## 5. 협업 / 갈등 해결

- 구조: 갈등 상황과 이해관계 → 본인이 한 구체적 행동(대화, 조율, 역할 조정) → 결과
- 재료: 팀 프로젝트, 동아리, 아르바이트 경험.
- 피할 것: "소통으로 해결했다"처럼 추상적 행동. 상대를 깎아내리는 서술.

## 6. 입사 후 포부

- 구조: 1~2년 내 구체적 목표(직무 기반) → 그를 위해 지금 준비 중인 것 → 장기 방향 한 문장
- 재료: posting.md 직무 설명, 본인 자격증·학습 계획.
- 피할 것: "열심히 하겠다"류. 회사 비전 반복.

## 7. 자유 기술 / 기타

- 위 유형 중 가장 가까운 것을 고른다. 정말 없으면 "직무역량" 접근법을 기본으로 쓴다.
```

- [ ] **Step 3: 커밋**

```bash
cd /c/jobjob
git add knowledge/principles.md knowledge/question-patterns.md
git commit -m "feat: seed writing principles and question patterns

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: profile 템플릿

**Files:**
- Create: `C:\jobjob\profile\resume.md`
- Create: `C:\jobjob\profile\experiences.md`

경험 카드 양식을 고정해야 intake 스킬이 추가하고 write 스킬이 읽는 형식이 일치한다.

- [ ] **Step 1: resume.md 작성**

```markdown
# 이력 요약

(jobjob-intake 스킬이 이력서 원본에서 채운다. 직접 편집해도 된다.)

## 기본
- 이름:
- 전공 / 학교 / 졸업(예정) 연월:

## 학력

## 활동 (인턴, 동아리, 프로젝트, 대외활동)

## 자격증 / 어학

## 수상
```

- [ ] **Step 2: experiences.md 작성**

````markdown
# 경험 카드

jobjob-write 스킬은 이 파일에 있는 경험만 자소서에 쓴다. 여기 없는 경험은 지어내지 않고 인터뷰로 묻는다.
jobjob-intake 스킬과 jobjob-write 스킬의 인터뷰가 아래 양식으로 카드를 추가한다.

## 카드 양식

```
### [경험 제목] (기간, 소속)
- 상황: 어떤 문제나 과제가 있었나
- 역할: 팀에서 내가 맡은 것 (팀 성과와 내 기여를 구분)
- 행동: 내가 구체적으로 한 일
- 결과: 수치나 비교 가능한 사실
- 배운 점: 한 문장
- 관련 역량: (예: 데이터 분석, 협업, 문제 해결)
- 쓰기 좋은 문항: (예: 직무역량, 실패 극복)
```

## 카드 목록

(아직 없음)
````

- [ ] **Step 3: 커밋**

```bash
cd /c/jobjob
git add profile/resume.md profile/experiences.md
git commit -m "feat: add profile templates with experience card format

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: 글자 수 검사 스크립트 (TDD)

**Files:**
- Create: `C:\jobjob\.claude\skills\jobjob-write\scripts\count_chars.py`
- Test: `C:\jobjob\.claude\skills\jobjob-write\scripts\test_count_chars.py`

draft 파일을 파싱해 문항별로 공백 포함/제외 글자 수를 세고, 제한 대비 초과 또는 85% 미만이면 경고한다. 문항 헤더 형식은 `## N. 제목 (숫자자 이내)`이고, 본문은 다음 `##` 전까지다. `>`로 시작하는 인용줄은 스크립트가 붙이는 보고줄이므로 글자 수에서 제외한다.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# C:\jobjob\.claude\skills\jobjob-write\scripts\test_count_chars.py
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
```

- [ ] **Step 2: 테스트 실행해 실패 확인**

```bash
cd /c/jobjob/.claude/skills/jobjob-write/scripts && python -m unittest test_count_chars -v
```

Expected: `ModuleNotFoundError: No module named 'count_chars'`

- [ ] **Step 3: 구현**

```python
# C:\jobjob\.claude\skills\jobjob-write\scripts\count_chars.py
"""자소서 초안 파일의 문항별 글자 수를 세고 제한 대비 상태를 보고한다.

사용법:
    python count_chars.py <draft.md>

문항 헤더 형식: "## N. 제목 (1,000자 이내)"  - 괄호 안 숫자가 제한.
본문: 헤더 다음 줄부터 다음 "##" 전까지. ">"로 시작하는 줄(보고줄)은 제외.
"""
import re
import sys

HEADER_RE = re.compile(r"^##\s*(\d+)\.\s*(.+?)\s*(?:\(([\d,]+)\s*자[^)]*\))?\s*$")
MIN_RATIO = 0.85


def parse_draft(text):
    sections = []
    current = None
    for line in text.splitlines():
        m = HEADER_RE.match(line)
        if m:
            if current:
                current["body"] = "\n".join(current["lines"]).strip()
                sections.append(current)
            limit = int(m.group(3).replace(",", "")) if m.group(3) else None
            current = {"number": int(m.group(1)), "title": m.group(2).strip(),
                       "limit": limit, "lines": []}
            continue
        if current is None:
            continue
        if line.lstrip().startswith(">"):
            continue
        current["lines"].append(line)
    if current:
        current["body"] = "\n".join(current["lines"]).strip()
        sections.append(current)
    for s in sections:
        del s["lines"]
    return sections


def count(body):
    """(공백 포함, 공백 제외) 글자 수. 줄바꿈은 공백 포함에서 1자, 공백 제외에서는 제외."""
    with_spaces = len(body)
    without_spaces = len(re.sub(r"\s", "", body))
    return with_spaces, without_spaces


def check(with_spaces, limit):
    if limit is None:
        return None
    if with_spaces > limit:
        return "초과"
    if with_spaces < limit * MIN_RATIO:
        return "부족"
    return "적정"


def report(sections):
    lines = []
    for s in sections:
        w, wo = count(s["body"])
        status = check(w, s["limit"])
        limit_txt = f"{s['limit']:,}자 이내" if s["limit"] else "제한 없음"
        status_txt = f" [{status}]" if status else ""
        lines.append(f"{s['number']}. {s['title']} ({limit_txt}): 공백 포함 {w:,}자 / 공백 제외 {wo:,}자{status_txt}")
    return "\n".join(lines)


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        sections = parse_draft(f.read())
    if not sections:
        print("문항 헤더(## N. 제목 (N자 이내))를 찾지 못했습니다.")
        return 1
    print(report(sections))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
cd /c/jobjob/.claude/skills/jobjob-write/scripts && python -m unittest test_count_chars -v
```

Expected: `Ran 9 tests ... OK`

- [ ] **Step 5: 실제 파일로 스모크 테스트**

```bash
cd /c/jobjob
printf '# t\n\n## 1. 지원동기 (20자 이내)\n안녕하세요 반갑습니다.\n' > tests/smoke-draft.md
python .claude/skills/jobjob-write/scripts/count_chars.py tests/smoke-draft.md
rm tests/smoke-draft.md
```

Expected: `1. 지원동기 (20자 이내): 공백 포함 12자 / 공백 제외 11자 [부족]`

- [ ] **Step 6: 커밋**

```bash
cd /c/jobjob
git add .claude/skills/jobjob-write/scripts/
git commit -m "feat: add character count checker with tests

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: jobjob-intake 스킬

**Files:**
- Create: `C:\jobjob\.claude\skills\jobjob-intake\SKILL.md`
- Create: `C:\jobjob\.claude\skills\jobjob-intake\references\classification.md`

- [ ] **Step 1: classification.md 작성**

````markdown
# 유형 판별과 정제 규칙

## 판별표

내용을 기준으로 판별한다. 파일명은 힌트일 뿐이다.

| 유형 | 판별 신호 | 목적지 |
|---|---|---|
| A. 영상 팁 | "~하세요", "~하지 마세요" 조언 어조. 캡션·해시태그 형식. 유튜브/인스타 URL. 크리에이터 이름 | `knowledge/tips/<출처-슬러그>.md` |
| B. 자소서 샘플 | 문항 제목 + 답변 구조. 1인칭 서술. 지원동기·성장과정 같은 제목. 본인 것이 아님 | `knowledge/samples/<회사-직무-또는-주제>.md` |
| C. 채용공고 | 회사명, 직무명, 자격요건, 우대사항, 자소서 문항과 글자 수, 접수 기간 | `applications/<YYYY-MM>-<회사>-<직무>/posting.md` |
| D. 본인 자료 | 사용자 이름. 이력서·포트폴리오 형식. 사용자가 "내 거"라고 말함 | `profile/resume.md`, `profile/experiences.md`, 원본은 `profile/raw/` |
| E. 기업 자료 | 특정 회사의 사업·문화·면접 후기·뉴스. 공고도 자소서도 아님 | `knowledge/companies/<회사>.md` |

B와 D는 겉모습이 같다. 자소서 형식인데 사용자가 누구 것인지 말하지 않았으면 반드시 묻는다.
샘플이 profile에 들어가면 남의 경험이 사용자 자소서에 섞인다.

## 유형별 정제

### A. 영상 팁 → tips/ + principles.md 병합

1. `knowledge/tips/<출처-슬러그>.md` 작성:
   ```
   # <영상 제목 또는 한 줄 요약>
   - 출처: <URL 또는 크리에이터명>, 정리일 <YYYY-MM-DD>
   - 원문 요지: (2~3문장)

   ## 추출한 규칙
   - <규칙 문장 1> - 적용 문항: <전체/지원동기/...>
   - <규칙 문장 2>
   ```
   규칙 문장은 "~한다" 형태의 실행 가능한 문장으로 바꾼다. 크리에이터의 문장을 그대로 옮기지 않는다.
2. `knowledge/principles.md` 병합:
   - 기존 원칙과 같은 뜻이면 해당 원칙의 출처에 추가만 한다.
   - 새 원칙이면 "기본 원칙" 또는 "선택 원칙"에 추가하고 출처를 적는다. 모든 문항에 항상 적용되는 것만 기본 원칙.
   - 기존 원칙과 충돌하면 "팁 충돌 기록"에 두 견해를 나란히 적고, 보고 시 사용자에게 어느 쪽을 기본으로 할지 묻는다.
   - 상투어 표현이 나오면 상투어 목록에 추가.

### B. 자소서 샘플 → samples/

파일 앞머리에 아래 블록을 붙이고 본문은 그대로 둔다.
```
> 참고용 샘플. 본인 경험 아님. 문체와 구조만 참고하고 경험·문장은 가져오지 않는다.
> 출처: <어디서 왔는지>, 정리일 <YYYY-MM-DD>
> 배울 점: <2~3줄. 예: 두괄식이 뚜렷함, 수치 활용이 좋음>
> 주의할 점: <있으면>
```

### C. 채용공고 → applications/.../posting.md

```
# <회사> <직무> 채용공고

- 접수 기간:
- 출처:
- 정리일: <YYYY-MM-DD>

## 직무 요건
- 담당 업무:
- 자격 요건:
- 우대 사항:

## 인재상 / 키워드
(공고에 있으면. 없으면 "공고에 없음")

## 자소서 문항
| 번호 | 문항 | 글자 수 제한 | 유형 (question-patterns 기준) |
|---|---|---|---|
| 1 | ... | 1,000자 | 지원동기 |
```

폴더명은 `<YYYY-MM>-<회사>-<직무>`. 같은 회사·직무 폴더가 이미 있으면 posting.md를 덮어쓰지 말고 `posting-<날짜>.md`로 저장하고 보고한다.

### D. 본인 자료 → profile/

1. 원본 파일을 `profile/raw/`로 복사한다.
2. 이력 정보(학력, 활동 목록, 자격증, 수상)는 `profile/resume.md`의 해당 섹션에 병합한다. 중복은 넣지 않는다.
3. 경험 서술이 있으면 `profile/experiences.md`의 카드 양식으로 카드를 만든다. 원본에 없는 항목(결과 수치, 배운 점 등)은 비워 두고 "(인터뷰 필요)"라고 적는다. 지어내지 않는다.
4. 이미 같은 경험 카드가 있으면 새로 만들지 말고 비어 있던 항목만 채운다.

### E. 기업 자료 → companies/

`knowledge/companies/<회사>.md`가 없으면 만들고, 있으면 아래 블록을 끝에 추가한다.
```
## <YYYY-MM-DD> <자료 종류: 기업 분석 / 면접 후기 / 뉴스 / 기타>
- 출처:
- 요지: (3~5줄)
- 자소서에 쓸 만한 것: (인재상 키워드, 최근 사업 방향, 직무 관련 사실)
```
````

- [ ] **Step 2: SKILL.md 작성**

````markdown
---
name: jobjob-intake
description: C:\jobjob\inbox에 들어온 자소서 재료(영상 팁, 참고 자소서, 채용공고, 본인 이력서·경험 메모, 기업 분석·면접 후기)를 유형별로 분류하고 정제해 knowledge/, profile/, applications/ 폴더에 넣는다. 사용자가 "inbox 정리해줘", "이거 분류해줘", "이 팁 반영해줘", "이 공고 정리해줘", "내 이력서 넣어줘"라고 하거나, 자소서 관련 재료를 채팅에 붙여넣으며 저장·정리를 원할 때 반드시 사용한다. 자소서를 쓰는 요청에는 jobjob-write를 쓴다.
---

# jobjob-intake: 재료 정리

사용자는 재료를 `C:\jobjob\inbox\`에 던지거나 채팅에 붙여넣기만 한다. 이 스킬이 그것을 다섯 유형으로 나눠
작성 스킬(jobjob-write)이 바로 쓸 수 있는 형태로 정제한다. 분류가 정확해야 작성 스킬이 남의 경험을
사용자 것으로 착각하지 않고, 팁이 원칙으로 쌓인다.

## 절차

1. **대상 확인.** `inbox/` 안의 파일 목록을 본다 (`processed/` 제외). 채팅에 붙여넣은 텍스트가 있으면 그것도 대상이다.
   대상이 없으면 "inbox가 비어 있습니다"라고 말하고 끝낸다.
2. **하나씩 읽고 판별.** `references/classification.md`의 판별표로 유형을 정한다. 내용 기준이다.
   한 파일에 여러 유형이 섞여 있으면 (예: 공고 + 회사 소개) 나눠서 각각 처리한다.
3. **애매하면 묻는다.** 특히 자소서 형식은 본인 것인지 참고 샘플인지 반드시 확인한다.
   여러 파일이 애매하면 한 번에 모아서 묻는다.
4. **정제해서 쓴다.** `references/classification.md`의 유형별 정제 규칙을 따른다.
   - 영상 팁은 규칙 문장으로 바꾸고 `knowledge/principles.md`에 병합한다. 크리에이터 문장을 그대로 옮기지 않는다.
   - 본인 자료에서 비어 있는 항목은 "(인터뷰 필요)"로 남긴다. 채우려고 지어내지 않는다.
5. **원본 이동.** 처리한 inbox 파일을 `inbox/processed/`로 옮긴다. 지우지 않는다. 채팅 붙여넣기는 원본이 없으므로 생략.
6. **보고.** 아래 형식으로 한 번에 보고한다.

## 보고 형식

```
정리 완료: N건

| 원본 | 유형 | 저장 위치 | 비고 |
|---|---|---|---|
| reels-tip-1.txt | 영상 팁 | knowledge/tips/xxx.md | 원칙 2개 추가, 1개 기존과 동일 |

principles.md 변경:
- 추가: "..."
- 충돌: "..." vs "..." → 어느 쪽을 기본으로 할까요?

profile 변경:
- 경험 카드 추가: <제목> (결과 수치 인터뷰 필요)
```

## 왜 이렇게 하나

- **원본을 지우지 않는 이유:** 잘못 분류돼도 processed에서 꺼내 다시 넣으면 된다.
- **팁을 규칙 문장으로 바꾸는 이유:** 작성 스킬이 검증 단계에서 "이 원칙을 지켰나"를 체크해야 하므로 실행 가능한 문장이어야 한다. 또한 남의 문장을 그대로 쌓지 않아 저작권 문제를 피한다.
- **충돌을 사용자에게 묻는 이유:** 자소서 조언은 유파가 갈린다. 스킬이 임의로 고르면 사용자가 원한 스타일과 어긋난다.
````

- [ ] **Step 3: 스킬 로드 확인**

Claude Code에서 `/jobjob-intake`를 입력해 스킬이 목록에 뜨고 내용이 로드되는지 확인한다. inbox가 비어 있으므로 "inbox가 비어 있습니다"가 나와야 한다.

Expected: 스킬 로드됨, 빈 inbox 메시지.

- [ ] **Step 4: 커밋**

```bash
cd /c/jobjob
git add .claude/skills/jobjob-intake/
git commit -m "feat: add jobjob-intake skill for classifying inbox materials

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: jobjob-write 스킬

**Files:**
- Create: `C:\jobjob\.claude\skills\jobjob-write\SKILL.md`
- Create: `C:\jobjob\.claude\skills\jobjob-write\references\draft-format.md`

- [ ] **Step 1: draft-format.md 작성**

````markdown
# 초안 파일 형식과 검증 보고 형식

## 초안 파일 (applications/<폴더>/draft-vN.md)

문항 헤더는 반드시 `## N. 제목 (제한자 이내)` 형식이어야 `scripts/count_chars.py`가 읽는다.
제한이 없는 문항은 `## N. 제목`으로 쓴다. 각 문항 본문 뒤에 `>` 보고줄을 붙인다.

```
# <회사> <직무> 자소서 v<N>

- 작성일: YYYY-MM-DD
- 공고: posting.md
- 이전 버전 대비 변경: (v2부터. v1은 "초안")

## 1. 지원동기 (1,000자 이내)
<본문>
> 공백 포함 947자 / 공백 제외 712자 · 사용 경험: 캡스톤 프로젝트, 인턴십 · 유형: 지원동기

## 2. 직무역량 (800자 이내)
<본문>
> 공백 포함 ...
```

## 검증 보고 (채팅에 출력)

```
초안 저장: applications/2026-09-삼성전자-SW개발/draft-v1.md

| 문항 | 제한 | 공백 포함 | 공백 제외 | 상태 | 사용 경험 |
|---|---|---|---|---|---|
| 1. 지원동기 | 1,000 | 947 | 712 | 적정 | 캡스톤, 인턴십 |
| 2. 직무역량 | 800 | 812 | 605 | 초과 | 캡스톤 |

원칙 체크:
- 두괄식: 1 O, 2 O
- 숫자로 증명: 1 O, 2 X (결과 수치 없음. 인터뷰 필요: 캡스톤 성능 개선 수치)
- 상투어: 없음

다음: 2번 문항 12자 줄이고, 캡스톤 수치 알려주시면 반영하겠습니다.
```

## 인터뷰 형식

한 번에 한 문항, 질문 3~4개 이내. 답을 받으면 profile/experiences.md 카드에 바로 반영한다.

```
2번 직무역량 문항에 캡스톤 프로젝트를 쓰려고 합니다. 세 가지만 알려 주세요.
1. 프로젝트에서 본인이 맡은 부분은 정확히 무엇이었나요?
2. 결과를 숫자로 말할 수 있나요? (예: 처리 속도 30% 개선, 사용자 200명)
3. 가장 어려웠던 점과 어떻게 풀었는지 한 줄로요.
```
````

- [ ] **Step 2: SKILL.md 작성**

````markdown
---
name: jobjob-write
description: 사용자 본인의 한국 기업 신입 공채 자소서를 문항별·글자 수 제한에 맞춰 작성하고 검증한다. C:\jobjob의 profile/(본인 경험 카드), knowledge/(작성 원칙, 문항 패턴, 기업 자료), applications/(공고 정리)를 읽어 초안을 만들고, 글자 수·경험 출처·원칙 준수·상투어를 자동 검사한다. "자소서 써줘", "<회사> 자소서 초안", "<문항> 다시 써줘", "지원동기 고쳐줘", "자소서 최종본", "워드로 뽑아줘"처럼 자소서 작성·수정·검토·출력 요청에 반드시 사용한다. 재료 분류 요청은 jobjob-intake를 쓴다.
---

# jobjob-write: 자소서 작성

목표는 사용자의 실제 경험만으로, 공고 문항과 글자 수에 맞고, knowledge/principles.md 원칙을 지킨 초안을
만드는 것이다. 지어낸 경험이 하나라도 들어가면 면접에서 무너지므로, 부족한 재료는 인터뷰로 채운다.

## 절차

### 1. 대상 확인
- 어느 회사·직무인지 정한다. `applications/`에서 해당 폴더의 `posting.md`를 찾는다.
- 없으면: 공고를 inbox에 넣어 달라고 하거나 (그러면 jobjob-intake로 정리), 문항과 글자 수를 직접 물어 `posting.md`를 만든다.
- 특정 문항만 고치는 요청이면 최신 `draft-vN.md`를 읽고 그 문항만 다룬다.

### 2. 재료 수집
- `profile/experiences.md`, `profile/resume.md`를 읽는다.
- `knowledge/principles.md`, `knowledge/question-patterns.md`를 읽는다.
- `knowledge/companies/<회사>.md`가 있으면 읽는다.
- 각 문항을 question-patterns의 유형으로 분류하고, 카드의 "쓰기 좋은 문항"과 "관련 역량"을 보고 문항별 경험 후보를 1~2개 고른다.
- `knowledge/samples/`는 문체가 궁금할 때만 1~2편 읽는다. 샘플의 경험과 문장은 절대 가져오지 않는다.

### 3. 부족분 인터뷰
- 문항에 맞는 경험이 없거나, 고른 카드에 "(인터뷰 필요)" 항목이 있거나, 결과 수치가 없으면 묻는다.
- `references/draft-format.md`의 인터뷰 형식대로 한 번에 한 문항, 3~4개 질문.
- 답을 받으면 `profile/experiences.md`의 카드를 갱신한다. 다음 지원 때 다시 묻지 않기 위해서다.
- 사용자가 "그냥 있는 걸로 써줘"라고 하면 인터뷰 없이 진행하되 빠진 부분을 보고에 적는다.

### 4. 초안 작성
- 문항별로 question-patterns의 구조를 따르고, principles.md 기본 원칙을 지킨다.
- 초안을 `applications/<폴더>/draft-vN.md`에 `references/draft-format.md` 형식으로 저장한다. 기존 최고 버전 +1.
- 헤더 형식 `## N. 제목 (제한자 이내)`을 정확히 지킨다. 글자 수 스크립트가 이 형식을 읽는다.

### 5. 검증과 보고
1. 글자 수: `python .claude/skills/jobjob-write/scripts/count_chars.py <draft 경로>` 실행. 결과를 각 문항의 `>` 보고줄과 채팅 표에 반영한다.
   "초과"면 줄여서 다시 저장하고 다시 센다. "부족"이면 보강할 내용을 인터뷰하거나 보고에 적는다.
2. 경험 출처: 초안에 등장하는 모든 경험이 `profile/experiences.md` 카드에 있는지 대조한다. 없는 것은 지어낸 것이므로 빼고 다시 쓴다.
3. 원칙 준수: principles.md 기본 원칙 각각을 문항마다 체크한다. 두괄식은 첫 문장이 답인지, 숫자 증명은 수치가 있는지, 직무 연결은 마지막에 직무 얘기로 닫히는지.
4. 상투어: principles.md 상투어 목록의 표현이 있으면 경고하고 바꾼다.
5. `references/draft-format.md`의 검증 보고 형식으로 채팅에 보고한다.

### 6. 수정과 최종
- 수정 요청은 새 버전(`draft-v(N+1).md`)으로 저장하고 "이전 버전 대비 변경"을 적는다. 이전 버전은 지우지 않는다.
- "최종"이라고 하면 최신 draft를 `final.md`로 복사한다.
- Word 요청이 있으면 `anthropic-skills:docx` 스킬을 불러 `final.md` 내용으로 `final.docx`를 같은 폴더에 만든다. 문항 제목은 굵게, 본문은 일반 단락, `>` 보고줄은 넣지 않는다.

## 왜 이렇게 하나

- **경험 출처를 대조하는 이유:** 모델은 그럴듯한 경험을 만들어 내기 쉽다. 카드에 없는 경험은 사용자의 것이 아니다.
- **글자 수를 스크립트로 세는 이유:** 눈대중은 수십 자씩 틀린다. 공백 포함/제외를 둘 다 보여 주는 이유는 채용 사이트마다 기준이 다르기 때문이다.
- **버전을 남기는 이유:** 수정하다 이전 표현이 더 나았음을 알게 되는 일이 잦다. 다음 회사 지원 때 비슷한 문항 답변을 재활용할 수도 있다.
- **인터뷰를 짧게 하는 이유:** 질문이 길면 사용자가 지쳐 대충 답한다. 문항 하나 분량의 재료만 받고 바로 쓴다.
````

- [ ] **Step 3: 스킬 로드 확인**

Claude Code에서 `/jobjob-write`를 입력한다. posting.md가 없으므로 회사·직무와 문항을 묻는 흐름이 나와야 한다.

Expected: 스킬 로드됨, 대상 확인 질문.

- [ ] **Step 4: 커밋**

```bash
cd /c/jobjob
git add .claude/skills/jobjob-write/
git commit -m "feat: add jobjob-write skill for drafting and validating cover letters

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: 테스트 픽스처 (가상 공고 2개, 가상 프로필 1개)

**Files:**
- Create: `C:\jobjob\tests\fixtures\posting-a.md`
- Create: `C:\jobjob\tests\fixtures\posting-b.md`
- Create: `C:\jobjob\tests\fixtures\profile-sample\resume.md`
- Create: `C:\jobjob\tests\fixtures\profile-sample\experiences.md`

실제 profile을 건드리지 않고 스킬을 돌려 보기 위한 가상 데이터. 회사명은 가상이다.

- [ ] **Step 1: posting-a.md (IT 개발직, 문항 3개)**

```markdown
# 한빛소프트웨어 백엔드 개발 신입 채용

- 접수 기간: 2026-09-01 ~ 2026-09-20
- 출처: (가상 공고, 테스트용)

## 직무 요건
- 담당 업무: 결제 서비스 API 개발 및 운영
- 자격 요건: 컴퓨터공학 관련 전공 또는 동등한 실무 경험, Java 또는 Kotlin 사용 경험
- 우대 사항: 대용량 트래픽 처리 경험, 오픈소스 기여

## 인재상 / 키워드
끝까지 파고드는 집요함, 동료와 함께 성장

## 자소서 문항
| 번호 | 문항 | 글자 수 제한 |
|---|---|---|
| 1 | 한빛소프트웨어에 지원한 이유와 입사 후 이루고 싶은 목표를 적어 주세요. | 1,000자 |
| 2 | 가장 몰입했던 개발 경험과 그 과정에서 겪은 기술적 어려움을 어떻게 해결했는지 적어 주세요. | 1,000자 |
| 3 | 팀 프로젝트에서 의견 충돌을 조율한 경험을 적어 주세요. | 600자 |
```

- [ ] **Step 2: posting-b.md (마케팅직, 문항 2개, 짧은 제한)**

```markdown
# 온새미로식품 브랜드마케팅 신입 채용

- 접수 기간: 2026-09-05 ~ 2026-09-25
- 출처: (가상 공고, 테스트용)

## 직무 요건
- 담당 업무: 신제품 런칭 캠페인 기획, SNS 채널 운영
- 자격 요건: 4년제 학사 이상
- 우대 사항: SNS 콘텐츠 제작 경험, 데이터 기반 마케팅 경험

## 인재상 / 키워드
공고에 없음

## 자소서 문항
| 번호 | 문항 | 글자 수 제한 |
|---|---|---|
| 1 | 본인의 성장과정을 통해 형성된 가치관을 소개해 주세요. | 500자 |
| 2 | 마케팅 직무를 수행하는 데 필요한 역량을 갖추기 위해 노력한 경험을 적어 주세요. | 800자 |
```

- [ ] **Step 3: profile-sample/resume.md**

```markdown
# 이력 요약 (테스트용 가상 인물)

## 기본
- 이름: 김테스트
- 전공 / 학교 / 졸업(예정) 연월: 컴퓨터공학 / 가상대학교 / 2027-02

## 학력
- 가상대학교 컴퓨터공학과 (2021-03 ~ 2027-02 예정)

## 활동
- 캡스톤 프로젝트 "중고거래 채팅 서비스" 백엔드 담당 (2025-09 ~ 2025-12)
- 스타트업 인턴 (백엔드, 2026-01 ~ 2026-02)
- 교내 개발 동아리 운영진 (2024-03 ~ 2025-02)

## 자격증 / 어학
- 정보처리기사 (2025-11)
- TOEIC 850 (2025-06)

## 수상
- 교내 캡스톤 경진대회 우수상 (2025-12)
```

- [ ] **Step 4: profile-sample/experiences.md**

```markdown
# 경험 카드 (테스트용 가상 인물)

## 카드 목록

### 중고거래 채팅 서비스 캡스톤 (2025-09 ~ 2025-12, 가상대학교)
- 상황: 4인 팀. 실시간 채팅 기능에서 동시 접속 100명 넘으면 메시지 지연이 3초 이상 발생
- 역할: 백엔드 전담. 프론트 2명, 기획 1명
- 행동: 폴링 방식을 WebSocket으로 교체하고, 메시지 저장을 비동기 큐로 분리
- 결과: 동시 접속 500명에서 지연 0.3초 이하. 교내 경진대회 우수상
- 배운 점: 병목은 추측이 아니라 측정으로 찾아야 한다
- 관련 역량: 문제 해결, 성능 최적화, Java/Spring
- 쓰기 좋은 문항: 직무역량, 실패 극복, 몰입 경험

### 스타트업 백엔드 인턴 (2026-01 ~ 2026-02, 가상스타트업)
- 상황: 결제 API 장애 알림이 잦았으나 원인 파악에 매번 반나절 소요
- 역할: 인턴 1명. 사수 1명 지도
- 행동: 로그에 요청 ID를 붙이는 구조를 제안하고 구현. 장애 대응 문서 작성
- 결과: 원인 파악 시간 평균 4시간에서 30분으로 단축
- 배운 점: 운영 편의는 코드만큼 중요하다
- 관련 역량: 운영, 문서화, 주도성
- 쓰기 좋은 문항: 직무역량, 지원동기(결제 도메인)

### 개발 동아리 운영진 갈등 (2024-09, 가상대학교)
- 상황: 스터디 커리큘럼을 두고 운영진 둘이 "기초부터" vs "프로젝트부터"로 대립. 2주간 진행 정지
- 역할: 운영진 3인 중 1인. 중재 역할
- 행동: 신입 부원 12명에게 설문을 돌려 실제 수준을 파악하고, 2주 기초 후 프로젝트로 넘어가는 절충안 제시
- 결과: 절충안 채택. 학기 말 부원 이탈률 전년 40%에서 15%로 감소
- 배운 점: 의견 대립은 데이터로 풀린다
- 관련 역량: 협업, 갈등 조율, 데이터 기반 의사결정
- 쓰기 좋은 문항: 협업/갈등, 성장과정
```

- [ ] **Step 5: 커밋**

```bash
cd /c/jobjob
git add tests/
git commit -m "test: add fixture postings and sample profile for skill testing

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: 스킬 통합 테스트 (수동, 픽스처 사용)

이 태스크는 코드가 아니라 스킬을 실제로 돌려 보는 것이다. 실제 profile을 보호하기 위해 픽스처를 임시로 복사해 쓴다.

**Files:**
- 임시 사용: `tests/fixtures/*` → `profile/`, `inbox/`
- 산출: `applications/2026-09-한빛소프트웨어-백엔드개발/draft-v1.md` 등

- [ ] **Step 1: 실제 profile 백업 후 픽스처 투입**

```bash
cd /c/jobjob
cp profile/resume.md profile/resume.md.bak
cp profile/experiences.md profile/experiences.md.bak
cp tests/fixtures/profile-sample/resume.md profile/resume.md
cp tests/fixtures/profile-sample/experiences.md profile/experiences.md
cp tests/fixtures/posting-a.md inbox/
cp tests/fixtures/posting-b.md inbox/
```

- [ ] **Step 2: intake 스킬 테스트**

Claude Code에서 `/jobjob-intake` 실행.

Expected:
- 두 파일 모두 "채용공고"로 판별
- `applications/2026-09-한빛소프트웨어-백엔드개발/posting.md`, `applications/2026-09-온새미로식품-브랜드마케팅/posting.md` 생성
- 문항 표에 유형(지원동기+포부, 직무역량/실패극복, 협업 등)이 채워짐
- 원본이 `inbox/processed/`로 이동
- 보고 표 출력

확인 명령:
```bash
ls /c/jobjob/applications/ /c/jobjob/inbox/ /c/jobjob/inbox/processed/
```

- [ ] **Step 3: write 스킬 테스트 (공고 A)**

Claude Code에서 "한빛소프트웨어 자소서 써줘" 입력.

Expected:
- posting.md를 읽고 문항 3개 모두 카드에서 경험을 고름 (캡스톤, 인턴, 동아리 갈등)
- 카드에 재료가 충분하므로 인터뷰 없이 또는 최소 질문으로 진행
- `draft-v1.md` 생성. 헤더가 `## 1. ... (1,000자 이내)` 형식
- 글자 수 스크립트 실행 결과가 보고 표에 있음
- 카드에 없는 경험이 없음 (직접 읽어 확인)
- 상투어 목록의 표현이 없음

확인 명령:
```bash
cd /c/jobjob && python .claude/skills/jobjob-write/scripts/count_chars.py "applications/2026-09-한빛소프트웨어-백엔드개발/draft-v1.md"
```
Expected: 문항 3개 모두 "적정" 또는 스킬이 보고한 상태와 일치.

- [ ] **Step 4: write 스킬 테스트 (공고 B, 재료 부족 상황)**

"온새미로식품 자소서 써줘" 입력. 프로필이 개발자라 마케팅 역량 경험이 약하므로 인터뷰가 발동해야 한다.

Expected:
- 2번 문항(마케팅 역량)에 대해 3~4개 이내 질문
- "그냥 있는 걸로 써줘"라고 답하면 인터뷰 없이 작성하고 보고에 "마케팅 직접 경험 없음, 동아리 운영 경험으로 대체" 같은 메모

- [ ] **Step 5: 수정과 최종, Word 테스트**

"1번 문항 좀 더 짧게" → `draft-v2.md` 생성, 변경 사항 기록 확인.
"최종" → `final.md` 생성 확인.
"워드로도 뽑아줘" → `final.docx` 생성 확인.

```bash
ls "/c/jobjob/applications/2026-09-한빛소프트웨어-백엔드개발/"
```
Expected: `posting.md draft-v1.md draft-v2.md final.md final.docx`

- [ ] **Step 6: 발견한 문제 수정**

테스트에서 스킬이 형식을 어기거나(헤더 형식, 보고 표), 지어낸 경험을 넣거나, 인터뷰가 길면 해당 SKILL.md 또는 references를 고친다. 고친 뒤 해당 Step을 다시 돌린다.

- [ ] **Step 7: 픽스처 정리, 실제 profile 복원**

```bash
cd /c/jobjob
mv profile/resume.md.bak profile/resume.md
mv profile/experiences.md.bak profile/experiences.md
rm -rf "applications/2026-09-한빛소프트웨어-백엔드개발" "applications/2026-09-온새미로식품-브랜드마케팅"
rm -f inbox/processed/posting-a.md inbox/processed/posting-b.md
git status
```

Expected: `git status`에 스킬 수정 외 변경 없음 (applications, inbox는 gitignore 대상).

- [ ] **Step 8: 커밋**

```bash
cd /c/jobjob
git add .claude/skills/
git commit -m "fix: adjust skills based on integration test findings

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

(수정이 없었으면 이 커밋은 생략.)

---

## 완료 후

- 사용자가 실제 이력서와 영상 팁을 `inbox/`에 넣고 `/jobjob-intake`를 돌린다.
- 실제 공고로 `/jobjob-write`를 돌려 첫 자소서를 만든다.
- 이 과정에서 나온 피드백으로 principles.md와 스킬을 다듬는다. 스킬 설명문(description) 최적화는 anthropic-skills:skill-creator의 description optimization으로 나중에 할 수 있다.
