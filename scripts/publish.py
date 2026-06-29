"""Publish a local Skill to GitHub.

Workflow:
    1. validate SKILL.md (blocking)
    2. generate README.md + LICENSE from frontmatter
    3. git init + commit
    4. gh repo create + push (interactive confirmation before push)
    5. optional: PR to community (awesome-claude-skills etc.)

Usage:
    python publish.py --name code-reviewer --source ./my-skill --visibility public
    python publish.py --name code-reviewer --source ./my-skill --dry-run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml  # PyYAML


LICENSE_TEMPLATES = {
    "Apache 2.0": "Apache License 2.0 — full text at https://www.apache.org/licenses/LICENSE-2.0.txt",
    "MIT": "MIT License — full text at https://opensource.org/licenses/MIT",
    "Proprietary": "All rights reserved.",
    "Apache-2.0": "Apache License 2.0 — full text at https://www.apache.org/licenses/LICENSE-2.0.txt",
    "MIT License": "MIT License — full text at https://opensource.org/licenses/MIT",
}

GITIGNORE_TEMPLATE = """\
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/

# Editor / OS
.vscode/
.idea/
.DS_Store
Thumbs.db

# Secrets
.env
*.bak
"""


# ---------- helpers ----------

def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess, print output, raise on error."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def check_gh_auth() -> tuple[bool, str]:
    """Return (is_authenticated, username)."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        return False, ""
    if result.returncode != 0:
        return False, ""
    for line in result.stdout.splitlines() + result.stderr.splitlines():
        if "Logged in to" in line and " as " in line:
            user = line.split(" as ", 1)[1].split("(")[0].strip()
            return True, user
    return True, ""


def prompt_continue(msg: str) -> bool:
    """Interactive yes/no prompt."""
    try:
        ans = input(f"\n{msg} [y/N]: ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes")


# ---------- generators ----------

def read_skill_md(skill_md: Path) -> tuple[dict, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("SKILL.md missing YAML frontmatter")
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("SKILL.md frontmatter not closed")
    fm = yaml.safe_load(text[3:end]) or {}
    body = text[end + 4 :].lstrip("\n")
    if not isinstance(fm, dict):
        raise ValueError("frontmatter must be a mapping")
    return fm, body


def generate_readme(fm: dict, body: str) -> str:
    name = fm.get("name", "unknown")
    desc = fm.get("description", "").strip()
    license_ = fm.get("license", "未指定")
    body_extract = body.split("## 使用示例", 1)[0] if "## 使用示例" in body else body[:500]
    return f"""# {name}

{desc}

## 安装

### 通过 `mavis skill install`(Mavis)
```bash
mavis skill install https://github.com/<owner>/{name}
```

### 通过 `npx skills add`(Claude Code / Codex / Cursor)
```bash
npx skills add <owner>/{name}
```

### 手动安装
把 `{name}/SKILL.md` 复制到对应平台:
- Claude Code: `~/.claude/skills/{name}/SKILL.md`
- Mavis: `~/.mavis/agents/<your-agent>/skills/{name}/SKILL.md`
- Codex: `~/.codex/skills/{name}/SKILL.md`

## 使用

{body_extract}

## License

{license_}

## 由 Skill Publisher 自动生成

本仓库通过 [skill-publisher](https://github.com/Weiming3/skill-publisher) 自动发布。
"""


def generate_license(lc: str) -> str:
    note = LICENSE_TEMPLATES.get(lc, f"License: {lc}")
    return f"""# License

{note}

(完整 LICENSE 文本应由 maintainer 在首次发布前补充)
"""


# ---------- main workflow ----------

def publish(
    name: str,
    source: Path,
    owner: str,
    visibility: str,
    dry_run: bool,
    community_pr: bool,
) -> int:
    """Run the full publish pipeline."""
    skill_md = source / "SKILL.md" if source.is_dir() else source
    if not skill_md.exists():
        print(f"[ERROR] SKILL.md not found at {skill_md}", file=sys.stderr)
        return 2

    work_dir = source if source.is_dir() else source.parent

    print(f"\n{'=' * 60}")
    print(f"  Skill Publisher: {name}")
    print(f"  source:   {source}")
    print(f"  owner:    {owner}")
    print(f"  visibility: {visibility}")
    print(f"{'=' * 60}\n")

    # 1. validate
    print("[1/5] 校验 SKILL.md ...")
    val_result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "validate_skill.py"), str(skill_md)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    print(val_result.stdout)
    if val_result.returncode != 0:
        print("[ABORT] 校验未通过,禁止发布")
        return 1

    # 2. generate companion files
    print("\n[2/5] 生成 README / LICENSE / .gitignore ...")
    fm, body = read_skill_md(skill_md)
    readme = work_dir / "README.md"
    license_file = work_dir / "LICENSE"
    gitignore = work_dir / ".gitignore"

    if not dry_run:
        readme.write_text(generate_readme(fm, body), encoding="utf-8")
        license_file.write_text(generate_license(fm.get("license", "未指定")), encoding="utf-8")
        gitignore.write_text(GITIGNORE_TEMPLATE, encoding="utf-8")
        print(f"  ✓ {readme}")
        print(f"  ✓ {license_file}")
        print(f"  ✓ {gitignore}")
    else:
        print("  (dry-run: skipped)")

    # 3. git init + commit
    print("\n[3/5] git init + commit ...")
    if not dry_run:
        if not (work_dir / ".git").exists():
            run(["git", "init", "-b", "main"], cwd=work_dir)
        run(["git", "add", "."], cwd=work_dir)
        run(
            ["git", "commit", "-m", f"feat: initial skill publish for {name}"],
            cwd=work_dir,
        )
    else:
        print("  (dry-run: skipped)")

    # 4. gh auth + push
    print(f"\n[4/5] GitHub: gh repo create + push ({visibility}) ...")
    is_auth, user = check_gh_auth()
    if not is_auth:
        print("[ABORT] gh CLI 未认证")
        print("  请先在 terminal 跑:")
        print("    gh auth login --web")
        print("  然后重跑本脚本。")
        return 3

    print(f"  ✓ gh auth: {user}")
    repo_full = f"{owner}/{name}"
    if not dry_run:
        if not prompt_continue(f"  准备创建 {repo_full}({visibility})并 push,继续吗?"):
            print("  用户取消")
            return 0
        run(
            [
                "gh",
                "repo",
                "create",
                repo_full,
                f"--{visibility}",
                "--source=.",
                "--push",
                f"--description={fm.get('description', name)[:100]}",
            ],
            cwd=work_dir,
        )
        print(f"\n  ✓ https://github.com/{repo_full}")
    else:
        print("  (dry-run: skipped)")

    # 5. optional community PR
    print(f"\n[5/5] 社区 PR(可选) ...")
    if community_pr and not dry_run:
        if prompt_continue("  PR 到 awesome-claude-skills / anthropics/skills?"):
            print("  (TODO: implement community PR workflow)")
            print("  见 https://github.com/ComposioHQ/awesome-claude-skills#contributing")
        else:
            print("  跳过")

    print(f"\n{'=' * 60}")
    print(f"  ✓ 发布完成: https://github.com/{repo_full}")
    print(f"{'=' * 60}\n")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Publish a Skill to GitHub.")
    p.add_argument("--name", required=True, help="skill name (must match SKILL.md frontmatter)")
    p.add_argument("--source", required=True, type=Path, help="path to SKILL.md or skill dir")
    p.add_argument("--owner", required=True, help="GitHub owner (user or org)")
    p.add_argument(
        "--visibility",
        choices=["public", "private"],
        default="private",
        help="repo visibility (default: private; public must be explicit)",
    )
    p.add_argument("--dry-run", action="store_true", help="don't write anything or push")
    p.add_argument("--community-pr", action="store_true", help="ask about PR to community repos")
    args = p.parse_args()
    return publish(
        name=args.name,
        source=args.source,
        owner=args.owner,
        visibility=args.visibility,
        dry_run=args.dry_run,
        community_pr=args.community_pr,
    )


if __name__ == "__main__":
    sys.exit(main())