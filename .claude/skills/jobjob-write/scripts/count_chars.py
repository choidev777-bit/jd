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
    # Windows 콘솔 기본 인코딩(cp949)에서 한글이 깨지므로 UTF-8로 고정
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
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
