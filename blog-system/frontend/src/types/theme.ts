/**
 * 主题系统类型定义
 */

export interface ThemeConfig {
  /** 主题ID */
  id: string
  /** 主题名称 */
  name: string
  /** 主题描述 */
  description: string
  /** 主题图标 */
  icon: string
  /** 预览图 */
  preview?: string
  
  /** 颜色配置 */
  colors: {
    /** 主色调 */
    primary: string
    /** 次要色 */
    secondary?: string
    /** 文本颜色 */
    text: string
    /** 次要文本颜色 */
    textSecondary: string
    /** 背景颜色 */
    bg: string
    /** 卡片背景 */
    cardBg: string
    /** 边框颜色 */
    border: string
    /** Header背景 */
    headerBg: string
    /** Footer背景 */
    footerBg: string
    /** 成功色 */
    success?: string
    /** 警告色 */
    warning?: string
    /** 错误色 */
    error?: string
    /** 信息色 */
    info?: string
  }
  
  /** 布局配置 */
  layout: {
    /** 容器最大宽度 */
    containerMaxWidth: string
    /** 卡片圆角 */
    cardRadius: string
    /** 按钮圆角 */
    buttonRadius: string
    /** 输入框圆角 */
    inputRadius: string
    /** 阴影 */
    shadow: string
    /** 卡片阴影 */
    cardShadow: string
    /** Hover阴影 */
    hoverShadow: string
    /** 菜单样式 */
    menuStyle?: 'horizontal' | 'vertical' | 'centered' | 'minimal'
    /** 菜单位置 */
    menuPosition?: 'top' | 'left' | 'right' | 'center'
    /** Header样式 */
    headerStyle?: 'default' | 'minimal' | 'glass' | 'solid'
    /** 文章卡片布局 */
    postCardLayout?: 'card' | 'list' | 'magazine' | 'minimal'
    /** 文章详情页布局 */
    postLayout?: 'centered' | 'wide' | 'narrow' | 'magazine'
    /** 内容区域布局 */
    contentLayout?: 'single' | 'two-column' | 'three-column'
  }
  
  /** 字体配置 */
  typography: {
    /** 字体族 */
    fontFamily: string
    /** 标题字体 */
    headingFont?: string
    /** 基础字体大小 */
    baseSize: string
    /** 行高 */
    lineHeight: string
  }
  
  /** 鼠标样式配置 */
  cursor: {
    /** 默认鼠标样式 */
    default: string
    /** 链接鼠标样式 */
    pointer: string
    /** 文本选择鼠标样式 */
    text: string
    /** 自定义鼠标样式（CSS cursor值或图片URL） */
    custom?: string
    /** 鼠标跟随效果 */
    followEffect?: {
      enabled: boolean
      type: 'dot' | 'circle' | 'ring' | 'custom'
      color?: string
      size?: string
    }
  }
  
  /** 背景配置 */
  background: {
    /** 背景图片URL */
    image?: string
    /** 背景策略 */
    strategy: 'none' | 'no-repeat' | 'repeat' | 'cover' | 'contain'
    /** 背景颜色（作为fallback） */
    color: string
    /** 背景渐变 */
    gradient?: string
    /** 背景动画 */
    animation?: 'none' | 'gradient' | 'particles' | 'waves'
  }
  
  /** 动画配置 */
  animations: {
    /** 页面切换动画 */
    pageTransition: 'fade' | 'slide' | 'zoom' | 'none'
    /** 卡片hover动画 */
    cardHover: 'lift' | 'scale' | 'glow' | 'none'
    /** 按钮hover动画 */
    buttonHover: 'scale' | 'glow' | 'slide' | 'none'
    /** 动画持续时间 */
    duration: string
  }
  
  /** 特殊效果 */
  effects?: {
    /** 玻璃态效果 */
    glassmorphism?: boolean
    /** 毛玻璃效果 */
    backdropBlur?: boolean
    /** 粒子效果 */
    particles?: boolean
  }
}

