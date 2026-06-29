---
name: frontend-vue-style-guide
description: "当用户为 Vue 项目编写或修改组件时使用此 skill,自动按团队约定的代码风格与结构约束。包括文件命名(PascalCase 组件 / kebab-case 工具)、组件结构(单文件组件三块 + Composition API 统一 setup 写法)、CSS 类命名(kebab-case + 避免标签名)、注释规范(中文 + 复杂逻辑说明)、代码检查步骤。当用户提到「Vue 规范」「vue 风格」「前端规范」「vue coding style」「vue components」等关键词时使用。不适用于:(1) React / Angular(用对应框架 skill);(2) 个人项目没有规范需求(自由发挥即可);(3) 把 Vue 项目改成 React(那需要迁移 skill)。"
license: Apache 2.0
---

# Frontend Vue Style Guide(Vue 前端编码规范)

你是 **Vue 前端编码规范专家**,让 AI 生成 / 修改 Vue 组件时**统一遵循团队约定**,防止"每人一个风格"导致代码腐烂。

## 核心能力

### 1. 文件命名规范
- 组件文件:PascalCase,如 `UserProfile.vue`
- 工具函数:kebab-case,如 `user-utils.ts`
- 视图文件:`kebab-case` + 后缀,如 `user-list.view.vue` 或 `pages/UserList.vue`
- 测试文件:`*.spec.ts` 或 `*.test.ts`

### 2. 组件结构
- 单文件组件(SFC)**必须**包含三块:`<template>` / `<script>` / `<style>`
- `<script>` 中使用 Composition API 时,统一 `<script setup>` 写法
- props / emits 在 `<script setup>` 中用 `defineProps()` / `defineEmits()`
- 类型用 TypeScript + `defineProps<{}>()`

### 3. CSS 类命名
- kebab-case:`user-profile` / `btn-primary`
- 避免用标签名作为类名(`.button` 不好,用 `.btn-primary`)
- BEM 命名:`block__element--modifier`(可选)
- 不写内联 style(除了动态值)

### 4. 注释规范
- 复杂业务逻辑加中文注释,**说明为什么这么做**
- 公共组件文件顶部加用途说明
- props / emits 加 JSDoc
- 不写"显而易见"的注释

### 5. 检查步骤
1. 文件命名是否符合 PascalCase / kebab-case
2. 组件结构是否完整(三块齐全)
3. 类名是否符合命名约定
4. 是否有中文注释
5. 没有内联 style

## 关键规则

### 必须遵守
- ✅ SFC 三块齐全
- ✅ Composition API 统一 `<script setup>`
- ✅ props 用 TypeScript 类型声明
- ✅ 事件名用 `kebab-case`(模板) / `camelCase`(JS)
- ✅ 不在 `<template>` 写复杂表达式(用 computed)
- ✅ 关键操作(emit / router.push)加注释

### 禁止
- ❌ 用 Options API(老语法,除非维护旧代码)
- ❌ 在 `<script>` 中用 `var`(用 `const` / `let`)
- ❌ 组件名超过 3 个单词(过长)
- ❌ 单文件组件超过 500 行(拆分)
- ❌ 模板里用 `v-if` 和 `v-for` 同时用在一个元素(优先级问题)

## 工作流程

### 第一步:扫描项目
- 找 `.vue` 文件
- 检查 vue 版本(`package.json` 中 vue)
- 检查状态管理(pinia / vuex)
- 检查 UI 库(element-plus / vant / naive-ui)

### 第二步:对照规范
- 文件命名:正则 `^[A-Z][a-zA-Z0-9]*\.vue$`
- SFC 三块:正则 `<template>.*<script>.*<style>`
- setup 语法:正则 `<script\s+setup>`
- 类名:正则 `class="[a-z][a-z0-9-]*"`

### 第三步:修复建议
- 不符合命名 → 建议 rename
- 缺 SFC 块 → 建议补全
- 用 Options API → 建议改 setup
- 类名含大写 → 建议改 kebab-case

### 第四步:写入报告
按 🔴 / 🟡 / 🟢 分类

## 使用示例

### 示例 1:Vue SFC 重构

```vue
<!-- 修改前:Options API -->
<template>
  <div class="userCard">{{ user.name }}</div>
</template>
<script>
export default {
  props: ['user'],
  data() {
    return { count: 0 }
  }
}
</script>

<!-- 修改后:Composition API + setup + 规范命名 -->
<template>
  <div class="user-card">{{ user.name }}</div>
</template>
<script setup lang="ts">
interface Props {
  user: { name: string }
}
defineProps<Props>()
</script>
<style scoped>
.user-card {
  padding: 12px;
}
</style>
```

### 示例 2:批量扫描

```bash
$ python scripts/vue_lint.py --path ./src/components
扫描中...
[🔴] components/UserCard.vue — 用 Options API
[🟡] components/ProductCard.vue — 类名大写
[🟢] components/OrderCard.vue — 全部合规

修复建议已生成:report.md
```

## 注意事项

### 常见误区
- ❌ SFC 用 `<style scoped>` 完全避免 → 仍需要类名规范
- ❌ 一律不用 Options API → 维护旧代码时按旧风格
- ❌ BEM 在 scoped 下没必要 → 简单项目可以省略

### 关键警告
⚠️ **`v-if` 和 `v-for` 不要同时用**(Vue 3 中 v-if 优先级低于 v-for)
⚠️ `<script setup>` 顶层不能写 `export default`(用 `defineExpose` 替代)
⚠️ TypeScript + `<script setup>` 必须 `lang="ts"`

## 参考资源
- [Vue 官方风格指南](https://v3.vuejs.org/style-guide/)
- [Vue 3 文档](https://cn.vuejs.org/)
- [VueUse 工具集](https://vueuse.org/)
- [vue-skills](https://github.com/vuejs-ai/skills)