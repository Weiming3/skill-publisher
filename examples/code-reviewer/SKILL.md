---
name: code-reviewer
description: "当用户需要对代码进行系统化审查和重构建议时使用此 skill。包括检查安全性(SQL 注入 / XSS / 硬编码密钥)、可读性(命名 / 复杂度 / 注释)、性能(N+1 查询 / 大循环重操作)、错误处理(边界 / 异常 / 资源释放),并给出按优先级排序的修复建议。审查 Python / JavaScript / TypeScript / Java / Go / Rust / C++ 等主流语言。当用户提到「代码审查」「code review」「check code」「代码质量」「找 bug」「优化代码」「重构」「security check」「安全检查」等关键词时使用。不适用于:(1) 单纯写代码或编程问题解答(用通用编程 skill);(2) 单元测试生成(用 unit-test-generator);(3) 代码格式化 / linting(用专门的 formatter skill)。"
license: Apache 2.0
---

# Code Reviewer

> **示例**:可直接复制 `templates/code-reviewer.md` 到 `examples/code-reviewer/SKILL.md`

这是 skill-publisher 仓库的**完整可发布示例**。

## 安装

```bash
mavis skill install https://github.com/Weiming3/code-reviewer
# 或
npx skills add Weiming3/code-reviewer
```

## 使用

触发关键词:`代码审查` / `code review` / `找 bug` / `重构` 等。

详见 `templates/code-reviewer.md` 完整版本(包含核心能力 / 关键规则 / 工作流程 / 使用示例)。

## License

Apache 2.0