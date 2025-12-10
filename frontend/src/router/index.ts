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
          component: () => import('../views/common/CourseDetail.vue'),
          redirect: to => ({ name: 'course-tasks', params: { id: to.params.id } }),
          children: [
            {
              path: 'tasks',
              name: 'course-tasks',
              component: () => import('@/views/common/TaskManager.vue') // 假设任务组件路径
            },
            {
              path: 'discussions',
              name: 'course-discussions',
              component: () => import('@/views/common/DiscussionManager.vue')
            },
            {
              path: 'discussions/:topicId',
              name: 'course-discussion-detail',
              component: () => import('@/views/common/DiscussionTopicDetail.vue'),
              props: true
            },
            {
              path: 'chapters',
              name: 'course-chapters',
              component: () => import('@/views/common/ChapterManager.vue')
            },
            {
              path: 'members',
              name: 'course-members',
              component: () => import('@/views/common/MemberManager.vue')
            },
            {
              path: 'announcements',
              name: 'course-announcements',
              component: () => import('@/views/common/AnnouncementManager.vue')
            },
            {
              path: 'materials',
              name: 'course-materials',
              component: () => import('@/views/common/CourseMaterialManager.vue')
            }
            // 其他子路由可以根据需要在这里添加
          ]
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
        return next('/student/courses');
      case 'teacher':
        return next('/teacher/courses');
      case 'admin':
        return next('/admin/users');
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
      // 已登录，但访问的是根路径或旧的dashboard -> 根据角色重定向
      const oldDashboardPaths = ['/', '/dashboard', '/student/dashboard', '/teacher/dashboard', '/admin/dashboard'];
      if (oldDashboardPaths.includes(to.path)) {
        switch (userRole) {
          case 'student':
            return next('/student/courses');
          case 'teacher':
            return next('/teacher/courses');
          case 'admin':
            return next('/admin/users');
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
