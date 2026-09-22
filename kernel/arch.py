"""kernel/arch.py — 아키텍처팩 로더.

아키텍처 하나를 늘리는 비용을 **데이터 파일 하나**로 만든다. `kernel/lang.py` 와 같은
골격이고, 선언은 하나뿐이다.

  NOT_APPLICABLE   이 아키텍처에서는 규칙 자체가 성립하지 않는 게이트와 그 사유

언어팩과 나뉘는 선: 언어팩은 "검사기가 그 언어를 이해하는 방법"이고, 아키텍처팩은
"이 프로젝트 형태에 어떤 레이어가 존재하는가"다. 화면 없는 서비스의 UI 게이트가
[SKIP](설정을 안 채움)이 아니라 [N/A](채울 것이 없음)로 찍히게 하는 것이 존재 이유다.

실물은 `kernel/archs/<이름>.py` 이고, 프로파일의 `ARCH` 가 어느 것을 쓸지 정한다.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any

from kernel.context import ROOT

SHIPPED_DIR = Path(__file__).resolve().parent / "archs"
PROJECT_DIR = "profiles/arch"

DEFAULTS: dict[str, Any] = {"NOT_APPLICABLE": {}}


def pack_path(name: str) -> Path | None:
    """이 아키텍처팩의 실물. 프로젝트 것이 커널 것을 이긴다."""
    if not isinstance(name, str) or not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", name):
        raise ValueError(f"잘못된 아키텍처팩 이름: {name!r}")
    for candidate in (ROOT / PROJECT_DIR / f"{name}.py", SHIPPED_DIR / f"{name}.py"):
        if candidate.is_file():
            return candidate
    return None


def available() -> list[str]:
    names: set[str] = set()
    for directory in (SHIPPED_DIR, ROOT / PROJECT_DIR):
        if directory.is_dir():
            names |= {p.stem for p in directory.glob("*.py") if not p.stem.startswith("_")}
    return sorted(names)


def load(name: str | None) -> dict[str, Any]:
    """선언한 팩은 반드시 읽고 검증한다. 미선언만 기본값을 사용한다."""
    pack: dict[str, Any] = {"NOT_APPLICABLE": {}}
    if name is None:
        return pack
    path = pack_path(name)
    if path is None:
        raise ValueError(f"아키텍처팩을 찾을 수 없음: {name}")
    spec = importlib.util.spec_from_file_location(f"_arch_{name}", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"아키텍처팩 로더를 만들 수 없음: {name}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise ValueError(f"아키텍처팩 로드 실패: {name}: {type(exc).__name__}") from exc
    given = getattr(module, "NOT_APPLICABLE", None)
    if given is not None and not isinstance(given, dict):
        raise ValueError(f"아키텍처팩 NOT_APPLICABLE는 매핑이어야 함: {name}")
    if given:
        pack["NOT_APPLICABLE"] = dict(given)
    return pack
