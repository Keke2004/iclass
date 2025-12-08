<template>
  <div class="course-detail-container">
    <div v-if="loading" class="loading-state">
      <p>正在加载课程详情...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    <el-container v-else-if="course" class="course-layout">
        <el-aside width="200px" class="course-sidebar">
          <div class="course-title-container">
            <h2 class="course-title">{{ course.name }}</h2>
            <el-button type="primary" link @click="goBack">返回课程列表</el-button>
          </div>
          <el-menu :default-active="activeMenu" class="course-menu" @select="handleMenuSelect">
            <el-menu-item index="tasks">
              <el-icon><el-icon-menu /></el-icon>
              <span>任务</span>
            </el-menu-item>
            <el-menu-item index="chapters">
              <el-icon><el-icon-notebook /></el-icon>
              <span>章节</span>
            </el-menu-item>
            <el-menu-item index="discussions">
              <el-icon><el-icon-chat-dot-round /></el-icon>
              <span>讨论</span>
            </el-menu-item>
            <el-menu-item index="assignments">
              <el-icon><el-icon-edit-pen /></el-icon>
              <span>作业</span>
            </el-menu-item>
            <el-menu-item index="exams">
              <el-icon><el-icon-finished /></el-icon>
              <span>考试</span>
            </el-menu-item>
            <el-menu-item index="announcements">
              <el-icon><el-icon-bell /></el-icon>
              <span>公告</span>
            </el-menu-item>
            <el-menu-item index="materials">
              <el-icon><el-icon-folder /></el-icon>
              <span>课程资料</span>
            </el-menu-item>
            <el-menu-item index="members">
              <el-icon><el-icon-user /></el-icon>
              <span>成员</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main class="course-content">
          <router-view></router-view>
        </el-main>
      </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watchEffect } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../services/api';
import {
  Menu as ElIconMenu,
  Notebook as ElIconNotebook,
  ChatDotRound as ElIconChatDotRound,
  EditPen as ElIconEditPen,
  Finished as ElIconFinished,
  Bell as ElIconBell,
  Folder as ElIconFolder,
  User as ElIconUser
} from '@element-plus/icons-vue';
import { ElMessage, ElContainer, ElAside, ElMain, ElMenu, ElMenuItem, ElIcon, ElButton } from 'element-plus';

interface Course {
  id: number;
  name: string;
  description: string;
}

const route = useRoute();
const router = useRouter();
const course = ref<Course | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const activeMenu = ref('tasks'); // 默认激活任务区
const courseId = route.params.id as string;

// 路由名称到菜单索引的映射
const routeNameToMenuIndex: { [key: string]: string } = {
  'course-tasks': 'tasks',
  'course-discussions': 'discussions',
  'course-chapters': 'chapters',
  'course-members': 'members',
  'course-announcements': 'announcements',
  // 其他映射
};

const handleMenuSelect = (index: string) => {
  // 菜单索引到路由名称的映射
  const menuIndexToRouteName: { [key: string]: string } = {
    tasks: 'course-tasks',
    discussions: 'course-discussions',
    chapters: 'course-chapters',
    members: 'course-members',
    announcements: 'course-announcements',
    // 其他映射
  };
  const routeName = menuIndexToRouteName[index];
  if (routeName) {
    router.push({ name: routeName, params: { id: courseId } });
  }
};

// 监听路由变化，更新激活的菜单项
watchEffect(() => {
  const currentRouteName = route.name as string;
  const menuIndex = routeNameToMenuIndex[currentRouteName];
  if (menuIndex) {
    activeMenu.value = menuIndex;
  }
});

const fetchCourseDetail = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId}/`);
    course.value = response.data;
  } catch (err) {
    console.error('获取课程详情失败:', err);
    error.value = '无法加载课程详情，请稍后重试。';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  const userRole = localStorage.getItem('user_role');
  if (userRole === 'teacher') {
    router.push({ name: 'teacher-courses' });
  } else if (userRole === 'student') {
    router.push({ name: 'student-courses' });
  } else {
    // 如果没有角色信息，可以跳转到首页或登录页作为后备
    router.push('/');
  }
};

onMounted(() => {
  fetchCourseDetail();
});
</script>

<style scoped>
.course-detail-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}
.loading-state, .error-state {
  text-align: center;
  color: #909399;
  padding: 40px;
}
.course-layout {
  flex-grow: 1;
  display: flex;
}
.course-sidebar {
  background-color: #f4f6f8;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}
.course-title-container {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}
.course-title {
  margin: 0 0 10px 0;
  font-size: 1.2em;
}
.course-menu {
  border-right: none;
  flex-grow: 1;
  min-height: 0;
}
.course-content {
  padding: 20px;
  overflow: auto;
}
</style>
