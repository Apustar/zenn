# 主题系统使用文档

## 概述

本博客系统支持一键切换多个主题模板，每个主题都有独特的布局、UI风格和鼠标样式。主题切换不会影响任何现有功能。

## 功能特性

### ✅ 已实现的功能

1. **4个内置主题**
   - 默认主题：简洁现代风格
   - 深色主题：护眼暗色风格，带鼠标跟随效果
   - 极简主题：极简主义风格
   - 彩色主题：活泼多彩风格，带渐变背景和鼠标跟随效果

2. **主题配置系统**
   - 颜色系统（主色、文本色、背景色等）
   - 布局系统（圆角、阴影、间距等）
   - 字体系统（字体族、大小、行高）
   - 鼠标样式系统（默认、指针、文本、自定义、跟随效果）
   - 背景系统（纯色、渐变、图片）
   - 动画系统（页面切换、卡片hover、按钮hover）

3. **一键切换**
   - 点击Header中的主题切换按钮
   - 弹出主题选择模态框
   - 实时预览主题效果
   - 切换后立即生效并保存到localStorage

4. **鼠标样式**
   - 支持自定义鼠标样式
   - 支持鼠标跟随效果（点、圆、环）
   - 不同主题可以有不同的鼠标样式

## 使用方法

### 用户端

1. 点击Header右上角的调色板图标
2. 在弹出的主题选择框中选择喜欢的主题
3. 主题会立即应用并保存

### 开发者端

#### 添加新主题

1. 在 `src/themes/` 目录下创建新主题文件，例如 `mytheme.ts`：

```typescript
import type { ThemeConfig } from '@/types/theme'

export const myTheme: ThemeConfig = {
  id: 'mytheme',
  name: '我的主题',
  description: '主题描述',
  icon: 'mdi:star',
  
  colors: {
    primary: '#FF0000',
    // ... 其他颜色配置
  },
  
  // ... 其他配置
}
```

2. 在 `src/themes/index.ts` 中注册新主题：

```typescript
import { myTheme } from './mytheme'

export const themes: Record<string, ThemeConfig> = {
  // ... 现有主题
  mytheme: myTheme,
}
```

#### 自定义鼠标样式

在主题配置中的 `cursor` 字段设置：

```typescript
cursor: {
  default: 'default',  // 默认鼠标样式
  pointer: 'pointer',  // 链接鼠标样式
  text: 'text',        // 文本鼠标样式
  custom: 'url("/cursors/custom.cur"), default',  // 自定义鼠标样式（图片URL）
  followEffect: {     // 鼠标跟随效果
    enabled: true,
    type: 'dot' | 'circle' | 'ring',
    color: '#FF0000',
    size: '10px',
  },
}
```

## 主题配置项说明

### 颜色配置 (colors)

- `primary`: 主色调
- `secondary`: 次要色
- `text`: 文本颜色
- `textSecondary`: 次要文本颜色
- `bg`: 背景颜色
- `cardBg`: 卡片背景
- `border`: 边框颜色
- `headerBg`: Header背景
- `footerBg`: Footer背景
- `success/warning/error/info`: 语义化颜色

### 布局配置 (layout)

- `containerMaxWidth`: 容器最大宽度
- `cardRadius`: 卡片圆角
- `buttonRadius`: 按钮圆角
- `inputRadius`: 输入框圆角
- `shadow`: 基础阴影
- `cardShadow`: 卡片阴影
- `hoverShadow`: Hover阴影

### 鼠标样式配置 (cursor)

- `default`: 默认鼠标样式
- `pointer`: 指针鼠标样式
- `text`: 文本鼠标样式
- `custom`: 自定义鼠标样式（CSS cursor值或图片URL）
- `followEffect`: 鼠标跟随效果配置

### 背景配置 (background)

- `image`: 背景图片URL
- `strategy`: 背景策略（none/no-repeat/repeat/cover/contain）
- `color`: 背景颜色
- `gradient`: 背景渐变
- `animation`: 背景动画类型

### 动画配置 (animations)

- `pageTransition`: 页面切换动画（fade/slide/zoom/none）
- `cardHover`: 卡片hover动画（lift/scale/glow/none）
- `buttonHover`: 按钮hover动画（scale/glow/slide/none）
- `duration`: 动画持续时间

## 技术实现

### 主题应用流程

1. 用户选择主题
2. `ThemeStore.setTheme()` 被调用
3. `applyThemeToDOM()` 应用CSS变量到DOM
4. `applyCursorStyle()` 应用鼠标样式
5. 如果启用鼠标跟随，`initCursorFollow()` 初始化跟随效果
6. 主题ID保存到localStorage

### CSS变量系统

所有主题配置都通过CSS变量应用到DOM：

```css
:root {
  --primary-color: #FE9600;
  --text-color: #333;
  /* ... 其他变量 */
}
```

组件通过 `var(--primary-color)` 使用这些变量，确保主题切换时自动更新。

### 兼容性保证

- 所有现有组件都使用CSS变量，无需修改
- 主题切换只改变CSS变量值，不影响组件逻辑
- 向后兼容：保留原有的 `.dark` 类支持

## 注意事项

1. **不影响现有功能**：主题系统只改变视觉样式，不改变任何功能逻辑
2. **性能优化**：主题切换使用CSS变量，性能开销极小
3. **浏览器兼容**：CSS变量支持现代浏览器（IE11+）
4. **鼠标跟随效果**：在移动端会自动禁用

## 未来扩展

- [ ] 主题编辑器（可视化配置主题）
- [ ] 更多内置主题
- [ ] 用户自定义主题保存
- [ ] 主题市场（分享和下载主题）
- [ ] 主题预览功能增强

