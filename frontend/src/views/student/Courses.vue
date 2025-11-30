<template>
  <div class="course-list-container">
    <div class="header">
      <h1>我的课程</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <p>正在加载课程...</p>
    </div>

    <div v-else-if="courses.length === 0" class="empty-state">
      <p>您还没有加入任何课程。</p>
    </div>

    <el-row :gutter="20" v-else>
      <el-col :span="8" v-for="course in courses" :key="course.id">
        <el-card class="course-card">
          <template #header>
            <div class="card-header">
              <span>{{ course.name }}</span>
            </div>
          </template>
          <p class="course-description">{{ course.description }}</p>
          <div class="card-footer">
            <el-button type="primary" link>进入课程</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../../services/api';
import { ElMessage } from 'element-plus';

interface Course {
  id: number;
  name: string;
  description: string;
  teacher: number;
}

const courses = ref<Course[]>([]);
const loading = ref(true);

const fetchEnrolledCourses = async () => {
  try {
    const response = await apiClient.get('/courses/');
    courses.value = response.data;
  } catch (error) {
    console.error('获取已加入课程列表失败:', error);
    ElMessage.error('无法加载课程列表，请稍后重试。');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchEnrolledCourses();
});
</script>

<style scoped>
.course-list-container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.course-card {
  margin-bottom: 20px;
}
.card-header {
  font-weight: bold;
}
.course-description {
  color: #606266;
  font-size: 14px;
  min-height: 60px;
}
.card-footer {
  text-align: right;
  margin-top: 10px;
}
.loading-state, .empty-state {
  text-align: center;
  color: #909399;
  padding: 40px;
}
</style>
