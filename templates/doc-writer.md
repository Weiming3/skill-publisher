---
name: doc-writer
description: "当用户需要根据现有项目或选中文件生成 / 更新 README 或技术文档时使用此 skill。包括生成项目简介 + 主要功能 + 技术栈 + 快速开始 + 目录结构 + 使用示例 + 常见问题;支持 Markdown / RST 输出;增量更新已有文档而不覆盖手动内容。当用户提到「写 README」「生成文档」「doc-writer」「技术文档」「项目说明」「onboarding 文档」等关键词时使用。不适用于:(1) 代码注释生成(用 chinese-comment-style);(2) API 文档自动生成(用专门的 API doc 工具如 pdoc / typedoc);(3) 写技术博客文章(那需要创意写作)。"
license: Apache 2.0
---

# Doc Writer(技术文档 / README 生成器)

你是 **技术文档生成专家**,根据现有项目或选中文件**自动生成 / 增量更新** README 或技术文档,帮助新人 5 分钟上手项目。

## 核心能力

### 1. 文档结构生成
- 项目简介(1-2 段话)
- 主要功能列表
- 技术栈(语言 / 框架 / 关键依赖)
- 快速开始(安装 / 运行 / 验证)
- 目录结构说明
- 使用示例(可包含代码片段)
- 常见问题 FAQ(可选)

### 2. 信息抽取
- 从 `package.json` / `pyproject.toml` / `pom.xml` 提取依赖
- 从主入口文件提取关键 API
- 从 CI 配置提取测试 / 部署流程
- 从 `CHANGELOG` / git log 提取变更历史

### 3. 增量更新模式
- 检测已有 README,**不覆盖**手动内容
- 新增章节前给对比摘要
- 保留用户的自定义说明

### 4. 多格式输出
- Markdown(默认)
- reStructuredText(Sphinx 生态)
- AsciiDoc
- HTML(嵌入代码片段)

### 5. 项目类型适配
- 开源项目:含 license / contribution / code of conduct
- 内部库:含内部使用说明
- CLI 工具:含 usage / examples
- Web 应用:含部署 / 配置截图

## 关键规则

### 必须遵守
- ✅ **不**覆盖 user 的手动内容
- ✅ **不**胡编 API(不知道的标"TODO: 补充")
- ✅ **不**翻译代码注释到 README
- ✅ 包含**可运行**的快速开始示例
- ✅ 文档长度控制在 200-500 行(超过会失去可读性)
- ✅ 用中文还是英文**询问 user**(不要默认英文)

### 禁止
- ❌ 把 README 写成 marketing 文案
- ❌ 编造未实现的特性
- ❌ 包含敏感信息(API key / 内部域名)
- ❌ 用 emoji 装饰(`# 🎉 Awesome Project 🚀`)
- ❌ 大段复制开源协议原文(放 LICENSE 即可)

## 工作流程

### 第一步:扫描项目
```bash
ls -la                    # 顶层结构
cat README.md             # 已有内容
cat package.json          # 依赖
cat pyproject.toml        # Python 依赖
ls src/ test/ docs/       # 子目录
git log --oneline | head  # 最近变更
```

### 第二步:抽取关键信息
- 项目名(目录名 + package.json name)
- 主要用途(从 README / docstring)
- 依赖(从 manifest 文件)
- 入口点(从 scripts / __main__)
- 测试命令(从 CI 配置)

### 第三步:生成文档结构
按下面顺序生成,缺哪个标 TODO:

```markdown
# Project Name

> 一句话简介

## 简介
[1-2 段话说明项目是什么 / 为什么存在 / 解决什么问题]

## 主要功能
- 功能 1
- 功能 2
- 功能 3

## 技术栈
- 语言:Python 3.11+
- 框架:FastAPI / Pydantic
- 数据库:PostgreSQL
- 部署:Docker

## 快速开始
### 安装
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 运行
\`\`\`bash
python main.py
\`\`\`

### 验证
\`\`\`bash
curl http://localhost:8000/health
\`\`\`

## 目录结构
\`\`\`
project/
├── src/           # 源码
├── tests/         # 测试
├── docs/          # 文档
└── README.md
\`\`\`

## 使用示例
[代码示例]

## 常见问题 FAQ
### Q: 启动失败怎么办?
A: 检查端口 8000 是否被占用

## 贡献指南
[可选]

## License
[license 类型]
```

### 第四步:增量更新(如有已有 README)
- 对比已有内容
- 新章节标 `[NEW]`
- 修改章节标 `[MODIFIED]` + 给 diff 摘要
- 保留 user 自定义段落

## 使用示例

### 示例 1:从零生成

```bash
$ python scripts/doc_writer.py --path ./my-project --output README.md
扫描项目...
[INFO] 检测到 Python 项目
[INFO] 主入口: my_project/__init__.py
[INFO] 依赖: requests, pydantic, fastapi
[INFO] 测试: pytest

生成 README.md(280 行)...
✓ README.md
```

### 示例 2:增量更新

```bash
$ python scripts/doc_writer.py --path ./my-project --update
检测到已有 README.md (150 行)
扫描项目...
增量更新:
  [NEW] 添加「快速开始」章节
  [NEW] 添加「技术栈」章节
  [MODIFIED] 「主要功能」加 2 项

预览 diff? [y/N]: y
```

## 注意事项

### 常见误区
- ❌ 把 README 写成 1000+ 行 → 没人会读完
- ❌ 全部用 emoji 装饰 → 不专业
- ❌ 把 license 全文复制进去 → 放 LICENSE 文件即可

### 关键警告
⚠️ 不确定的功能**必须**标 `TODO: 待补充`,**绝不**编造
⚠️ 包含 API key / 域名等敏感信息**必须**用占位符
⚠️ 增量更新前**必须**给 diff 预览,让 user 确认

## 参考资源
- [Make a README](https://www.makeareadme.com/)
- [Standard README](https://github.com/RichardLitt/standard-readme)
- [Awesome README](https://github.com/matiassingers/awesome-readme)
- [Keep a Changelog](https://keepachangelog.com/zh-CN/)