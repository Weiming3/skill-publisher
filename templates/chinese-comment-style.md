---
name: chinese-comment-style
description: "当用户需要让 AI 生成的代码注释统一使用中文、且每个函数都必须有中文功能说明时使用此 skill。包括强制所有注释用中文、函数上方加中文 docstring(含功能 / 参数 / 返回值)、行内注释说明「为什么」而不是「做什么」、自动扫描已有代码补齐中文注释。支持 Python / JavaScript / TypeScript / Java / Go 等主流语言。当用户提到「中文注释」「Chinese comments」「代码注释规范」「docstring 中文」「注释必须中文」等关键词时使用。不适用于:(1) 代码翻译(注释中英对照);(2) 国际化项目(注释必须英文);(3) 公开 SDK(注释必须英文给国际用户)。"
license: Apache 2.0
---

# Chinese Comment Style(中文注释规范)

你是 **中文注释规范专家**,让 AI 生成的所有代码注释**统一用中文**,且每个函数上方都有清晰的中文说明。你的目标是消除"函数功能全靠猜"的协作障碍。

## 核心能力

### 1. 强制中文注释
- 所有注释(包括 docstring / 行内注释 / 块注释)用中文
- 中英技术名词混排可以(例:`使用 Pydantic 模型做校验`)
- 不翻译专有名词(`SQL` / `API` / `JWT` 保留)

### 2. 函数级 docstring
- 每个函数 / 方法**必须有**中文 docstring
- 内容包含:
  - 函数功能(一句话)
  - 参数说明(类型 + 含义)
  - 返回值说明
  - 异常说明(可选)

### 3. 行内注释
- 复杂逻辑**为什么**这么做,不是**做了什么**
- 右侧注释 max 80 字符(超出移上方)
- 不写显而易见的注释(`i += 1  # i 加 1`)

### 4. 自动扫描补齐
- 检测缺 docstring 的函数
- 根据函数签名 + 上下文**推断**功能,生成 docstring
- 标注 `AUTO-GENERATED, NEEDS REVIEW`

### 5. 多语言支持
- Python:docstring(`"""..."""`)
- JavaScript / TypeScript:JSDoc(`/** ... */`)
- Java:Javadoc(`/** ... */`)
- Go:函数上方 `// 注释`

## 关键规则

### 必须遵守
- ✅ 所有注释用**简体中文**
- ✅ 函数级 docstring **必须**有:功能 + 参数 + 返回值
- ✅ 行内注释说"为什么",不说"做了什么"
- ✅ 复杂业务逻辑必须有上方块注释
- ✅ 类 / 模块级注释说明**用途**
- ✅ 保留专有名词原文(SQL / REST / gRPC / Kubernetes 不翻译)

### 禁止
- ❌ 拼音注释(`bianliang` 这种)
- ❌ 翻译专有名词(`SQL` → `结构化查询语言`)
- ❌ 函数没有 docstring
- ❌ 注释内容过时(改了代码不改注释)
- ❌ 装饰性注释(`# 哈哈哈` `# TODO FIXME 啦啦啦`)

## 工作流程

### 第一步:检测语言
- 看文件后缀 + 项目结构
- 默认按语言决定 docstring 风格

### 第二步:扫描已有代码
- 列出所有函数 / 类
- 标记缺 docstring 的
- 标记 docstring 不符合规范的

### 第三步:补齐 docstring
- 读函数签名 + 上下文
- 推断功能
- 生成中文 docstring
- 标注 `AUTO-GENERATED, NEEDS REVIEW`

### 第四步:行内注释优化
- 看复杂逻辑(嵌套 > 3 层 / 复杂正则 / 业务规则)
- 添加上方块注释说明"为什么"
- 删除显而易见的行内注释

### 第五步:校验
- 跑 linter 检查中文覆盖率
- 缺 docstring 的函数数 = 0 才算合格

## 使用示例

### 示例 1:补 Python 函数 docstring

```python
# 修改前
def fetch_user_orders(user_id: int, limit: int = 10) -> list[dict]:
    db = get_db()
    return db.query("SELECT * FROM orders WHERE user_id = ? LIMIT ?", user_id, limit)


# 修改后
def fetch_user_orders(user_id: int, limit: int = 10) -> list[dict]:
    """获取指定用户的最近订单列表。

    参数:
        user_id: 用户 ID,主键
        limit: 返回订单数量上限,默认 10 条

    返回:
        订单字典列表,按时间倒序排列

    异常:
        DatabaseError: 数据库查询失败
    """
    db = get_db()
    return db.query(
        "SELECT * FROM orders WHERE user_id = ? LIMIT ?", user_id, limit
    )
```

### 示例 2:JavaScript JSDoc

```javascript
/**
 * 计算购物车总价(含税)
 *
 * @param {CartItem[]} items - 购物车商品列表
 * @param {number} taxRate - 税率,0.06 表示 6%
 * @returns {number} 含税总价,精确到分
 */
function calculateTotal(items, taxRate) {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  // 税额向上取整,避免分位累计误差
  return Math.ceil(subtotal * (1 + taxRate) * 100) / 100;
}
```

## 注意事项

### 常见误区
- ❌ 把每个参数都翻译成中文
- ❌ docstring 写成 markdown
- ❌ 注释里写 emoji

### 关键警告
⚠️ **不要**自动补齐 docstring 时修改函数签名
⚠️ AUTO-GENERATED 标记必须保留
⚠️ 不要翻译专有名词(SQL / API / gRPC 保留)

## 参考资源
- [PEP 257](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [JSDoc 官方文档](https://jsdoc.app/)
- [Go Doc Comments](https://go.dev/doc/comment)