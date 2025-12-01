<template>
  <div class="course-detail-container">
    <div v-if="loading" class="loading-state">
      <p>正在加载课程详情...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="course">
      <el-container class="course-layout">
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
          <component :is="currentComponent"></component>
          <!-- 其他模块的占位符 -->
        </el-main>
      </el-container>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, shallowRef } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../services/api';
import ChapterManager from './ChapterManager.vue';
import AnnouncementManager from './AnnouncementManager.vue';
import MemberManager from './MemberManager.vue';
import { ElMessage, ElContainer, ElAside, ElMain, ElMenu, ElMenuItem, ElIcon, ElButton } from 'element-plus';
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
const activeMenu = ref('tasks');
const currentComponent = shallowRef(null);

const courseId = route.params.id;

const handleMenuSelect = (index: string) => {
  activeMenu.value = index;
  if (index === 'chapters') {
    currentComponent.value = ChapterManager;
  } else if (index === 'announcements') {
    currentComponent.value = AnnouncementManager;
  } else if (index === 'members') {
    currentComponent.value = MemberManager;
  } else {
    currentComponent.value = null;
  }
  // 未来这里可以与子路由结合
};

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
  router.back();
};

onMounted(() => {
  fetchCourseDetail();
});
</script>

<style scoped>
.course-detail-container {
  height: calc(100vh - 60px); /* 减去顶部导航栏的高度 */
}
.loading-state, .error-state {
  text-align: center;
  color: #909399;
  padding: 40px;
}
.course-layout {
  height: 100%;
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
}
.course-content {
  padding: 20px;
}
</style>
