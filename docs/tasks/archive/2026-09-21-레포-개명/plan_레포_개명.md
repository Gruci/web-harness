# plan_레포_개명 — claude-web-harness 를 web-harness 로

> 담는 것: 개명의 변경 자리·순서·검증. 담지 않는 것: 옛 이름의 소비 경로와 호환성 근거(→ `research_레포_개명.md`). 읽는 시점: 구현 중 Todo 대조.

## 승인 근거

0단계 인터뷰에서 사용자가 이름 `web-harness` 와 범위 "GitHub 레포명까지"를 골랐다. 그 선택지에 레포 개명·origin·README clone 주소·`UPSTREAM`·그림 4장 재렌더가 명시돼 있었으므로 같은 범위의 승인을 다시 받지 않는다. 로컬 폴더명은 범위 밖이다.

## 접근

| # | 자리 | 변경 |
|:--|:--|:--|
| 1 | GitHub | `gh repo rename web-harness` 후 `git remote set-url origin https://github.com/Gruci/web-harness` |
| 2 | `kernel/__init__.py` | `UPSTREAM = "https://github.com/Gruci/web-harness"` |
| 3 | `README.md` | 제목 `# web-harness`, 버전 줄 `웹 개발용 하네스 v3.8.0`, clone 주소 |
| 4 | `README.en.md` | 제목 `# web-harness`, 버전 줄 `Web development harness v3.8.0`, clone 주소 |
| 5 | `.claude/skills/harness-init/SKILL.md` | 사고 서술의 폴더명을 `web-harness/` 로 |
| 6 | 그림 정본 3장 | `meta.repository.url`, architecture 는 `meta.title` 도 |
| 7 | 그림 산출물 | 2~6 커밋 뒤 `kernel.diagram rules` 와 `deliver` 3회, 그다음 그림 커밋 |

버전 줄은 `하네스 v`·`Harness v` 패턴을 유지해 `tests/test_release_identity.py` 의 정규식에 그대로 걸린다.
`KERNEL_VERSION` 은 올리지 않는다. 옛 주소가 넘겨지므로 설치본이 새 `UPSTREAM` 을 급히 받을 이유가 없고, 다음 배포에 실려 간다.

## 파일 설계표

| 경로 | 구분 | 책임 | 규모 |
|:--|:--|:--|--:|
| `kernel/__init__.py` | 수정 | 원류 주소 | 1줄 |
| `README.md`·`README.en.md` | 수정 | 제목·버전 줄·clone 주소 | 각 3줄 |
| `.claude/skills/harness-init/SKILL.md` | 수정 | 폴더명 예시 | 1줄 |
| `docs/architecture/*.json` 4장과 산출물 | 수정·재생성 | url·title | 각 1~2줄 |

반응형 설계표와 행동 테스트는 해당 없음이다. 화면과 수집·계산 로직이 없다.
병렬 후보는 미발동이다. 전부 순차 의존이다.
아키텍처 델타는 미발동이다. 노드와 엣지가 그대로다.

## 호환성

깨지는 계약이 없다. 옛 주소의 넘겨주기는 같은 계정에 옛 이름의 레포를 새로 만들지 않는 동안 유지된다.

## 검증

- `gh repo view Gruci/web-harness` 와 `git ls-remote origin` 이 exit 0.
- 옛 이름 grep 이 `docs/tasks/` 밖에서 0건. 영수증의 로컬 절대경로는 폴더명이라 범위 밖이다.
- `tests/` 에서 `python -X utf8 -m unittest test_release_identity test_harness_setup` 통과. 이 환경에는 pytest 가 없다.
- `python -X utf8 harness_install.py --check-update` 가 새 주소에서 버전을 읽는다.
- `python -X utf8 -m kernel.runner` 통과. 검사 48 포함.

## Todo

- [x] 과업 파일 등록
- [x] 1 레포 개명과 origin
- [x] 2~6 편집과 커밋
- [x] 7 그림 재생성과 커밋
- [x] 검증
- [x] archive·push·과업 파일 삭제

## 결과

검증 5건 모두 exit 0. 그림 4장은 9/9 showcase·오류 0·경고 0, revision `e3735f3`. 렌더 HTML 확인: 안 봤음.
