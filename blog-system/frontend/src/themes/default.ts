import type { ThemeConfig } from '@/types/theme'

/**
 * 默认主题 - 简洁现代风格
 */
export const defaultTheme: ThemeConfig = {
  id: 'default',
  name: '默认主题',
  description: '简洁现代的默认主题，适合日常使用',
  icon: 'mdi:palette',
  
  colors: {
    primary: '#FE9600',
    secondary: '#FFB84D',
    text: '#333333',
    textSecondary: '#666666',
    bg: '#FFFFFF',
    cardBg: '#FFFFFF',
    border: '#E5E5E5',
    headerBg: 'rgba(255, 255, 255, 0.9)',
    footerBg: '#F5F5F5',
    success: '#4CAF50',
    warning: '#FF9800',
    error: '#F44336',
    info: '#2196F3',
  },
  
  layout: {
    containerMaxWidth: '1200px',
    cardRadius: '8px',
    buttonRadius: '6px',
    inputRadius: '4px',
    shadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    cardShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    hoverShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    menuStyle: 'horizontal',
    menuPosition: 'top',
    headerStyle: 'default',
    postCardLayout: 'card',
    postLayout: 'centered',
    contentLayout: 'single',
  },
  
  typography: {
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    baseSize: '16px',
    lineHeight: '1.6',
  },
  
  cursor: {
    default: 'default',
    pointer: 'pointer',
    text: 'text',
  },
  
  background: {
    strategy: 'none',
    color: '#FFFFFF',
  },
  
  animations: {
    pageTransition: 'fade',
    cardHover: 'lift',
    buttonHover: 'scale',
    duration: '0.3s',
  },
}

