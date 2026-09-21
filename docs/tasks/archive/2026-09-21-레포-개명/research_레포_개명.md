# research_레포_개명 — claude-web-harness 를 web-harness 로

> 담는 것: 옛 이름이 박힌 자리와 각 자리의 소비 경로, 개명이 깨뜨릴 수 있는 계약. 담지 않는 것: 변경 순서와 검증(→ `plan_레포_개명.md`). 읽는 시점: plan 검토 전.

## 배경

Claude Code 전용으로 시작했지만 지금은 Codex 와 같이 쓰는 하네스다. 이름의 `claude-` 가 실물과 어긋난다.

## 옛 이름이 있는 자리

| 자리 | 성격 | 소비 경로 |
|:--|:--|:--|
| `README.md`·`README.en.md` 제목 | 표시 이름 | 사람 |
| 같은 두 파일의 clone 명령 | 레포 주소 | 사람이 복사해 실행 |
| `kernel/__init__.py` `UPSTREAM` | 레포 주소 | `harness_install.py` 의 버전 대조와 `--upgrade` clone |
| 그림 정본 3장의 `meta.repository.url` | 레포 주소 | 뷰어의 SRC 링크. 영수증 해시에 포함된다 |
| `harness.architecture.json` 의 `meta.title` | 표시 이름 | 렌더 HTML·SVG 제목 |
| `rules.workflow.json` 의 url | 생성물 | `kernel/diagram/rules.py` 가 `git remote get-url origin` 에서 읽는다 |
| `harness-init` 스킬의 사고 서술 | clone 폴더명 예시 | 새 주소로 clone 하면 폴더명이 달라지므로 같이 바꾼다 |

`.codex/`·`AGENTS.md`·프리셋·프로파일에는 옛 이름이 없다.

## 깨질 수 있는 계약

- **이미 설치된 프로젝트의 `UPSTREAM`.** 옛 주소를 들고 있다. GitHub 은 개명된 레포의 git 주소와 raw 주소를 새 주소로 넘겨주므로 버전 대조와 `--upgrade` 는 계속 동작한다. 단 같은 계정에 `claude-web-harness` 라는 새 레포를 만들면 넘겨주기가 끊긴다.
- **그림 영수증.** url 은 정본 JSON 의 일부라 고치면 `spec_sha256_lf` 가 어긋난다. 검사 48 이 막으므로 deliver 를 다시 돌려야 한다. 순서는 코드 커밋 → deliver → 그림 커밋이다.
- **배포 정체 테스트.** `tests/test_release_identity.py` 는 README 의 `하네스 v`·`Harness v` 패턴만 본다. 제목 변경과 무관하다.

## 확인한 상태

- `Gruci/web-harness` 는 비어 있는 이름이다.
- `gh` 는 Gruci 계정으로 로그인돼 있다.
- 원격에 CI 와 PR 관행이 없고 master 직접 커밋이 이 레포의 관행이다.
- 열린 과업과 추가 worktree 가 없다.
