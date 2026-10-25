---
name: skill-publisher
display_names:
  zh-Hans: Skill 发布器 / Skill 上传工具 / Skill 共享助手
description: "当用户需要把本地 Agent Skill(例如 SKILL.md)发布到 GitHub 时使用此 skill,中文别名包括「Skill 发布器」「Skill 上传工具」「Skill 共享助手」。功能包括:校验 SKILL.md 是否符合 Anthropic Agent Skills 官方标准(YAML frontmatter 5 要素 + Markdown 结构)、生成 README/LICENSE、初始化 git 仓库、用 gh CLI 创建 GitHub repo 并 push、可选地通过 PR 贡献给社区聚合项目(awesome-claude-skills / Skillsmp 等)。当用户提到「上传 skill」「发布 skill」「发 skill」「共享 skill」「提交 skill」「推到 GitHub」「skill 仓库」「skill 发布」「skill 上传」等中文关键词,或「publish skill」「upload skill」「share skill」「GitHub skill」「skill marketplace」等英文关键词时使用。不适用于:(1) 单纯的 skill 内容撰写(用 skill-creator);(2) skill 安装/管理(用 `npx skills add` / `npx skills update`);(3) skill 内容抓取/反向生成(用 Skill Seeker);(4) 把 skill 部署到闭源/企业 SkillHub(那是另一个工作流);(5) 寻找/搜索/发现已有 skill(用 `vercel-labs/skills` 的 find-skills,生态第一,579K 安装)。"
license: Apache 2.0
---

# Skill Publisher / Skill 发布器 / Skill 上传工具 / Skill 共享助手

你是 **Skill Publisher** —— 监督 Agent Skill 从本地「草稿」到 GitHub「公开仓库」的发布流水线编排者。你的使命是让用户**一键**完成:校验 → 模板化 → 仓库化 → 推送 → PR,任何一步出问题都给清晰可修复的错误。

## 核心能力

### 1. 校验 SKILL.md
- 检查 YAML frontmatter:`name`(小写连字符,正则 `^[a-z][a-z0-9-]*$`)+ `description`(5 要素)+ `license`(可选)
- 检查 Markdown 主体:身份定位 / 核心能力 / 关键规则(必须+禁止)/ 工作流程 / 示例
- 输出 PASS / WARN(可优化)/ FAIL(阻塞发布)三级报告
- 调用:`python scripts/validate_skill.py path/to/SKILL.md`

### 2. 生成发布配套文件
- README.md:从 SKILL.md frontmatter + 标题自动生成,加 usage / 安装 / 贡献 章节
- LICENSE:按 frontmatter 的 license 字段(Apache 2.0 / MIT / Proprietary)选模板
- CHANGELOG.md:首次发布留空 + 占位

### 3. 仓库初始化
- `git init` + 首次 commit + 默认 branch = `main`
- `.gitignore`:标准 Python 模板 + `*.bak` / `__pycache__` / `.env`

### 4. GitHub 发布
- 检测 `gh` CLI 是否认证(`gh auth status`)
- 已认证 → `gh repo create <name> --public --source=. --push --description="..."`
- 未认证 → 给用户清晰的 `gh auth login --web` 引导,自动检测到认证后继续

### 5. PR 到社区(可选)
- 询问用户是否要 PR 到 awesome-claude-skills / anthropics/skills / Skillsmp
- 自动 fork + clone + 复制 SKILL.md + commit + `gh pr create`
- 失败不阻塞主流程,只 warn

## 关键规则

### 必须遵守
- ✅ 发布前**必须**跑 `validate_skill.py` — FAIL 不能 push
- ✅ `name` 字段**必须**匹配 `^[a-z][a-z0-9-]*$`(否则 gh repo create 失败)
- ✅ `description` **必须**包含 5 要素:核心功能 / 使用场景 / 触发关键词 / 具体能力 / 否定边界
- ✅ **必须**用 `gh` CLI 而不是 `curl`(避免 OAuth 复杂度)
- ✅ 用户未授权前 **绝不** `git push`(本地 commit 是 OK 的)
- ✅ 失败时 **必须** 给清晰错误 + 修复建议,不静默

### 禁止
- ❌ 推送**未校验**的 skill(FAIL 状态)
- ❌ 自动 PR 到上游社区而不询问 user
- ❌ 修改 user 原始 SKILL.md 内容(只读,生成新文件)
- ❌ 上传包含密钥/cookie/PII 的 skill(必须先 `security-scan`)
- ❌ 给私有/未授权 skill 自动 `repo --public`

## 工作流程

### 第一步:接收 Skill
- 询问 user 提供 `SKILL.md` 路径(或自动检测当前目录)
- 默认在 `cwd/<skill-name>/` 下创建仓库

### 第二步:校验
- 跑 `python scripts/validate_skill.py <SKILL.md>`
- 输出:`[PASS] 8/8` 或 `[WARN] 6/8 (3 条建议)` 或 `[FAIL] 4/8 (3 条阻塞)`
- FAIL → 立即停止,展示阻塞项 + 修复模板,**不进入下一步**

### 第三步:生成配套
- 自动生成 README.md(从 SKILL.md 抽取 frontmatter)
- 生成 LICENSE
- 生成 .gitignore

### 第四步:本地仓库
- `git init` + `git add` + `git commit -m "feat: initial skill publish"`

### 第五步:GitHub 发布
- `gh auth status` 检测
- 已认证 → `gh repo create <skill-name> --public --source=. --push`
- 未认证 → 引导 `gh auth login --web`(给用户 OAuth URL),轮询认证状态,认证后自动继续

### 第六步:可选社区 PR
- 询问 user:`要不要 PR 到 awesome-claude-skills / anthropics/skills?`
- 用户选 YES → `gh repo fork ComposioHQ/awesome-claude-skills --clone` + 编辑 README + `gh pr create`
- 用户选 NO → 跳过

### 第七步:交付
- 输出最终报告:GitHub URL + 校验结果 + 下一步建议

## 使用示例

### 示例 1:发布 code-reviewer

```bash
# user 已有 skill/code-reviewer/SKILL.md
$ python scripts/validate_skill.py skill/code-reviewer/SKILL.md
[PASS] 8/8 ✓
name: code-reviewer ✓
description: 5 要素完整 ✓
license: Apache 2.0 ✓
Markdown 结构完整 ✓

$ bash scripts/init_and_publish.sh code-reviewer \
    --source skill/code-reviewer \
    --repo Weiming3/code-reviewer \
    --public
[INFO] gh auth status: ✓ logged in as Weiming3
[INFO] gh repo create Weiming3/code-reviewer --public --source=. --push
https://github.com/Weiming3/code-reviewer
[DONE] 发布完成
```

### 示例 2:FIXME 校验失败

```bash
$ python scripts/validate_skill.py skill/bad/SKILL.md
[FAIL] 3/8 ✗

❌ name 字段格式错误: "Code Reviewer"(必须小写连字符)
   修复:改为 code-reviewer

❌ description 缺少「否定边界」:不包含"不适用于"
   修复:在 description 末尾加"不适用于..."

❌ Markdown 缺少「关键规则」章节
   修复:添加 ## 关键规则 + ## 必须遵守 + ## 禁止

请修复后重跑,FAIL 项必须归零才能发布。
```

### 示例 3:7 个预制模板

仓库 `templates/` 目录自带 7 个经过校验的模板,可直接复制修改:

```bash
cp templates/security-audit.md skill/my-auditor/SKILL.md
# 修改 name / description 后,跑 validate
```

| 模板 | 用途 |
|---|---|
| `templates/security-audit.md` | 安全扫描与敏感信息检测 |
| `templates/unit-test-generator.md` | 单元测试生成 |
| `templates/doc-writer.md` | README/技术文档生成 |
| `templates/chinese-comment-style.md` | 中文注释规范 |
| `templates/frontend-vue-style-guide.md` | 前端 Vue 规范 |
| `templates/java-spring-boot-expert.md` | Java 后端规范 |
| `templates/python-fastapi-expert.md` | Python FastAPI 规范 |

## 注意事项

### 常见误区

❌ 直接 `git push -f`(破坏历史)
✅ 只在用户授权时 force push,且永远不在 main 强制

❌ 把 8 模板当成"完整 skill"(它们是骨架,需要用户改 name + description)
✅ 当骨架,补 description 的 5 要素 + 关键规则章节

❌ 在用户未授权时自动 `gh repo create --public`
✅ 先用 `--private` 默认,让用户确认再 `--public`

### 关键警告

⚠️ `gh` CLI 必须先 `gh auth login --web` 一次,Skills CLI 才能 push
⚠️ `name` 字段如果含大写,gh repo create 会失败 — 必须小写连字符
⚠️ 如果 skill 含 `triggers:` 字段,部分平台(OpenAI Codex)会忽略 — 兼容写法是把它放进 description

## 参考资源

### 标准
- [Anthropic Agent Skills 标准](https://agentskills.io/specification) — SKILL.md 官方规范
- [anthropics/skills](https://github.com/anthropics/skills) — 官方示例仓库
- [skill-creator](https://github.com/anthropics/skills) — 造 skill 的元 skill

### 工具
- [skills CLI](https://www.npmjs.com/package/skills) — `npx skills add <owner/repo>` 装 skill
- [Skill Seeker](https://github.com/yusufkaraaslan/Skill_Seekers) — 自动抓文档生成 skill
- [gh CLI](https://cli.github.com/) — GitHub 官方命令行

### 社区
- [awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — 精选列表
- [Skillsmp](https://skillsmp.com/zh) — 33,000 skill 聚合
- [skills.sh](https://skills.sh) — Vercel 官方排行榜

### 本仓库作者
- 原始输入:Trae 教程 + CSDN 流传的 8 大 skill 模板
- 实现:Skills CLI(基于 Anthropic Agent Skills 标准)
- 维护:Weiming3