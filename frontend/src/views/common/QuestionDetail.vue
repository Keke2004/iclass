<template>
  <div class="question-detail-container">
    <div v-if="isLoading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>
    <div v-else>
      <RandomQuestionPicker
          v-if="showPicker && question"
          :students="allStudents"
          :selected-student="question.student"
          @finished="handlePickerFinished"
      />
      <el-card v-if="!showPicker && question">
        <template #header>
          <div class="card-header">
            <span>随机提问</span>
            <el-button
                v-if="isTeacher"
                type="danger"
                @click="deleteQuestion"
                :loading="isDeleting"
            >
              删除提问
            </el-button>
          </div>
        </template>
        <div class="detail-item">
          <strong>状态:</strong>
          <el-tag :type="question.is_active ? 'success' : 'info'">
            {{ question.is_active ? '进行中' : '已结束' }}
          </el-tag>
        </div>
        <div class="detail-item">
          <strong>发起时间:</strong> {{ new Date(question.created_at).toLocaleString() }}
        </div>
        <div class="detail-item">
          <strong>被提问学生:</strong>
          <span class="selected-student">{{ question.student.username }}</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getRandomQuestionDetail, deleteRandomQuestion, getCourseMembers } from '@/services/api';
import type { RandomQuestion, User } from '@/types';
import { ElMessage, ElMessageBox } from 'element-plus';
import RandomQuestionPicker from '@/components/RandomQuestionPicker.vue';

const route = useRoute();
const router = useRouter();
const question = ref<RandomQuestion | null>(null);
const isDeleting = ref(false);
const allStudents = ref<User[]>([]);
const showPicker = ref(false);
const isLoading = ref(true);

const courseId = Number(route.params.id);
const taskId = Number(route.params.taskId);

const userRole = localStorage.getItem('user_role');
const isTeacher = computed(() => userRole === 'teacher');

const fetchInitialData = async () => {
  isLoading.value = true;
  try {
    const [questionResponse, membersResponse] = await Promise.all([
      getRandomQuestionDetail(courseId, taskId),
      getCourseMembers(courseId)
    ]);
    question.value = questionResponse.data;
    allStudents.value = membersResponse.data.students;

    if (question.value && allStudents.value.length > 0) {
      showPicker.value = true;
    }
  } catch (error) {
    console.error('获取初始数据失败', error);
    ElMessage.error('获取页面数据失败');
  } finally {
    isLoading.value = false;
  }
};

const handlePickerFinished = () => {
  showPicker.value = false;
};

const deleteQuestion = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这个提问吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });

    isDeleting.value = true;
    await deleteRandomQuestion(courseId, taskId);
    ElMessage.success('提问删除成功');
    router.push({ name: 'course-tasks', params: { id: courseId } });
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除提问失败', error);
      ElMessage.error('删除提问失败');
    }
  } finally {
    isDeleting.value = false;
  }
};

onMounted(fetchInitialData);
</script>

<style scoped>
.question-detail-container {
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
}
.loading-container {
  width: 100%;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.detail-item {
  margin-bottom: 15px;
  font-size: 16px;
}
.detail-item strong {
  margin-right: 10px;
}
.selected-student {
  font-weight: bold;
  color: #409eff;
  font-size: 1.2em;
}
</style>
