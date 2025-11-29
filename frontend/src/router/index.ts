import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import Layout from '../components/Layout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          name: 'home',
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: HomeView // Temporarily use HomeView as dashboard
        },
        {
          path: 'teacher/dashboard',
          name: 'teacher-dashboard',
          component: () => import('../views/teacher/Dashboard.vue')
        },
        {
          path: 'student/dashboard',
          name: 'student-dashboard',
          component: () => import('../views/student/Dashboard.vue')
        },
        {
          path: 'admin/dashboard',
          name: 'admin-dashboard',
          component: () => import('../views/admin/Dashboard.vue')
        },
        {
          path: '/about',
          name: 'about',
          // route level code-splitting
          // this generates a separate chunk (About.[hash].js) for this route
          // which is lazy-loaded when the route is visited.
          component: () => import('../views/AboutView.vue')
        }
      ]
    }
  ]
})

export default router
