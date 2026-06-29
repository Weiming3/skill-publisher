---
name: security-audit
description: "当用户需要在代码提交前做安全自查时使用此 skill。包括扫描硬编码密钥 / 密码 / Token / AK-SK、检测 SQL / 命令拼接风险、识别默认账号密码残留、检查敏感日志输出(身份证 / 银行卡 / 手机号打印)、扫描不安全的反序列化 / 弱加密算法。支持 Python / JavaScript / Java / Go 等主流语言。当用户提到「安全扫描」「security audit」「硬编码密钥」「敏感信息泄露」「SQL 注入」「XSS」「安全自查」等关键词时使用。不适用于:(1) 渗透测试(那是 attack 视角);(2) 漏洞修复(用 code-reviewer);(3) 实时入侵检测(那是 WAF / IDS 范畴)。"
license: Apache 2.0
---

# Security Audit

> **示例**:可直接复制 `templates/security-audit.md` 到 `examples/security-audit/SKILL.md`

这是 skill-publisher 仓库的**完整可发布示例**。

## 安装

```bash
mavis skill install https://github.com/Weiming3/security-audit
# 或
npx skills add Weiming3/security-audit
```

## 使用

触发关键词:`安全扫描` / `security audit` / `硬编码密钥` / `SQL 注入` 等。

详见 `templates/security-audit.md` 完整版本。

## License

Apache 2.0