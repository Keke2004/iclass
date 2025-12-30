<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="logo">
        <span>智慧课堂</span>
      </div>
      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="el-dropdown-link">
            <el-avatar :size="32" class="user-avatar">{{ username.charAt(0).toUpperCase() }}</el-avatar>
            <span class="username-text">{{ username }}</span>
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container>
      <el-aside width="240px" class="layout-aside">
        <div class="aside-profile">
          <el-avatar :size="80" class="aside-avatar">{{ username.charAt(0).toUpperCase() }}</el-avatar>
          <p class="aside-username">{{ username }}</p>
        </div>
        <el-menu
          :default-active="$route.path"
          class="el-menu-vertical-demo"
          router
          background-color="#34495E"
          text-color="#a7b1c2"
          active-text-color="#fff"
        >
          <!-- 学生菜单 -->
          <template v-if="userRole === 'student'">
            <el-menu-item index="/student/courses">
              <el-icon><management /></el-icon>
              <span>我的课程</span>
            </el-menu-item>
          </template>

          <!-- 教师菜单 -->
          <template v-if="userRole === 'teacher'">
            <el-menu-item index="/teacher/courses">
              <el-icon><management /></el-icon>
              <span>课程列表</span>
            </el-menu-item>
          </template>

          <!-- 管理员菜单 -->
          <template v-if="userRole === 'admin'">
            <el-menu-item index="/admin/users">
              <el-icon><user /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/statistics">
              <el-icon><data-line /></el-icon>
              <span>数据统计</span>
            </el-menu-item>
            <el-menu-item index="/admin/logs">
              <el-icon><tickets /></el-icon>
              <span>日志管理</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import {
  ArrowDown,
  Management,
  User,
  DataLine,
  Tickets,
  Document,
} from '@element-plus/icons-vue';

const router = useRouter();

// 从localStorage获取用户信息
const userRole = ref(localStorage.getItem('user_role'));
const username = ref(localStorage.getItem('username') || '用户');

// 根据角色计算首页路径
const homePath = computed(() => {
  switch (userRole.value) {
    case 'student':
      return '/student/dashboard';
    case 'teacher':
      return '/teacher/dashboard';
    case 'admin':
      return '/admin/dashboard';
    default:
      return '/';
  }
});

// 处理下拉菜单命令
const handleCommand = (command: string | number | object) => {
  if (command === 'logout') {
    // 清除所有登录信息
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username'); // 如果有保存用户名
    // 跳转到登录页
    router.push('/login');
  } else if (command === 'profile') {
    // 跳转到个人中心页，路径待定
    router.push('/profile');
  }
};
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #7A88FF; /* Updated background color from image */
  color: #fff; /* Updated text color */
  border-bottom: none;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  padding-left: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-right: 20px;
}


.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #fff; /* Ensure dropdown link text is white */
}

.username-text {
  margin: 0 8px;
}

.user-avatar {
  background-color: rgba(255, 255, 255, 0.8);
  color: #5468ff;
  font-weight: bold;
}

.layout-aside {
  background-color: #34495E; /* Updated sidebar background from image */
  border-right: none;
  display: flex;
  flex-direction: column;
}

.aside-profile {
  padding: 30px 20px;
  text-align: center;
  color: #fff;
}

.aside-avatar {
  width: 80px;
  height: 80px;
  font-size: 40px;
  margin-bottom: 15px;
  background-color: rgba(255, 255, 255, 0.1);
}

.aside-username {
  font-size: 18px;
  font-weight: bold;
}

.el-menu-vertical-demo {
  border-right: none;
  flex-grow: 1;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 240px;
}

.el-menu-item:hover, .el-sub-menu__title:hover {
    background-color: #2c3e50 !important;
}

.el-menu-item.is-active {
  background-color: #409EFF !important;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
  display: flex;
  flex-direction: column;
}
</style>
