"""Explicit Python binding for this reference only; never a new-app default."""
PROFILE_SCHEMA = 3
LANG = "python"
ARCH = "headless"
LINTERS = ()
CHECK_PATHS = {"tests": "tests"}
STAGE = "greenfield"
HUBS = ("README.md",)
MD = {"doc_exclude": ("docs/architecture/proposals/",), "ref_exclude": (), "style_exclude": (), "date_exempt": ()}
SCOPE = {"exclude_all": (), "exclude_scratch": ()}
