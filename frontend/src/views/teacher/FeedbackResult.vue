<template>
  <div class="feedback-result-manager">
    <div v-if="questionnaire">
      <div class="header">
        <h1>{{ questionnaire.title }}</h1>
        <div class="action-buttons">
          <el-button @click="editQuestionnaire">编辑</el-button>
          <el-button type="danger" @click="deleteQuestionnaire">删除</el-button>
        </div>
      </div>

      <div class="content-wrapper">
        <div class="main-content">
          <div class="response-summary">
            <strong>{{ submittedCount }}</strong> 人已提交
          </div>
          <div v-if="selectedResponse" class="response-list">
            <el-card :key="selectedResponse.id" class="response-card">
              <template #header>
                <div class="card-header">
                  <span>{{ selectedResponse.student.username }}</span>
                  <span class="timestamp">提交于: {{ new Date(selectedResponse.submitted_at).toLocaleString() }}</span>
                </div>
              </template>
              <div class="response-body">
                <div v-for="answer in selectedResponse.answers" :key="answer.id" class="answer-item">
                  <p class="question-text">{{ getQuestionText(answer.question) }}</p>
                  <p class="answer-content">
                    <template v-if="getQuestionType(answer.question) === 'rating'">
                      <el-rate :model-value="answer.answer_rating" disabled />
                    </template>
                    <template v-else>
                      {{ answer.answer_text }}
                    </template>
                  </p>
                </div>
              </div>
            </el-card>
          </div>
          <el-empty v-else description="请从右侧列表中选择学生查看反馈详情"></el-empty>
        </div>

        <div class="sidebar">
          <el-card class="student-list-card">
            <template #header>
              <div class="card-header">
                <span>学生列表 ({{ submittedCount }} / {{ totalStudents }})</span>
              </div>
            </template>
            <el-table :data="questionnaire.student_statuses" height="400" class="student-status-table" @row-click="handleRowClick" :row-class-name="tableRowClassName">
              <el-table-column prop="student.username" label="姓名" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'submitted' ? 'success' : 'info'" size="small">
                    {{ row.status === 'submitted' ? '已提交' : '未提交' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </div>
    </div>
    <div v-else>
      <p>正在加载反馈详情...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage, ElMessageBox } from 'element-plus';

const route = useRoute();
const router = useRouter();
const questionnaire = ref<any>(null);
const courseId = route.params.id;
const feedbackId = route.params.feedbackId;

const selectedResponse = ref<any>(null);

const submittedCount = computed(() => {
  return questionnaire.value?.student_statuses.filter(s => s.status === 'submitted').length || 0;
});

const totalStudents = computed(() => {
  return questionnaire.value?.student_statuses.length || 0;
});

const fetchQuestionnaireDetail = async () => {
  try {
    const response = await apiClient.get(`/questionnaires/${feedbackId}/`);
    questionnaire.value = response.data;
  } catch (error) {
    ElMessage.error('无法加载反馈详情');
    console.error(error);
  }
};

const getQuestionText = (questionId: number) => {
  const question = questionnaire.value?.questions.find(q => q.id === questionId);
  return question ? question.text : '未知问题';
};

const getQuestionType = (questionId: number) => {
  const question = questionnaire.value?.questions.find(q => q.id === questionId);
  return question ? question.question_type : 'text';
};

const viewResponse = (response: any) => {
  selectedResponse.value = response;
};

const handleRowClick = (row: any) => {
  if (row.status === 'submitted') {
    if (selectedResponse.value && selectedResponse.value.id === row.response.id) {
      selectedResponse.value = null;
    } else {
      viewResponse(row.response);
    }
  }
};

const tableRowClassName = ({ row }) => {
  if (row.status === 'submitted') {
    return 'clickable-row';
  }
  return '';
};

const editQuestionnaire = () => {
  router.push({ name: 'course-feedback-edit', params: { id: courseId, feedbackId: feedbackId } });
};

const deleteQuestionnaire = async () => {
  try {
    await ElMessageBox.confirm('确定要删除此反馈问卷吗？这将同时删除所有相关的学生提交。', '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await apiClient.delete(`/questionnaires/${feedbackId}/`);
    ElMessage.success('删除成功');
    router.push({ name: 'course-feedback', params: { id: courseId } }); // Go back to the list
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
      console.error(error);
    }
  }
};

onMounted(fetchQuestionnaireDetail);
</script>

<style scoped>
.feedback-result-manager {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.action-buttons {
  display: flex;
  gap: 10px;
}
.content-wrapper {
  display: flex;
  gap: 20px;
}
.main-content {
  flex: 1;
}
.sidebar {
  width: 320px;
  flex-shrink: 0;
}
.student-list-card {
  border-radius: 8px;
}
.student-list-card .card-header {
  font-weight: bold;
}
.student-status-table {
  width: 100%;
}
:deep(.el-table .clickable-row) {
  cursor: pointer;
}
:deep(.el-table .clickable-row:hover) {
  background-color: #f5f7fa;
}
.response-summary {
  color: #606266;
  margin-bottom: 20px;
}
.response-list {
  display: grid;
  gap: 20px;
}
.response-card {
  border-radius: 8px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
.timestamp {
  font-size: 0.9em;
  color: #909399;
  font-weight: normal;
}
.answer-item {
  margin-bottom: 15px;
}
.answer-item:last-child {
  margin-bottom: 0;
}
.question-text {
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}
.answer-content {
  color: #555;
  padding-left: 10px;
}
</style>
