# 考试系统 — 前端设计规范

本文件是 Codex 在此项目中执行任何 UI 变更时的强制规则集。目标是达到专业 SaaS 产品的质感水准——克制、精致、有呼吸感。

---

## 技术栈

- 框架: Vue 3 (Composition API + `<script setup>`)
- UI 库: Element Plus 2.x
- 图标: @element-plus/icons-vue（禁止引入额外图标库）
- 样式: CSS 自定义属性驱动，定义在 `src/styles/global.css`
- 路由: vue-router 4 / 状态: pinia / 构建: Vite 5

---

## 组件组织

- 公共组件: `src/components/`（PascalCase，如 `StatCard.vue`、`PageHeader.vue`）
- 页面: `src/views/`（`XxxView.vue`）
- 所有组件 `<script setup>` + `<style scoped>`
- Props 使用 `defineProps` 带 TypeScript 泛型或 JSDoc
- 禁止组件内 inline style（除非值完全由 JS 运行时计算）

---

## 设计 Token（强制）

所有视觉属性必须通过 CSS 变量引用，禁止硬编码。Token 体系见 `global.css`：

| 类别 | 变量 | 说明 |
|------|------|------|
| 主色 | `--color-primary` / `--primary-*` | 品牌色，调性克制不刺眼 |
| 灰度 | `--gray-50` ~ `--gray-900` | 暖灰，不用冷灰 Tailwind 色 |
| 功能色 | `--color-success/warning/danger` | 饱和度降低，带浅色背景变体 |
| 间距 | `--space-1`(4px) ~ `--space-12`(48px) | 基于 4px 倍率 |
| 圆角 | `--radius-sm`(6px) / `md`(8px) / `lg`(12px) / `xl`(16px) | 统一圆角尺度 |
| 阴影 | `--shadow-xs/sm/md/lg/xl` | 多层阴影，表达深度层级 |
| 字号 | `--text-xs` ~ `--text-3xl` | 含行高配对 |
| 字重 | `--font-normal/mid/semibold/bold` | 统一字重管理 |
| 过渡 | `--transition-fast`(150ms) / `base`(200ms) / `slow`(300ms) | 缓动函数统一 ease-out |

**关键规则：新增 token 一律加到 `:root`，不在组件内造变量。**

---

## 质感原则

### 字体排印

- 基准字号 14px，正文行高 1.6
- 标题使用 `-0.02em` letter-spacing（紧凑精致）
- 正文使用 `-0.01em` letter-spacing
- 小字（辅助信息/标签）使用 12px，行高 1.5
- 数字（统计值/金额）使用 tabular-nums 等宽数字
- 英文/数字与中文间保持 1px 间距（通过 font-family fallback 自然处理）

### 色彩哲学

- 灰度系统使用暖灰——不是冷峻的 slate，也不是暖到发黄
- 主色控制在页面 5% 以内的面积——主色是信号，不是氛围灯
- 背景色 `--gray-50`：微微偏暖的极浅灰，不是纯白也不是死灰
- 卡片纯白 #fff，靠阴影而非边框区分层级
- 功能性颜色只在需要时出现（成功/警告/危险标签），不做大面积彩色背景

### 空间节奏

- 页面内容区分三级间距：
  - 区块间（section 之间）：`--space-10` ~ `--space-12`（40~48px）
  - 组件间（卡片/表格之间）：`--space-6`（24px）
  - 元素间（字段/按钮之间）：`--space-3` ~ `--space-4`（12~16px）
- 页面左右留白不低于 `--space-6`（24px）
- 卡片内边距统一 `--space-6`（24px）

### 阴影语言

- 不使用单层大模糊阴影——使用多层叠加模拟真实光影
- `shadow-sm`: 卡片默认状态，0 1px 3px，几乎不可见但区分于背景
- `shadow-md`: hover 状态，多层叠加，有抬升感
- `shadow-lg`: 弹窗/下拉，明显深度
- 侧边栏与主内容区用阴影分隔（不是边框）

### 边框策略

- 表格/列表类组件用极浅边框（`--gray-100`）
- 卡片默认不用边框——靠阴影区分
- 输入框/选择器用 1px 边框，颜色 `--gray-200`，focus 时变为主色
- 分割线用 `--gray-100`，高度 1px

### 动效

- 页面切换：fade 200ms ease-out（已定义）
- hover 状态：150ms ease-out
- 弹窗出现：scale(0.95)→scale(1) + opacity，250ms ease-out
- 下拉菜单：opacity + translateY(-4px→0)，200ms
- 数值变化不弹跳，不抖动
- 不做夸张的 spring 动画或弹性缓动

---

## 布局规范

### 整体结构

```
.app-layout
├── .sidebar (240px, dark, fixed, shadow分隔)
└── .main-area
    ├── .topbar (60px, semi-transparent白, backdrop-blur, sticky)
    └── .main-content
        └── .page-container (padding: var(--space-6), max-width: 1400px)
            ├── .page-header
            └── [content]
```

### 页面框架

- `page-container` 不设背景色——继承 body 的 `--gray-50`
- `page-header`：h2 标题 + 右侧操作区，margin-bottom: `--space-8`
- 内容区不使用 `<el-card>` 包页面——`el-card` 仅用于独立数据块
- 页面段落之间用 `margin-bottom: var(--space-10)` 分隔

### 统计卡片

- 使用 grid: `repeat(auto-fill, minmax(240px, 1fr))`，gap: `--space-4`
- 卡片内：icon(40px) → label(12px gray-500) → value(30px bold gray-900) → trend(12px)
- icon 背景使用主色 8% 透明度，前景色为主色
- hover 时卡片轻微上浮（translateY(-2px)）+ 阴影加深

### 表格

- 表头：高度 44px，背景 `--gray-50`，文字 12px semibold `--gray-500`，大写或正常
- 数据行：高度 48px，hover 背景 `--gray-25`（极浅灰）
- 行内操作按钮：文字按钮，不加边框，仅 hover 显示主色
- 空状态：`el-empty`，image-size="80"，description 使用 `--gray-400`

### 侧边栏

- 背景 `--gray-900`（不是纯黑，微微偏暖）
- 活跃项使用主色背景 + 白色文字 + 左侧 3px 指示条
- 非活跃项灰色文字，hover 时背景 `rgba(255,255,255,0.04)`
- 折叠按钮在底部，不在顶部
- 用户信息区在侧边栏底部，含头像 + 角色标签

---

## Element Plus 使用约定

### 覆盖原则

所有 Element Plus 样式覆盖集中在 `global.css`，使用 `--el-*` 变量或直接选择器覆盖：

```css
/* 正确：通过 CSS 变量覆盖 */
--el-color-primary: var(--color-primary);
--el-border-radius-base: var(--radius-md);

/* 正确：选择器覆盖，统一管理 */
.el-card { border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); }
```

组件内不覆盖 Element Plus 样式（除非是极特殊的单组件需求）。

### 组件使用

| 场景 | 组件 | 注意事项 |
|------|------|----------|
| 页面容器 | 纯 div + class | 不用 el-card 包页面 |
| 数据卡片 | `el-card` | shadow="never"，用 CSS shadow-sm |
| 表格 | `el-table` | stripe，size="medium" |
| 表单 | `el-form` | label-width="100px"，label 右对齐 |
| 弹窗 | `el-dialog` | width 按内容定，不超过 640px |
| 确认 | `el-popconfirm` | 删除/不可逆操作必须用 |
| 下拉 | `el-dropdown` | trigger="click" |
| 标签 | `el-tag` | size="small"，type 按语义 |
| 空状态 | `el-empty` | description 必填 |
| 分页 | `el-pagination` | background，small，靠右 |
| 按钮 | `el-button` | 主操作 primary，次要 default，危险 danger |

---

## 状态处理

- **Loading**: 表格/列表用 `v-loading`，按钮用 `:loading`，不做骨架屏
- **Empty**: 用 `el-empty`，description 说明"暂无数据"并暗示下一步操作
- **Error**: 用 `el-alert` type="error" 展示错误信息，不含技术细节
- **Success**: 用 `el-message` type="success"，不做大面积的绿色成功页

---

## 响应式

- 桌面（>768px）：标准布局，sidebar 240px
- 平板（≤768px）：sidebar 折叠至 64px 图标模式，内容区 margin-left: 64px
- 手机（≤480px）：sidebar 隐藏，通过顶部汉堡菜单触发 overlay 抽屉；内容区全宽
- **字号不随视口变化**——移动端和桌面端用同一套字号
- 间距在手机端缩小：`--space-6` → `--space-4`，`--space-8` → `--space-5`

### 手机端导航

- sidebar 改为 overlay 抽屉模式：从左侧滑入，带半透明遮罩层
- topbar 左侧显示汉堡菜单按钮（触发抽屉）
- 遮罩层点击关闭抽屉
- 抽屉打开时禁止 body 滚动

### 手机端触控

- 所有可点击元素最小触控区域 44×44px
- 按钮之间间距不低于 `--space-2`（8px），防止误触
- 表格行高 ≥48px，保证单行可点
- 操作列按钮改为图标按钮，节省空间
- 表单输入框 `size="large"`（高度 40px）

### 手机端内容适配

- 统计卡片：≤480px 时单列堆叠
- 表格：横向滚动（el-table 默认支持），重要列固定左侧
- 弹窗：width="90%"，top="5vh"，padding 缩小一级
- 分页：精简为简洁模式 `layout="prev, pager, next"`，隐藏总数和跳页
- 卡片 `el-card` body padding 在手机端缩小为 `--space-4`
- 双列布局（el-row :gutter="16" :span="12"）改为单列堆叠

### 手机端安全区

- 使用 `env(safe-area-inset-*)` 适配刘海屏和底部指示条
- 底部固定按钮需要 `padding-bottom: env(safe-area-inset-bottom, 0)`
- 顶部固定栏需要 `padding-top: env(safe-area-inset-top, 0)`

---

## 禁止事项

- ❌ 硬编码颜色值（hex/rgb/hsl）—— 一律走 CSS 变量
- ❌ 硬编码 px 间距/字号 —— 一律走 CSS 变量
- ❌ 卡中卡 —— el-card 内部不嵌套 el-card
- ❌ 装饰性漂浮元素 —— 禁止背景圆球、bokeh、渐变光晕、bg-shape
- ❌ 引入额外图标库 —— 只用 @element-plus/icons-vue
- ❌ emoji 作为 UI 元素 —— 用图标组件
- ❌ 自定义滚动条样式
- ❌ 字号用 vw 缩放
- ❌ 彩色大背景 —— 背景统一用 gray-50
- ❌ 单层大模糊阴影 —— 用多层叠加
- ❌ 纯黑或纯白文字 —— 用灰度变量
- ❌ 过饱和功能色 —— success/warning/danger 都已调低饱和度

---

## Figma → 代码工作流

1. 解析 Figma URL → fileKey + nodeId
2. `get_design_context` → 结构化数据
3. `get_screenshot` → 视觉参考
4. 下载 Figma 资源（localhost 来源直接使用）
5. 将 Tailwind/React 输出转换为 Vue 3 + Element Plus + CSS 变量
6. 用 Element Plus 组件替换通用元素
7. 对照截图验证 1:1 还原
