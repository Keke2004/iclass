<template>
  <div class="feedback-manager">
    <div class="header">
      <h1>教学反馈</h1>
      <el-button v-if="isTeacher" type="primary" @click="createQuestionnaire">创建新反馈</el-button>
    </div>

    <div v-if="questionnaires.length > 0">
      <div class="task-list">
        <div v-for="q in questionnaires" :key="q.id" class="task-item" @click="handleFeedbackClick(q)">
          <div class="task-info">
            <div class="task-icon-wrapper status-ongoing">
              <div class="task-icon">反馈</div>
            </div>
            <div class="task-title">{{ q.title }}</div>
            <div class="task-time">创建于: {{ new Date(q.created_at).toLocaleString() }}</div>
          </div>
        </div>
      </div>
    </div>
    <el-empty v-else description="暂无反馈问卷"></el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import apiClient from '../../services/api';
import { useUserStore } from '../../stores/user';
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const questionnaires = ref([]);
const courseId = computed(() => route.params.id as string);
const isTeacher = computed(() => userStore.isTeacher);

const fetchQuestionnaires = async () => {
  try {
    const response = await apiClient.get('/questionnaires/', {
      params: { course_id: courseId.value }
    });
    questionnaires.value = response.data;
  } catch (error) {
    ElMessage.error('无法加载反馈列表');
    console.error(error);
  }
};

const createQuestionnaire = () => {
  router.push({ name: 'course-feedback-create', params: { id: courseId.value } });
};

const handleFeedbackClick = (questionnaire: any) => {
  if (isTeacher.value) {
    router.push({ name: 'course-feedback-results', params: { id: courseId.value, feedbackId: questionnaire.id } });
  } else {
    router.push({ name: 'course-feedback-fill', params: { id: courseId.value, feedbackId: questionnaire.id } });
  }
};

onMounted(fetchQuestionnaires);
</script>

<style scoped>
.feedback-manager {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.task-list {
  background-color: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  transition: background-color 0.3s;
  cursor: pointer;
}
.task-info {
  display: flex;
  align-items: center;
  flex-grow: 1;
}
.task-item:not(:last-child) {
  border-bottom: 1px solid #e8e8e8;
}
.task-item:hover {
  background-color: #f5f7fa;
}
.task-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}
.task-icon {
  color: #fff;
  font-size: 14px;
}
.status-ongoing {
  background-color: #409eff; /* Blue for ongoing */
}
.task-title {
  flex-grow: 1;
  font-size: 16px;
  color: #333;
}
.task-time {
  font-size: 14px;
  color: #999;
  margin-left: 15px;
}
</style>
