<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="logo" />
        <span>智慧课堂</span>
      </div>
      <div class="user-info">
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-avatar :size="32" class="user-avatar">U</el-avatar>
            <span>用户名</span>
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>个人中心</el-dropdown-item>
              <el-dropdown-item divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="layout-aside">
        <el-menu
          default-active="1"
          class="el-menu-vertical-demo"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><home-filled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-sub-menu index="2">
            <template #title>
              <el-icon><management /></el-icon>
              <span>课程管理</span>
            </template>
            <el-menu-item index="/courses">课程列表</el-menu-item>
            <el-menu-item index="/courses/create">创建课程</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import {
  ArrowDown,
  HomeFilled,
  Management,
} from '@element-plus/icons-vue';
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
