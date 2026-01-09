<template>
  <div class="feedback-form-container">
    <el-card class="feedback-card" v-if="questionnaire">
      <template #header>
        <div class="card-header">
          <h1>{{ questionnaire.title }}</h1>
          <p v-if="questionnaire.description">{{ questionnaire.description }}</p>
        </div>
      </template>
      <div class="card-content">
        <div v-if="userResponse" class="submitted-feedback">
        <el-alert title="您已提交此反馈" type="success" show-icon :closable="false" />
        <el-form label-position="top" disabled>
          <div v-for="(question, index) in questionnaire.questions" :key="question.id" class="question-item">
            <el-form-item :label="`${index + 1}. ${question.text}`">
              <el-rate v-if="question.question_type === 'rating'" v-model="answers[question.id]" :max="5" show-text
                :texts="['很差', '较差', '一般', '推荐', '力荐']"></el-rate>
              <el-input v-else v-model="answers[question.id]" type="textarea" :rows="4"></el-input>
            </el-form-item>
          </div>
        </el-form>
      </div>
      <el-form v-else label-position="top">
        <div v-for="(question, index) in questionnaire.questions" :key="question.id" class="question-item">
          <el-form-item :label="`${index + 1}. ${question.text}`">
            <el-rate v-if="question.question_type === 'rating'" v-model="answers[question.id]" :max="5" show-text
              :texts="['很差', '较差', '一般', '推荐', '力荐']"></el-rate>
            <el-input v-else v-model="answers[question.id]" type="textarea" :rows="4"
              placeholder="请输入您的回答"></el-input>
          </el-form-item>
        </div>
        <el-form-item class="submit-button-container">
          <el-button type="primary" @click="submitFeedback" size="large">提交反馈</el-button>
        </el-form-item>
      </el-form>
    </div>
    </el-card>
    <div v-else class="loading-container">
      <p>正在加载问卷...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();
const questionnaire = ref<any>(null);
const answers = ref<any>({});
const userResponse = ref<any>(null);

const fetchQuestionnaire = async () => {
  try {
    const response = await apiClient.get(`/questionnaires/${route.params.feedbackId}/`);
    questionnaire.value = response.data;
    userResponse.value = response.data.user_response;

    if (userResponse.value) {
      // If user has already responded, populate answers with their response
      userResponse.value.answers.forEach((ans: any) => {
        answers.value[ans.question] = ans.answer_rating !== null ? ans.answer_rating : ans.answer_text;
      });
    } else {
      // Otherwise, initialize for a new submission
      questionnaire.value.questions.forEach((q: any) => {
        answers.value[q.id] = q.question_type === 'rating' ? 0 : '';
      });
    }
  } catch (error) {
    ElMessage.error('无法加载问卷');
    console.error(error);
  }
};

const submitFeedback = async () => {
  const responseData = {
    questionnaire: questionnaire.value.id,
    answers: Object.keys(answers.value).map(questionId => ({
      question: parseInt(questionId),
      answer_rating: questionnaire.value.questions.find((q:any) => q.id === parseInt(questionId))?.question_type === 'rating' ? answers.value[questionId] : null,
      answer_text: questionnaire.value.questions.find((q:any) => q.id === parseInt(questionId))?.question_type === 'text' ? answers.value[questionId] : ''
    }))
  };

  try {
    await apiClient.post('/feedback/responses/', responseData);
    ElMessage.success('反馈提交成功');
    router.push({ name: 'course-feedback', params: { id: route.params.id } });
  } catch (error) {
    ElMessage.error('提交失败');
    console.error(error);
  }
};

onMounted(fetchQuestionnaire);
</script>

<style scoped>
.feedback-form-container {
  padding: 20px;
  background-color: #f5f7fa;
  height: calc(100vh - 150px);
  display: flex;
  flex-direction: column;
}

.feedback-card {
  max-width: 800px;
  margin: 0 auto;
  border-radius: 8px;
  width: 100%;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow: hidden;
}

.card-content {
  overflow-y: auto;
  flex-grow: 1;
  padding: 20px;
}

.card-header h1 {
  margin: 0;
  font-size: 24px;
}

.card-header p {
  margin: 5px 0 0;
  color: #606266;
}

.question-item {
  margin-bottom: 25px;
}

.el-form-item__label {
  font-weight: bold;
}

.submit-button-container {
  text-align: center;
  margin-top: 30px;
}

.loading-container {
  text-align: center;
  padding-top: 50px;
  color: #909399;
}

.submitted-feedback {
  /* padding: 20px; */
}

.submitted-feedback .el-alert {
  margin-bottom: 20px;
}
</style>
