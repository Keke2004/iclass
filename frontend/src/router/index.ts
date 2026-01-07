import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ForgotPassword from '../views/ForgotPassword.vue'
import Layout from '../components/Layout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
      {
        path: '/assignments/new',
        name: 'AssignmentCreate',
        component: () => import('../views/teacher/AssignmentEditor.vue'),
        meta: { requiresAuth: true, roles: ['teacher'] }
      },
      {
          path: '/assignments/:id/edit',
        name: 'AssignmentEdit',
        component: () => import('../views/teacher/AssignmentEditor.vue'),
        meta: { requiresAuth: true, roles: ['teacher'] }
      },
      {
        path: '/exams/new',
        name: 'ExamCreate',
        component: () => import('../views/teacher/ExamEditor.vue'),
        meta: { requiresAuth: true, roles: ['teacher'] }
      },
      {
        path: '/exams/:id/edit',
        name: 'ExamEdit',
        component: () => import('../views/teacher/ExamEditor.vue'),
        meta: { requiresAuth: true, roles: ['teacher'] }
      },
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
        path: '/forgot-password',
        name: 'forgot-password',
        component: ForgotPassword
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
          path: '/student/courses',
          name: 'student-courses',
          component: () => import('../views/student/Courses.vue')
        },
        // Teacher Routes
        {
          path: '/teacher/courses',
          name: 'teacher-courses',
          component: () => import('../views/teacher/Courses.vue')
        },
        {
          path: '/assignments/:id',
          name: 'assignment-detail',
          component: () => import('../views/common/AssignmentDetail.vue'),
          meta: { requiresAuth: true, roles: ['student', 'teacher'] },
          props: true
        },
        {
          path: '/exams/:id/notice',
          name: 'ExamNotice',
          component: () => import('../views/common/ExamNotice.vue'),
          meta: { requiresAuth: true, roles: ['student'] }
        },
        {
          path: '/exams/:id',
          name: 'ExamDetail',
          component: () => import('../views/common/ExamDetail.vue'),
          meta: { requiresAuth: true, roles: ['student', 'teacher'] }
        },
        {
          path: '/courses/:id',
          name: 'course-detail',
          component: () => import('../views/common/CourseDetail.vue'),
          redirect: to => ({ name: 'course-tasks', params: { id: to.params.id } }),
          async beforeEnter(to, from, next) {
            const userStore = useUserStore();
            if (!userStore.isAuthenticated) {
              await userStore.fetchUser();
            }
            next();
          },
          children: [
            {
              path: 'tasks',
              name: 'course-tasks',
              component: () => import('@/views/common/TaskManager.vue') // 假设任务组件路径
            },
            {
              path: 'tasks/:checkinId',
              name: 'checkin-detail',
              component: () => import('@/views/common/CheckinDetail.vue'),
              props: true
            },
            {
              path: 'votes/:voteId',
              name: 'vote-detail',
              component: () => import('@/views/common/VoteDetail.vue'),
              props: true
            },
            {
              path: 'question/:taskId',
              name: 'QuestionDetail',
              component: () => import('../views/common/QuestionDetail.vue')
            },
            {
              path: 'tasks/:taskId/random-question',
              name: 'RandomQuestionDetail',
              component: () => import('@/views/common/RandomQuestionDetail.vue')
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
              name: 'chapter-manager',
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
            },
            {
              path: 'sections/:sectionId',
              name: 'section-detail',
              component: () => import('../views/common/SectionDetail.vue'),
              props: true
            },
            {
              path: 'assignments',
              name: 'course-assignments',
              component: () => import('@/views/common/AssignmentManager.vue')
            },
            {
              path: 'exams',
              name: 'course-exams',
              component: () => import('@/views/common/ExamManager.vue')
            },
            {
              path: 'learning-records',
              name: 'course-learning-records',
              component: () => import('@/views/common/LearningRecord.vue')
            }
            // 其他子路由可以根据需要在这里添加
          ]
        },
        // Admin Routes
        {
          path: '/admin/users',
          name: 'admin-users',
          component: () => import('../views/admin/Users.vue')
        },
        {
          path: '/admin/statistics',
          name: 'admin-statistics',
          component: () => import('../views/admin/Statistics.vue')
        },
        {
          path: '/admin/logs',
          name: 'admin-logs',
          component: () => import('../views/admin/LogView.vue')
        }
      ]
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();
  const accessToken = localStorage.getItem('access_token');

  // 1. 如果 store 中没有用户信息但存在 token，则先获取用户信息
  if (accessToken && !userStore.user) {
    try {
      await userStore.fetchUser();
    } catch (error) {
      // 获取用户信息失败（例如 token 失效），清除 token 并重定向到登录页
      userStore.logout();
      return next('/login');
    }
  }

  const userRole = userStore.user?.role;

  // 2. 已登录用户访问登录/注册页 -> 重定向到主页
  if (userStore.isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    switch (userRole) {
      case 'student':
        return next('/student/courses');
      case 'teacher':
        return next('/teacher/courses');
      case 'admin':
        return next('/admin/users');
      default:
        userStore.logout();
        return next('/login');
    }
  }

  // 3. 访问需要认证的路由
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!userStore.isAuthenticated) {
      // 未登录 -> 重定向到登录页
      return next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
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
            userStore.logout();
            return next('/login');
        }
      }
      // 访问其他受保护路由 -> 放行
      return next();
    }
  }

  // 4. 访问公共路由 -> 放行
  next();
});

export default router
