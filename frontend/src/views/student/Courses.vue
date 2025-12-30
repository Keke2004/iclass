<template>
  <div class="course-list-container">
    <div class="header">
      <h1>我的课程</h1>
      <el-input
        v-model="searchQuery"
        placeholder="搜索课程"
        clearable
        style="width: 240px;"
      ></el-input>
    </div>

    <div v-if="loading" class="loading-state">
      <p>正在加载课程...</p>
    </div>

    <div v-else-if="filteredCourses.length === 0" class="empty-state">
      <p>没有找到匹配的课程。</p>
    </div>

    <el-row :gutter="20" v-else>
      <el-col :span="8" v-for="course in filteredCourses" :key="course.id">
        <course-card :course="course" @click="navigateToCourse(course.id)">
        </course-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage } from 'element-plus';
import CourseCard from '../../components/CourseCard.vue';

interface Teacher {
  id: number;
  username: string;
  role: string;
}

interface Course {
  id: number;
  name: string;
  description: string;
  teacher: Teacher;
}

const courses = ref<Course[]>([]);
const loading = ref(true);
const router = useRouter();
const searchQuery = ref('');

const filteredCourses = computed(() => {
  if (!searchQuery.value) {
    return courses.value;
  }
  const query = searchQuery.value.toLowerCase();
  return courses.value.filter(course =>
    course.name.toLowerCase().includes(query) ||
    course.description.toLowerCase().includes(query)
  );
});

const navigateToCourse = (courseId: number) => {
  router.push({ name: 'course-detail', params: { id: courseId } });
};

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
.loading-state, .empty-state {
  text-align: center;
  color: #909399;
  padding: 40px;
}
</style>
