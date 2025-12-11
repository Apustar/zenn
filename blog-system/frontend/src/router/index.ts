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
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
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

export default router

