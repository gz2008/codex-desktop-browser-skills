from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
UNFINISHED = re.compile(r"\b(TODO|TBD|FIXME)\b|\[TODO", re.IGNORECASE)
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def validate_frontmatter(skill_dir: Path) -> None:
    path = skill_dir / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path}: missing YAML frontmatter")

    end = text.find("\n---\n", 4)
    if end == -1:
        fail(f"{path}: unterminated YAML frontmatter")

    metadata = yaml.safe_load(text[4:end])
    if not isinstance(metadata, dict):
        fail(f"{path}: frontmatter must be a mapping")
    if metadata.get("name") != skill_dir.name:
        fail(f"{path}: name must match folder {skill_dir.name!r}")
    if not str(metadata.get("description", "")).strip():
        fail(f"{path}: missing description")
    if UNFINISHED.search(text):
        fail(f"{path}: unfinished placeholder found")


def validate_links(skill_dir: Path) -> None:
    for path in skill_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for raw_target in LINK.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = target.split("#", 1)[0]
            if target and not (path.parent / target).resolve().exists():
                fail(f"{path}: broken relative link {raw_target!r}")


def validate_agent_metadata(skill_dir: Path) -> None:
    path = skill_dir / "agents" / "openai.yaml"
    if not path.exists():
        return
    metadata = yaml.safe_load(path.read_text(encoding="utf-8"))
    interface = metadata.get("interface") if isinstance(metadata, dict) else None
    if not isinstance(interface, dict):
        fail(f"{path}: missing interface mapping")
    for key in ("display_name", "short_description"):
        if not str(interface.get(key, "")).strip():
            fail(f"{path}: missing interface.{key}")


def main() -> int:
    if not SKILLS.is_dir():
        fail(f"skills directory not found: {SKILLS}")

    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not skill_dirs:
        fail("no skills found")

    for skill_dir in skill_dirs:
        validate_frontmatter(skill_dir)
        validate_links(skill_dir)
        validate_agent_metadata(skill_dir)
        print(f"OK {skill_dir.name}")

    print(f"Validated {len(skill_dirs)} skill(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
