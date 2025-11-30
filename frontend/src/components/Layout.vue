<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="logo" />
        <span>智慧课堂</span>
      </div>
      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="el-dropdown-link">
            <el-avatar :size="32" class="user-avatar">{{ username.charAt(0).toUpperCase() }}</el-avatar>
            <span>{{ username }}</span>
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
      <el-aside width="200px" class="layout-aside">
        <el-menu :default-active="$route.path" class="el-menu-vertical-demo" router>
          <!-- 公共菜单 -->
          <el-menu-item :index="homePath">
            <el-icon><home-filled /></el-icon>
            <span>首页</span>
          </el-menu-item>

          <!-- 学生菜单 -->
          <template v-if="userRole === 'student'">
            <el-menu-item index="/student/courses">
              <el-icon><management /></el-icon>
              <span>我的课程</span>
            </el-menu-item>
          </template>

          <!-- 教师菜单 -->
          <template v-if="userRole === 'teacher'">
            <el-sub-menu index="teacher-courses">
              <template #title>
                <el-icon><management /></el-icon>
                <span>课程管理</span>
              </template>
              <el-menu-item index="/teacher/courses">课程列表</el-menu-item>
              <el-menu-item index="/teacher/courses/create">创建课程</el-menu-item>
            </el-sub-menu>
          </template>

          <!-- 管理员菜单 -->
          <template v-if="userRole === 'admin'">
            <el-menu-item index="/admin/users">
              <el-icon><user /></el-icon>
              <span>用户管理</span>
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
  HomeFilled,
  Management,
  User,
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
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 10px;
}

.user-info {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.user-avatar {
  margin-right: 8px;
}

.layout-aside {
  background-color: #fff;
  border-right: 1px solid #dcdfe6;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.layout-main {
  padding: 20px;
  background-color: #f0f2f5;
}
</style>
