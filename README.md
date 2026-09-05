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
