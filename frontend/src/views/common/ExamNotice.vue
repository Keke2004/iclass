<template>
  <div class="exam-notice-container">
    <el-card class="notice-card" v-if="!loading && exam">
      <template #header>
        <div class="card-header">
          <h1>{{ exam.title }}</h1>
        </div>
      </template>
      <div class="notice-content">
        <h2>考试须知</h2>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="考试说明">{{ exam.description || '无' }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(exam.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDate(exam.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="考试时长">{{ exam.time_limit }} 分钟</el-descriptions-item>
          <el-descriptions-item label="总分">{{ exam.total_points }} 分</el-descriptions-item>
        </el-descriptions>
        <div class="actions">
          <el-button type="primary" size="large" @click="handleStartExam" :loading="isStarting" :disabled="!canStart">
            {{ startButtonText }}
          </el-button>
        </div>
      </div>
    </el-card>
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getExam, startExam } from '@/services/api';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const examId = Number(route.params.id);

const loading = ref(true);
const isStarting = ref(false);
const exam = ref<any>(null);
const now = ref(new Date());

onMounted(async () => {
  if (!examId) return;
  try {
    const res = await getExam(examId);
    exam.value = {
      ...res.data,
      total_points: res.data.questions.reduce((sum: number, q: any) => sum + q.points, 0)
    };
  } catch (error) {
    ElMessage.error('获取考试信息失败');
  } finally {
    loading.value = false;
  }
  setInterval(() => {
    now.value = new Date();
  }, 1000);
});

const canStart = computed(() => {
  if (!exam.value) return false;
  const startTime = new Date(exam.value.start_time);
  const endTime = new Date(exam.value.end_time);
  return now.value >= startTime && now.value <= endTime;
});

const startButtonText = computed(() => {
  if (!exam.value) return '加载中...';
  const startTime = new Date(exam.value.start_time);
  if (now.value < startTime) {
    return '考试未开始';
  }
  if (now.value > new Date(exam.value.end_time)) {
    return '考试已结束';
  }
  return '我已阅读并同意，开始考试';
});

const handleStartExam = async () => {
  isStarting.value = true;
  try {
    const response = await startExam(examId);
    const submissionId = response.data.id;
    router.push({ name: 'ExamDetail', params: { id: examId }, query: { submissionId: submissionId } });
  } catch (error: any) {
    if (error.response && error.response.status === 400) {
        const submissionId = error.response.data.submission_id;
        if (submissionId) {
            ElMessage.info('您已完成该考试，正在跳转到提交详情...');
            router.push({ name: 'ExamDetail', params: { id: examId }, query: { submissionId: submissionId } });
        } else {
            ElMessage.error(error.response.data.detail || '开始考试失败，请重试');
        }
    } else {
        ElMessage.error('开始考试失败，请重试');
    }
  } finally {
    isStarting.value = false;
  }
};

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
};
</script>

<style scoped>
.exam-notice-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background-color: #f4f5f7;
  padding: 20px;
}
.notice-card {
  width: 100%;
  max-width: 800px;
}
.card-header h1 {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  margin: 0;
}
.notice-content h2 {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 20px;
  text-align: center;
}
.actions {
  text-align: center;
  margin-top: 30px;
}
.loading-state {
  width: 100%;
  max-width: 800px;
}
</style>
