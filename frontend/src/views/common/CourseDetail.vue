<template>
  <div class="course-detail-container">
    <div v-if="loading" class="loading-state">
      <p>正在加载课程详情...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    <el-container v-else-if="course" class="course-layout">
      <!-- 左侧边栏 -->
      <el-aside width="250px" class="course-sidebar">
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

      <!-- 右侧内容区 -->
      <el-container class="main-content-container">
        <!-- 章节视图 -->
        <template v-if="activeMenu === 'chapters'">
          <el-aside width="300px" class="chapter-list-sidebar">
            <ChapterManager :course-id="courseId" @select-chapter="handleChapterSelect" />
          </el-aside>
          <el-main class="chapter-content-main">
            <div v-if="selectedChapter" class="chapter-content-display">
              <h3>{{ selectedChapter.title }}</h3>
              
              <!-- 富文本内容 -->
              <div v-if="selectedChapter.content" v-html="selectedChapter.content" class="rich-text-content"></div>

              <!-- 视频播放器 -->
              <div v-if="selectedChapter.video" class="media-container">
                <h4>视频</h4>
                <video controls :src="selectedChapter.video" class="video-player"></video>
              </div>

              <!-- PDF 预览 -->
              <div v-if="selectedChapter.pdf" class="media-container">
                <h4>PDF 文档</h4>
                <embed :src="selectedChapter.pdf" type="application/pdf" class="pdf-viewer" />
              </div>

            </div>
            <div v-else class="chapter-placeholder">
              <p>请在左侧选择一个章节来查看内容。</p>
            </div>
          </el-main>
        </template>
        <!-- 其他视图 -->
        <el-main v-else class="course-content">
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../services/api';
import ChapterManager from './ChapterManager.vue';
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

interface Chapter {
  id: number;
  title: string;
  content: string;
  video?: string;
  pdf?: string;
  children?: Chapter[];
}

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
const courseId = computed(() => route.params.id as string);
const activeMenu = ref('tasks');
const selectedChapter = ref<Chapter | null>(null);

const routeNameToMenuIndex: { [key: string]: string } = {
  'course-tasks': 'tasks',
  'course-discussions': 'discussions',
  'course-chapters': 'chapters',
  'course-members': 'members',
  'course-announcements': 'announcements',
  'course-materials': 'materials',
};

const handleMenuSelect = (index: string) => {
  if (index === 'chapters') {
    activeMenu.value = 'chapters';
    // 更新URL，但不完全依赖路由来管理状态
    router.push({ name: 'course-chapters', params: { id: courseId.value } });
  } else {
    const menuIndexToRouteName: { [key: string]: string } = {
      tasks: 'course-tasks',
      discussions: 'course-discussions',
      members: 'course-members',
      announcements: 'course-announcements',
      materials: 'course-materials',
    };
    const routeName = menuIndexToRouteName[index];
    if (routeName) {
      router.push({ name: routeName, params: { id: courseId.value } });
    }
  }
};

const handleChapterSelect = (chapter: Chapter) => {
  selectedChapter.value = chapter;
};

watch(
  () => route.name,
  (newName) => {
    const menuIndex = routeNameToMenuIndex[newName as string];
    if (menuIndex) {
      activeMenu.value = menuIndex;
    }
  },
  { immediate: true }
);

const fetchCourseDetail = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId.value}/`);
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
  height: calc(100vh - 60px); /* 假设顶部导航栏高度为 60px */
}
.loading-state, .error-state {
  text-align: center;
  color: #909399;
  padding: 40px;
}
.course-layout {
  flex-grow: 1;
  display: flex;
  height: 100%;
}
.course-sidebar {
  background-color: #f4f6f8;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  height: 100%;
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
.main-content-container {
  display: flex;
  flex-grow: 1;
  height: 100%;
}
.chapter-list-sidebar {
  border-right: 1px solid #e0e0e0;
  height: 100%;
  overflow-y: auto;
}
.chapter-content-main {
  padding: 20px;
  overflow-y: auto;
  height: 100%;
}
.chapter-placeholder {
  text-align: center;
  color: #909399;
  padding-top: 50px;
}
.chapter-content-display h3 {
  margin-top: 0;
  margin-bottom: 20px;
}
.rich-text-content {
  line-height: 1.8;
  margin-bottom: 20px;
}
.media-container {
  margin-top: 30px;
}
.media-container h4 {
  margin-bottom: 10px;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}
.video-player {
  width: 100%;
  max-width: 800px;
  border-radius: 8px;
}
.pdf-viewer {
  width: 100%;
  height: 800px;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.course-content {
  padding: 20px;
  overflow: auto;
  height: 100%;
}
</style>
