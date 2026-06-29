"""Validate a SKILL.md against Anthropic Agent Skills standard.

Usage:
    python validate_skill.py path/to/SKILL.md
    python validate_skill.py path/to/skill-dir/   # auto-finds SKILL.md inside

Exit codes:
    0  PASS  (or PASS with WARN — not blocking)
    1  FAIL  (blocking issues — must fix before publish)
    2  File not found / parse error

Output levels:
    PASS   all 8 checks OK
    WARN   some advisory issues, but publishable
    FAIL   blocking issues, do NOT publish
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml  # PyYAML; install via `pip install pyyaml`


# ---------- constants ----------

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
DESCRIPTION_MIN_LEN = 80  # heuristic: a real 5-element description is rarely shorter
NEGATIVE_BOUNDARY = re.compile(r"不适用|不用于|not.{0,3}for|not.{0,3}applicable", re.IGNORECASE)
TRIGGER_KEYWORDS = re.compile(r"关键词|keywords|trigger|提到|提及|mention", re.IGNORECASE)

REQUIRED_SECTIONS = [
    "核心能力",
    "关键规则",
    "必须遵守",
    "禁止",
    "工作流程",
]

OPTIONAL_SECTIONS = ["使用示例", "注意事项", "参考资源"]


# ---------- helpers ----------

def split_frontmatter(text: str) -> tuple[dict, str, str]:
    """Split a SKILL.md into (frontmatter_dict, body_markdown, raw_frontmatter_text)."""
    if not text.startswith("---"):
        return {}, text, ""
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text, ""
    fm_raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"YAML frontmatter parse error: {e}") from e
    if not isinstance(fm, dict):
        raise ValueError("YAML frontmatter must be a mapping")
    return fm, body, fm_raw


def check_name(name: object) -> list[str]:
    errs = []
    if not name:
        errs.append("name 字段缺失")
        return errs
    if not isinstance(name, str):
        errs.append(f"name 必须是字符串,当前是 {type(name).__name__}")
        return errs
    if not NAME_PATTERN.match(name):
        errs.append(
            f"name 字段格式错误: '{name}'(必须小写字母+数字+连字符,以字母开头,正则: ^[a-z][a-z0-9-]*$)"
        )
    if len(name) > 64:
        errs.append(f"name 字段过长 ({len(name)} > 64)")
    return errs


def check_description(desc: object) -> list[str]:
    errs = []
    warns = []
    if not desc:
        errs.append("description 字段缺失(5 要素中最关键的一个)")
        return errs, warns
    if not isinstance(desc, str):
        errs.append("description 必须是字符串")
        return errs, warns
    if len(desc) < DESCRIPTION_MIN_LEN:
        errs.append(
            f"description 过短 ({len(desc)} < {DESCRIPTION_MIN_LEN}),"
            " 5 要素通常需要 80+ 字符"
        )
    # check 5 elements
    if not NEGATIVE_BOUNDARY.search(desc):
        errs.append(
            "description 缺少「否定边界」(必须包含「不适用」「不用于」"
            " 或 'not for' / 'not applicable')"
        )
    if not TRIGGER_KEYWORDS.search(desc):
        warns.append(
            "description 缺少「触发关键词」提示"
            "(建议加「关键词」「提到」「mention」等词帮助 AI 匹配)"
        )
    if desc.count("。") + desc.count(".") < 3:
        warns.append("description 句子过少,可能不够具体(建议 3 句以上)")
    return errs, warns


def check_license(lc: object) -> list[str]:
    warns = []
    if not lc:
        warns.append("license 字段缺失(推荐 Apache 2.0 / MIT)")
    elif not isinstance(lc, str):
        warns.append("license 字段不是字符串")
    return warns


def check_body(body: str) -> tuple[list[str], list[str]]:
    errs = []
    warns = []
    for sec in REQUIRED_SECTIONS:
        if sec not in body:
            errs.append(f"Markdown 缺少「{sec}」章节")
    has_any_optional = any(sec in body for sec in OPTIONAL_SECTIONS)
    if not has_any_optional:
        warns.append(
            "Markdown 缺少任一可选章节(使用示例 / 注意事项 / 参考资源),"
            " 可读性会下降"
        )
    if len(body) < 400:
        errs.append(f"Markdown 主体过短 ({len(body)} < 400 字符),内容不够充实")
    return errs, warns


def has_triggers_field(fm_raw: str) -> tuple[bool, list[str]]:
    """Warn (don't fail) if `triggers:` field present — breaks portability."""
    warns = []
    has = bool(re.search(r"^triggers\s*:", fm_raw, re.MULTILINE))
    if has:
        warns.append(
            "发现 `triggers:` 字段 — 兼容写法是把它放进 description,"
            " 否则部分平台(OpenAI Codex)会忽略"
        )
    return has, warns


# ---------- main ----------

def validate(path: Path) -> int:
    if not path.exists():
        print(f"[ERROR] file not found: {path}", file=sys.stderr)
        return 2
    if path.is_dir():
        cand = path / "SKILL.md"
        if not cand.exists():
            print(f"[ERROR] no SKILL.md in directory: {path}", file=sys.stderr)
            return 2
        path = cand
    text = path.read_text(encoding="utf-8")
    try:
        fm, body, fm_raw = split_frontmatter(text)
    except ValueError as e:
        print(f"[FAIL] {e}")
        return 1

    all_errs: list[str] = []
    all_warns: list[str] = []

    # name
    all_errs.extend(check_name(fm.get("name")))
    # description
    e, w = check_description(fm.get("description"))
    all_errs.extend(e)
    all_warns.extend(w)
    # license
    all_warns.extend(check_license(fm.get("license")))
    # triggers
    _, w = has_triggers_field(fm_raw)
    all_warns.extend(w)
    # body
    e, w = check_body(body)
    all_errs.extend(e)
    all_warns.extend(w)

    total = 8
    passed = total - len(all_errs)
    print(f"\n{'=' * 50}")
    print(f"  SKILL.md validation report: {path}")
    print(f"{'=' * 50}\n")

    if all_errs:
        print(f"[FAIL] {passed}/{total} — {len(all_errs)} 阻塞项\n")
        for i, e in enumerate(all_errs, 1):
            print(f"  ❌ [{i}] {e}")
        print()
        if all_warns:
            print(f"另外 {len(all_warns)} 条 WARN(非阻塞):")
            for w in all_warns:
                print(f"  ⚠  {w}")
        print("\n请修复 FAIL 项后重跑,所有阻塞项归零才能发布。")
        return 1

    if all_warns:
        print(f"[WARN] {passed}/{total} — 通过但有 {len(all_warns)} 条建议\n")
        for w in all_warns:
            print(f"  ⚠  {w}")
        print("\nWARN 不阻塞发布,但建议优化。")
        return 0

    print(f"[PASS] {passed}/{total} ✓\n")
    print(f"  name:        {fm.get('name')} ✓")
    print(f"  description: 5 要素完整 ✓")
    print(f"  license:     {fm.get('license', '(未设置)')} ✓")
    print(f"  Markdown 结构完整 ✓\n")
    print("可以进入发布流程:bash scripts/init_and_publish.sh")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python validate_skill.py <SKILL.md|dir>", file=sys.stderr)
        return 2
    return validate(Path(argv[1]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))