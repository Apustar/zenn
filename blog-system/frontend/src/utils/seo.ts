import type { Post } from '@/api/posts'

export interface SEOData {
  title?: string
  description?: string
  keywords?: string
  image?: string
  url?: string
  type?: string
}

export const updateSEO = (data: SEOData) => {
  const { title, description, keywords, image, url, type = 'website' } = data

  // 更新 title
  if (title) {
    document.title = `${title} - 我的博客`
  }

  // 更新或创建 meta 标签
  const updateMeta = (name: string, content: string, property?: boolean) => {
    const selector = property ? `meta[property="${name}"]` : `meta[name="${name}"]`
    let meta = document.querySelector(selector) as HTMLMetaElement
    
    if (!meta) {
      meta = document.createElement('meta')
      if (property) {
        meta.setAttribute('property', name)
      } else {
        meta.setAttribute('name', name)
      }
      document.head.appendChild(meta)
    }
    
    meta.setAttribute('content', content)
  }

  // 基础 SEO
  if (description) {
    updateMeta('description', description)
    updateMeta('og:description', description, true)
  }

  if (keywords) {
    updateMeta('keywords', keywords)
  }

  // Open Graph
  if (title) {
    updateMeta('og:title', title, true)
  }

  if (url) {
    updateMeta('og:url', url, true)
  }

  if (image) {
    updateMeta('og:image', image, true)
  }

  updateMeta('og:type', type, true)

  // Twitter Card
  if (title) {
    updateMeta('twitter:title', title)
  }

  if (description) {
    updateMeta('twitter:description', description)
  }

  if (image) {
    updateMeta('twitter:image', image)
  }

  updateMeta('twitter:card', 'summary_large_image')
}

export const updatePostSEO = (post: Post) => {
  updateSEO({
    title: post.title,
    description: post.excerpt || post.content?.substring(0, 200),
    keywords: post.tags.map(t => t.name).join(', '),
    image: post.cover,
    url: `${window.location.origin}/post/${post.slug}`,
    type: 'article',
  })
}

export const resetSEO = () => {
  updateSEO({
    title: '我的博客',
    description: '一个功能强大的个人博客系统',
  })
}

