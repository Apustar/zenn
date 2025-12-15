import type { ThemeConfig } from '@/types/theme'

/**
 * 极简主题 - 极简主义风格
 */
export const minimalTheme: ThemeConfig = {
  id: 'minimal',
  name: '极简主题',
  description: '极简主义风格，专注内容本身',
  icon: 'mdi:format-clear',
  
  colors: {
    primary: '#000000',
    secondary: '#666666',
    text: '#000000',
    textSecondary: '#666666',
    bg: '#FFFFFF',
    cardBg: '#FFFFFF',
    border: '#E0E0E0',
    headerBg: 'rgba(255, 255, 255, 0.95)',
    footerBg: '#FAFAFA',
    success: '#000000',
    warning: '#666666',
    error: '#000000',
    info: '#000000',
  },
  
  layout: {
    containerMaxWidth: '900px',
    cardRadius: '0px',
    buttonRadius: '0px',
    inputRadius: '0px',
    shadow: 'none',
    cardShadow: 'none',
    hoverShadow: 'none',
    menuStyle: 'minimal',
    menuPosition: 'top',
    headerStyle: 'minimal',
    postCardLayout: 'list',
    postLayout: 'narrow',
    contentLayout: 'single',
  },
  
  typography: {
    fontFamily: "'Helvetica Neue', Helvetica, Arial, sans-serif",
    headingFont: "'Georgia', serif",
    baseSize: '18px',
    lineHeight: '1.8',
  },
  
  cursor: {
    default: 'default',
    pointer: 'pointer',
    text: 'text',
    custom: 'url("/cursors/minimal.cur"), default',
  },
  
  background: {
    strategy: 'none',
    color: '#FFFFFF',
  },
  
  animations: {
    pageTransition: 'fade',
    cardHover: 'none',
    buttonHover: 'none',
    duration: '0.2s',
  },
}

