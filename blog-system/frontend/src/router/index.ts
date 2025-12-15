import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
  },
  {
    path: '/post/:slug',
    name: 'Post',
    component: () => import('@/views/Post.vue'),
  },
  {
    path: '/category/:slug',
    name: 'Category',
    component: () => import('@/views/Category.vue'),
  },
  {
    path: '/tag/:slug',
    name: 'Tag',
    component: () => import('@/views/Tag.vue'),
  },
  {
    path: '/archives',
    name: 'Archives',
    component: () => import('@/views/Archives.vue'),
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/Search.vue'),
  },
  {
    path: '/moments',
    name: 'Moments',
    component: () => import('@/views/Moments.vue'),
  },
  {
    path: '/photos',
    name: 'Photos',
    component: () => import('@/views/Photos.vue'),
  },
  {
    path: '/album/:slug',
    name: 'Album',
    component: () => import('@/views/Album.vue'),
  },
  {
    path: '/links',
    name: 'Links',
    component: () => import('@/views/Links.vue'),
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  {
    path: '/access-denied',
    name: 'AccessDenied',
    component: () => import('@/views/AccessDenied.vue'),
  },
  // 管理后台路由
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresStaff: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
      },
      {
        path: 'posts',
        name: 'AdminPosts',
        component: () => import('@/views/admin/Posts.vue'),
      },
      {
        path: 'posts/:id',
        name: 'AdminPostEdit',
        component: () => import('@/views/admin/PostEdit.vue'),
      },
      {
        path: 'posts/new',
        name: 'AdminPostNew',
        component: () => import('@/views/admin/PostEdit.vue'),
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import('@/views/admin/Categories.vue'),
      },
      {
        path: 'tags',
        name: 'AdminTags',
        component: () => import('@/views/admin/Tags.vue'),
      },
      {
        path: 'comments',
        name: 'AdminComments',
        component: () => import('@/views/admin/Comments.vue'),
      },
      {
        path: 'moments',
        name: 'AdminMoments',
        component: () => import('@/views/admin/Moments.vue'),
      },
      {
        path: 'photos',
        name: 'AdminPhotos',
        component: () => import('@/views/admin/Photos.vue'),
      },
      {
        path: 'music',
        name: 'AdminMusic',
        component: () => import('@/views/admin/Music.vue'),
      },
      {
        path: 'links',
        name: 'AdminLinks',
        component: () => import('@/views/admin/Links.vue'),
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/Settings.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// 路由守卫：检查访问权限
router.beforeEach(async (to, from, next) => {
  // 管理后台路由需要认证和 staff 权限
  if (to.path.startsWith('/admin')) {
    const { useAuthStore } = await import('@/stores/auth')
    const authStore = useAuthStore()
    
    // 检查是否有 token
    const token = localStorage.getItem('access_token')
    if (!token) {
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
    
    // 检查用户信息是否已加载
    if (!authStore.user) {
      try {
        await authStore.fetchUser()
      } catch (error) {
        // 如果获取用户信息失败，清除 token 并跳转登录
        authStore.logout()
        next({ path: '/login', query: { redirect: to.fullPath } })
        return
      }
    }
    
    // 检查是否有 staff 权限
    if (!authStore.user?.is_staff) {
      next({ path: '/access-denied' })
      return
    }
    
    next()
    return
  }
  
  // 排除登录页、访问受限页、搜索页和动态路由（这些不在导航菜单中）
  const excludedPaths = ['/login', '/access-denied', '/search']
  const isDynamicRoute = to.path.startsWith('/post/') || 
                         to.path.startsWith('/category/') || 
                         to.path.startsWith('/tag/') ||
                         to.path.startsWith('/album/')
  
  if (excludedPaths.includes(to.path) || isDynamicRoute) {
    next()
    return
  }

  try {
    // 检查URL访问权限（只检查导航菜单中的路由）
    const { navigationApi } = await import('@/api/settings')
    const result = await navigationApi.checkUrlAccess(to.path)
    
    if (result.accessible) {
      next()
    } else {
      // 不可访问，跳转到访问受限页面
      next('/access-denied')
    }
  } catch (error) {
    // API调用失败时，默认允许访问（避免阻塞正常访问）
    if (import.meta.env.DEV) {
      console.error('Failed to check URL access:', error)
    }
    next()
  }
})

export default router

