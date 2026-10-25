# skill-publisher / Skill 发布器 / Skill 上传工具 / Skill 共享助手

> **Meta-skill**:把 Agent Skill 从本地草稿发布到 GitHub 的流水线编排者

**中文别名**:`Skill 发布器` / `Skill 上传工具` / `Skill 共享助手` — 中文用户搜这些关键词也能找到。

**English**: `skill-publisher` / `Skill Publisher` / `agent skill publisher`

`skill-publisher` 是一个**监督 skill 上传 GitHub 的 skill**(meta-skill)。它让你**一键**完成:校验 SKILL.md 格式 → 生成 README/LICENSE → 初始化 git 仓库 → 用 gh CLI 推 GitHub → 可选 PR 到社区聚合。

## 为什么需要它

GitHub 上**已经有 33,000+ Agent Skills**(见 [Skillsmp](https://skillsmp.com))。但生态已经分得很清楚:

| 类别 | 已有项目 | 安装量 | 我们补什么 |
|---|---|---|---|
| 🔍 **Discover** | `vercel-labs/skills` 的 `find-skills` | **579K,生态第一** | — 不重复造轮子 |
| 🛠️ **Create** | `anthropics/skill-creator` | 37K | — 不重复造轮子 |
| 📦 **Install** | `npx skills add`(Vercel) | npm 级别 | — 不重复造轮子 |
| 🛒 **Marketplace** | `skills.sh` / `Skillsmp` / `clawhub.ai` | 流量大 | — 不重复造轮子 |
| 🚀 **Publish**(校验 + README + 推 GitHub) | ❌ **没有** | — | ✅ **唯一空白** |

常见痛点(我们的解药):

- ❌ SKILL.md 写得不规范,Anthropic 标准检查 5 要素没人做
- ❌ 推到 GitHub 后忘了加 README / LICENSE
- ❌ `gh repo create` 失败(因为 `name` 字段有大写)
- ❌ 想 PR 到 awesome-claude-skills 但流程繁琐

**skill-publisher 一键解决**。

## 核心特性

| 特性 | 说明 |
|---|---|
| 🔍 **8 项校验** | YAML frontmatter + 命名 + 5 要素 + Markdown 结构 |
| 📝 **自动生成 README** | 从 SKILL.md frontmatter 抽取,加 install / 使用章节 |
| 📜 **多 license 支持** | Apache 2.0 / MIT / Proprietary 自动选模板 |
| 🚀 **gh CLI 一键 push** | 检测认证 + 交互式确认 + `--public` 必须显式 |
| 🎁 **7 个预制模板** | security-audit / unit-test-generator / chinese-comment-style 等 |
| 🌐 **社区 PR**(可选) | 自动 PR 到 awesome-claude-skills / anthropics/skills |

## 安装

### 通过 `npx skills add`(Claude Code / Codex / Cursor)
```bash
npx skills add Weiming3/skill-publisher
```

### 手动
把 `SKILL.md` 复制到 `~/.claude/skills/skill-publisher/SKILL.md`。

## 使用

### 1. 校验 SKILL.md

```bash
python scripts/validate_skill.py path/to/SKILL.md
```

**输出**:
```
==================================================
  SKILL.md validation report: SKILL.md
==================================================

[PASS] 8/8 ✓

  name:        code-reviewer ✓
  description: 5 要素完整 ✓
  license:     Apache 2.0 ✓
  Markdown 结构完整 ✓

可以进入发布流程
```

**FAIL 模式**:
```
[FAIL] 3/8 — 3 阻塞项

  ❌ [1] name 字段格式错误: "Code Reviewer"(必须小写连字符)
  ❌ [2] description 缺少「否定边界」
  ❌ [3] Markdown 缺少「关键规则」章节

请修复 FAIL 项后重跑。
```

### 2. 发布到 GitHub

```bash
python scripts/publish.py \
    --name code-reviewer \
    --source ./my-skill \
    --owner Weiming3 \
    --visibility public
```

**Dry-run**(不实际 push,只校验 + 生成文件):
```bash
python scripts/publish.py --name code-reviewer --source ./my-skill --dry-run
```

### 3. 一键脚本(包装)

```bash
bash scripts/init_and_publish.sh code-reviewer Weiming3 public
```

## 7 个预制模板

仓库 `templates/` 目录包含 **7 个经过校验**的模板,可直接复制修改:

| 模板 | 用途 | 优先级 |
|---|---|---|
| `security-audit.md` | 安全扫描与敏感信息检测 | 🔥 高 |
| `chinese-comment-style.md` | 中文注释规范 | 🔥 高 |
| `unit-test-generator.md` | 单元测试生成 | ⚪ 中 |
| `doc-writer.md` | README/技术文档 | ⚪ 中 |
| `frontend-vue-style-guide.md` | Vue 编码规范 | ⚪ 低(看你的栈) |
| `java-spring-boot-expert.md` | Spring Boot 规范 | ⚪ 低(看你的栈) |
| `python-fastapi-expert.md` | FastAPI 规范 | ⚪ 低(看你的栈) |

**使用模板**:
```bash
cp templates/security-audit.md ./my-auditor/SKILL.md
# 修改 name / description 后,跑 validate
```

## 工作流程

```
┌─────────────┐
│  本地 SKILL.md│
└──────┬──────┘
       ↓
┌─────────────────────┐
│  validate_skill.py │  ← 8 项校验,FAIL 不让走
└──────┬──────────────┘
       ↓ PASS
┌──────────────────────┐
│  生成 README/LICENSE│
└──────┬───────────────┘
       ↓
┌────────────────────┐
│  git init + commit │
└──────┬─────────────┘
       ↓
┌──────────────────────────┐
│  gh auth status 检查     │  ← 未认证 → 引导 `gh auth login --web`
└──────┬───────────────────┘
       ↓ 已认证
┌──────────────────────────────┐
│  gh repo create --public     │  ← 交互式确认 + 默认 private 必须显式 public
│  --source=. --push           │
└──────┬───────────────────────┘
       ↓
┌────────────────────────────┐
│  可选: PR 到 awesome-claude-skills │
└────────────────────────────┘
```

## 校验规则(8 项)

1. **`name` 字段**:`^[a-z][a-z0-9-]*$`,小写连字符
2. **`description` 长度**:`>= 80` 字符(过短通常是 5 要素不全)
3. **`description` 含否定边界**:必须包含"不适用" / "不用于" / "not for"
4. **`description` 含触发关键词**:含"关键词" / "提到" / "mention" 之类
5. **`license` 字段**:推荐 Apache 2.0 / MIT
6. **无 `triggers:` 字段**(否则 OpenAI Codex 忽略,放 description 里)
7. **Markdown 结构**:`核心能力` / `关键规则` / `必须遵守` / `禁止` / `工作流程` 章节齐全
8. **Markdown 长度**:`>= 400` 字符

## 项目结构

```
skill-publisher/
├── SKILL.md                      # skill 自己的描述(Anthropic 标准)
├── README.md                     # 本文件
├── LICENSE                       # Apache 2.0
├── .gitignore
├── scripts/
│   ├── validate_skill.py         # 8 项校验
│   ├── publish.py                # 完整发布流程
│   └── init_and_publish.sh       # 一键脚本
├── templates/                    # 7 个预制模板
│   ├── security-audit.md
│   ├── unit-test-generator.md
│   ├── doc-writer.md
│   ├── chinese-comment-style.md
│   ├── frontend-vue-style-guide.md
│   ├── java-spring-boot-expert.md
│   └── python-fastapi-expert.md
└── examples/                     # 完整可发布的 skill 示例
    ├── code-reviewer/
    └── security-audit/
```

## 依赖

- Python 3.8+
- `pyyaml`:`pip install pyyaml`
- `gh` CLI:[安装](https://cli.github.com/)

## 相关项目

- [Anthropic Agent Skills 标准](https://agentskills.io/specification) — SKILL.md 规范
- [anthropics/skills](https://github.com/anthropics/skills) — 官方示例
- [skill-creator](https://github.com/anthropics/skills) — 造 skill 的元 skill
- [skills CLI](https://www.npmjs.com/package/skills) — 装/管 skill
- [Skill Seeker](https://github.com/yusufkaraaslan/Skill_Seekers) — 抓文档转 skill
- [awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — 精选列表
- [Skillsmp](https://skillsmp.com/zh) — 33,000 skill 聚合

## License

Apache 2.0

## 由谁维护

Weiming3 — 按 Anthropic Agent Skills 标准构建。

原始输入:Trae 教程 + CSDN 流传的 8 大 skill 模板。
