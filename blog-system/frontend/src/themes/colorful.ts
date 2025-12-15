import type { ThemeConfig } from '@/types/theme'

/**
 * 彩色主题 - 活泼多彩风格
 */
export const colorfulTheme: ThemeConfig = {
  id: 'colorful',
  name: '彩色主题',
  description: '活泼多彩的主题，充满活力',
  icon: 'mdi:palette-outline',
  
  colors: {
    primary: '#FF6B6B',
    secondary: '#4ECDC4',
    text: '#2C3E50',
    textSecondary: '#7F8C8D',
    bg: '#F8F9FA',
    cardBg: '#FFFFFF',
    border: '#E1E8ED',
    headerBg: 'rgba(255, 255, 255, 0.95)',
    footerBg: '#ECF0F1',
    success: '#2ECC71',
    warning: '#F39C12',
    error: '#E74C3C',
    info: '#3498DB',
  },
  
  layout: {
    containerMaxWidth: '1200px',
    cardRadius: '16px',
    buttonRadius: '24px',
    inputRadius: '12px',
    shadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    cardShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
    hoverShadow: '0 12px 24px rgba(0, 0, 0, 0.15)',
    menuStyle: 'centered',
    menuPosition: 'top',
    headerStyle: 'glass',
    postCardLayout: 'magazine',
    postLayout: 'wide',
    contentLayout: 'two-column',
  },
  
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    baseSize: '16px',
    lineHeight: '1.6',
  },
  
  cursor: {
    default: 'default',
    pointer: 'pointer',
    text: 'text',
    followEffect: {
      enabled: true,
      type: 'circle',
      color: '#FF6B6B',
      size: '20px',
    },
  },
  
  background: {
    strategy: 'cover',
    color: '#F8F9FA',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%)',
    animation: 'gradient',
  },
  
  animations: {
    pageTransition: 'slide',
    cardHover: 'scale',
    buttonHover: 'scale',
    duration: '0.4s',
  },
  
  effects: {
    glassmorphism: true,
    backdropBlur: true,
  },
}

