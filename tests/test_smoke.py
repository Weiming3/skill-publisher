#!/usr/bin/env python3
"""skill-publisher 离线冒烟测试：不依赖网络。"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VALIDATE = os.path.join(ROOT, "scripts", "validate_skill.py")
PUBLISH = os.path.join(ROOT, "scripts", "publish.py")
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS " if cond else "  FAIL ") + name + ((" :: " + str(detail)[:300]) if detail and not cond else ""))


def run(args, cwd=ROOT):
    return subprocess.run([sys.executable] + args, capture_output=True, encoding="utf-8",
                          errors="replace", timeout=120, cwd=cwd)


def main():
    r = run([VALIDATE, "--help"])
    check("validate --help exit=0", r.returncode == 0, r.stderr)
    check("validate --help 有 Usage", "usage" in (r.stdout or "").lower(), r.stdout[:200])

    r = run([VALIDATE])
    check("validate 无参数 exit=2", r.returncode == 2, r.returncode)

    templates = sorted(
        os.path.join(ROOT, "templates", f)
        for f in os.listdir(os.path.join(ROOT, "templates"))
        if f.endswith(".md")
    )
    check("templates 数量为 7", len(templates) == 7, len(templates))
    bad = []
    for p in templates:
        rr = run([VALIDATE, p])
        if rr.returncode != 0:
            bad.append((os.path.basename(p), rr.returncode))
    check("7 个模板全部通过校验", not bad, bad)

    tmp = tempfile.mkdtemp(prefix="pub-smoke-")
    broken = os.path.join(tmp, "SKILL.md")
    with open(broken, "w", encoding="utf-8") as f:
        f.write("# not a skill\n")
    r = run([VALIDATE, broken])
    check("残缺 skill 被判 FAIL(exit=1)", r.returncode == 1, r.returncode)

    r = run([VALIDATE, os.path.join(tmp, "nope.md")])
    check("不存在的文件 exit=2", r.returncode == 2, r.returncode)

    r = run([PUBLISH, "--help"])
    check("publish --help exit=0", r.returncode == 0, r.stderr)

    for script in (VALIDATE, PUBLISH):
        rr = run(["-m", "py_compile", script])
        check("py_compile " + os.path.basename(script), rr.returncode == 0, rr.stderr)

    stale = []
    for name in ("README.md", "SKILL.md", "scripts/publish.py"):
        p = os.path.join(ROOT, *name.split("/"))
        txt = open(p, encoding="utf-8").read()
        if "mavis" in txt.lower():
            stale.append(name)
    check("文档里不再出现 mavis", not stale, stale)

    print("\n%d passed, %d failed" % (len(PASS), len(FAIL)))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
