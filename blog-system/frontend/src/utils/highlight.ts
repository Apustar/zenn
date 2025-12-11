import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

export const initHighlight = () => {
  // 高亮代码块
  document.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightElement(block as HTMLElement)
  })
}

export const highlightCode = (code: string, language?: string): string => {
  if (language) {
    return hljs.highlight(code, { language }).value
  }
  return hljs.highlightAuto(code).value
}

