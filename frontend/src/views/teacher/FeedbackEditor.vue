<template>
  <div class="feedback-editor-container">
    <el-card class="editor-card">
      <template #header>
        <div class="card-header">
          <h1>{{ isEditMode ? '编辑' : '创建' }}反馈问卷</h1>
        </div>
      </template>
      <div class="form-wrapper">
      <el-form :model="form" label-position="top" class="feedback-form">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入问卷标题"></el-input>
        </el-form-item>

        <el-divider>问题列表</el-divider>

        <div v-for="(question, index) in form.questions" :key="index" class="question-item-card">
          <el-card>
            <template #header>
              <div class="question-header">
                <span>问题 {{ index + 1 }}</span>
                <el-button type="danger" :icon="Delete" circle @click="removeQuestion(index)"></el-button>
              </div>
            </template>
            <el-form-item label="问题内容">
              <el-input v-model="question.text" placeholder="输入问题内容"></el-input>
            </el-form-item>
            <el-form-item label="问题类型">
              <el-select v-model="question.question_type" placeholder="选择问题类型" style="width: 100%">
                <el-option label="评分题 (1-5分)" value="rating"></el-option>
                <el-option label="文本题" value="text"></el-option>
              </el-select>
            </el-form-item>
          </el-card>
        </div>

        <div class="form-actions">
          <el-button type="primary" plain @click="addQuestion">添加问题</el-button>
          <el-button type="success" @click="saveQuestionnaire">保存问卷</el-button>
        </div>
      </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage } from 'element-plus';
import { Delete } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const form = ref({
  title: '',
  questions: [] as { text: string; question_type: string }[],
  course: route.params.id
});
const isEditMode = computed(() => !!route.params.feedbackId);

const fetchQuestionnaire = async () => {
  if (isEditMode.value) {
    try {
      const response = await apiClient.get(`/questionnaires/${route.params.feedbackId}/`);
      form.value = { ...response.data, course: route.params.id };
    } catch (error) {
      ElMessage.error('无法加载问卷详情');
      console.error(error);
    }
  }
};

const addQuestion = () => {
  form.value.questions.push({ text: '', question_type: 'rating' });
};

const removeQuestion = (index: number) => {
  form.value.questions.splice(index, 1);
};

const saveQuestionnaire = async () => {
  try {
    if (isEditMode.value) {
      await apiClient.put(`/questionnaires/${route.params.feedbackId}/`, form.value);
      ElMessage.success('更新成功');
    } else {
      await apiClient.post('/questionnaires/', form.value);
      ElMessage.success('创建成功');
    }
    router.push({ name: 'course-feedback', params: { id: route.params.id } });
  } catch (error) {
    ElMessage.error('保存失败');
    console.error(error);
  }
};

onMounted(() => {
  fetchQuestionnaire();
  // 如果是新建模式，默认添加一个问题
  if (!isEditMode.value) {
    addQuestion();
  }
});
</script>

<style scoped>
.feedback-editor-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
  padding: 20px;
  box-sizing: border-box;
}
.editor-card {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow: hidden;
}
.editor-card > :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow: hidden;
}
.form-wrapper {
  overflow-y: auto;
  flex-grow: 1;
}
.card-header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}
.feedback-form {
  margin-top: 20px;
}
.question-item-card {
  margin-bottom: 20px;
}
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.question-header span {
  font-weight: bold;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
