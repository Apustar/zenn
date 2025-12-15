import type { ThemeConfig } from '@/types/theme'

/**
 * 深色主题 - 护眼暗色风格
 */
export const darkTheme: ThemeConfig = {
  id: 'dark',
  name: '深色主题',
  description: '护眼的深色主题，适合夜间使用',
  icon: 'mdi:weather-night',
  
  colors: {
    primary: '#FFB84D',
    secondary: '#FE9600',
    text: '#E5E5E5',
    textSecondary: '#999999',
    bg: '#1A1A1A',
    cardBg: '#2A2A2A',
    border: '#404040',
    headerBg: 'rgba(26, 26, 26, 0.9)',
    footerBg: '#1A1A1A',
    success: '#66BB6A',
    warning: '#FFA726',
    error: '#EF5350',
    info: '#42A5F5',
  },
  
  layout: {
    containerMaxWidth: '1200px',
    cardRadius: '12px',
    buttonRadius: '8px',
    inputRadius: '6px',
    shadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
    cardShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
    hoverShadow: '0 6px 20px rgba(0, 0, 0, 0.5)',
    menuStyle: 'horizontal',
    menuPosition: 'top',
    headerStyle: 'glass',
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
    followEffect: {
      enabled: true,
      type: 'dot',
      color: '#FFB84D',
      size: '8px',
    },
  },
  
  background: {
    strategy: 'cover',
    color: '#1A1A1A',
    gradient: 'linear-gradient(135deg, #1A1A1A 0%, #2A2A2A 100%)',
  },
  
  animations: {
    pageTransition: 'fade',
    cardHover: 'glow',
    buttonHover: 'glow',
    duration: '0.3s',
  },
  
  effects: {
    glassmorphism: false,
    backdropBlur: true,
  },
}

