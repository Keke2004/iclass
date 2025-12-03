import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
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
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/',
      component: Layout,
      meta: { requiresAuth: true },
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
        },
        // Profile Page
        {
          path: '/profile',
          name: 'profile',
          component: () => import('../views/ProfileView.vue')
        },
        // Student Routes
        {
          path: 'student/courses',
          name: 'student-courses',
          component: () => import('../views/student/Courses.vue')
        },
        // Teacher Routes
        {
          path: 'teacher/courses',
          name: 'teacher-courses',
          component: () => import('../views/teacher/Courses.vue')
        },
        {
          path: 'teacher/courses/create',
          name: 'teacher-create-course',
          component: () => import('../views/teacher/CreateCourse.vue')
        },
        {
          path: 'courses/:id',
          name: 'course-detail',
          component: () => import('../views/common/CourseDetail.vue')
        },
        // Admin Routes
        {
          path: 'admin/users',
          name: 'admin-users',
          component: () => import('../views/admin/Users.vue')
        },
        {
          path: 'admin/statistics',
          name: 'admin-statistics',
          component: () => import('../views/admin/Statistics.vue')
        },
        {
          path: 'admin/logs',
          name: 'admin-logs',
          component: () => import('../views/admin/LogView.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const accessToken = localStorage.getItem('access_token');
  const userRole = localStorage.getItem('user_role');

  // 1. 已登录用户访问登录/注册页 -> 重定向到主页
  if (accessToken && userRole && (to.name === 'login' || to.name === 'register')) {
    switch (userRole) {
      case 'student':
        return next('/student/dashboard');
      case 'teacher':
        return next('/teacher/dashboard');
      case 'admin':
        return next('/admin/dashboard');
      default:
        // 角色丢失或异常，登出
        localStorage.clear();
        return next('/login');
    }
  }

  // 2. 访问需要认证的路由
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!accessToken || !userRole) {
      // 未登录 -> 重定向到登录页
      return next('/login');
    } else {
      // 已登录，但访问的是根路径或通用dashboard -> 根据角色重定向
      if (to.path === '/' || to.path === '/dashboard') {
        switch (userRole) {
          case 'student':
            return next('/student/dashboard');
          case 'teacher':
            return next('/teacher/dashboard');
          case 'admin':
            return next('/admin/dashboard');
          default:
            localStorage.clear();
            return next('/login');
        }
      }
      // 访问其他受保护路由 -> 放行
      return next();
    }
  }

  // 3. 访问公共路由 -> 放行
  next();
});

export default router
