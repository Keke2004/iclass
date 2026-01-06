<template>
  <div class="random-question-detail-container">
    <el-page-header @back="goBack" content="随机提问"></el-page-header>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <div v-else-if="question" class="content-wrapper">
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        <div class="info-item">
          <span class="label">状态:</span>
          <el-tag :type="statusTagType" effect="dark" size="small">{{ statusText }}</el-tag>
        </div>
        <div class="info-item">
          <span class="label">发起时间:</span>
          <span>{{ new Date(question.created_at).toLocaleString() }}</span>
        </div>
      </el-card>

      <el-card v-if="isTeacher" class="action-card">
        <template #header>
          <div class="card-header">
            <span>操作</span>
          </div>
        </template>
        <div class="actions">
          <el-button @click="startDraw" :disabled="isDrawing || question.status === 'finished'" type="primary">
            {{ isDrawing ? '抽选中...' : '开始抽选' }}
          </el-button>
          <el-button @click="deleteQuestion" type="danger">删除提问</el-button>
        </div>
      </el-card>

      <el-card v-if="showPicker" class="picker-card">
        <RandomQuestionPicker
          :students="students"
          :selected-student="question.student"
          @finished="onAnimationFinished"
        />
      </el-card>

      <el-card v-if="question.status === 'finished' && question.student && showFinalResult" class="result-card">
        <template #header>
          <div class="card-header">
            <span>抽选结果</span>
          </div>
        </template>
        <div class="selected-student">
          <p class="student-name">{{ question.student.username }}</p>
          <p class="congrats">🎉 恭喜这位同学！ 🎉</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, ElPageHeader, ElCard, ElButton, ElTag } from 'element-plus';
import api from '@/services/api';
import type { RandomQuestion, User } from '@/types';
import RandomQuestionPicker from '@/components/RandomQuestionPicker.vue';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();

const userStore = useUserStore();
const isTeacher = computed(() => userStore.isTeacher);
const loading = ref(true);
const error = ref('');
const question = ref<RandomQuestion | null>(null);
const students = ref<User[]>([]);
const isDrawing = ref(false);
const showPicker = ref(false);
const showFinalResult = ref(false);

const courseId = computed(() => route.params.id as string);
const questionId = computed(() => route.params.taskId as string);

const statusText = computed(() => {
  if (question.value?.status === 'ongoing') return '进行中';
  if (question.value?.status === 'finished') return '已结束';
  return '未知';
});

const statusTagType = computed(() => {
  if (question.value?.status === 'ongoing') return 'warning';
  if (question.value?.status === 'finished') return 'success';
  return 'info';
});

const goBack = () => {
  router.back();
};

const loadPageData = async () => {
  loading.value = true;
  error.value = '';
  try {
    // First, get the user role. This is critical for the UI.
    await userStore.fetchUser();

    // Then, fetch the other data in parallel.
    const [questionResponse, membersResponse] = await Promise.all([
      api.get(`/courses/${courseId.value}/random-questions/${questionId.value}/`),
      api.get(`/courses/${courseId.value}/members/`)
    ]);

    question.value = questionResponse.data;
    if (question.value?.status === 'finished') {
      showFinalResult.value = true;
    }
    students.value = membersResponse.data.students;

  } catch (err) {
    error.value = '无法加载页面数据，请稍后重试。';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const startDraw = async () => {
  isDrawing.value = true;
  showPicker.value = true;
  showFinalResult.value = false;
  try {
    const response = await api.post(`/courses/${courseId.value}/random-questions/${questionId.value}/draw/`);
    question.value = response.data;
  } catch (err) {
    ElMessage.error('抽选失败，请稍后重试。');
    console.error(err);
    isDrawing.value = false;
    showPicker.value = false;
  }
};

const onAnimationFinished = () => {
  showPicker.value = false;
  isDrawing.value = false;
  showFinalResult.value = true;
};

const deleteQuestion = () => {
  ElMessageBox.confirm('确定要删除本次提问吗？此操作不可恢复。', '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'error',
  }).then(async () => {
    try {
      await api.delete(`/courses/${courseId.value}/random-questions/${questionId.value}/`);
      ElMessage.success('提问已删除');
      goBack();
    } catch (err) {
      ElMessage.error('删除失败，请稍后重试。');
      console.error(err);
    }
  }).catch(() => {
    // 用户取消操作
  });
};

onMounted(() => {
  loadPageData();
});
</script>

<style scoped>
.random-question-detail-container {
  padding: 20px;
}

.content-wrapper {
  margin-top: 20px;
}

.el-card {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: bold;
  color: #555;
  margin-right: 1rem;
  min-width: 70px;
}

.result-card .selected-student {
  text-align: center;
}

.result-card .student-name {
  font-size: 2.5rem;
  font-weight: bold;
  color: #d32f2f;
  margin: 10px 0;
}

.result-card .congrats {
  font-size: 1.2rem;
  color: #555;
  margin-top: 0.5rem;
}

.action-card .actions {
  display: flex;
  gap: 10px;
}

.loading, .error-message {
  text-align: center;
  font-size: 1.2rem;
  padding: 2rem;
  color: #909399;
}

.error-message {
  color: #f56c6c;
}

.picker-card {
  border: 2px dashed #409eff;
}
</style>
