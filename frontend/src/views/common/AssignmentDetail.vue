<template>
  <div class="assignment-detail-container" v-if="!loading">
    <!-- Header -->
    <el-card class="page-header-card">
      <div class="header-content">
        <div class="header-left">
          <span class="assignment-title">{{ assignment.title }}</span>
          <div class="header-meta">
            <span>题目: {{ assignment.questions?.length || 0 }}</span>
            <span>总分: {{ totalPoints }}</span>
            <span v-if="isStudent && isGraded">作答时间: {{ formatDate(submission.submitted_at) }}</span>
            <span v-else>截止时间: {{ formatDate(assignment.due_date) }}</span>
          </div>
        </div>
        <div class="header-right" v-if="isStudent && isGraded">
          <span class="score-label">得分</span>
          <span class="score-value">{{ submission.grade }}</span>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" class="main-content">
      <!-- Main Content -->
      <el-col :span="18">
        <el-card class="main-card">
          <!-- Student View -->
          <div v-if="isStudent">
            <div class="question-list">
              <div v-for="(question, index) in assignment.questions" :key="question.id" class="question-item" :id="`question-${question.id}`">
                <div class="question-header">
                  <h4>{{ index + 1 }}. [{{ getQuestionTypeName(question.question_type) }}] {{ question.text }} ({{ question.points }}分)</h4>
                </div>
                
                <!-- Answering / Readonly View -->
                <div class="answer-area">
                  <el-radio-group v-if="question.question_type === 'single_choice'" :model-value="studentAnswers[question.id]" :disabled="isReadOnly" class="choice-radio-group">
                    <el-radio
                      v-for="(choice, choiceIndex) in question.choices"
                      :key="choice.id"
                      :label="choice.id.toString()"
                      class="choice-radio-item"
                      @click="handleRadioClick(question.id, choice.id.toString())"
                    >
                      <span class="choice-label">{{ getChoiceLabel(choiceIndex) }}.</span> {{ choice.text }}
                    </el-radio>
                  </el-radio-group>
                  <el-checkbox-group v-else-if="question.question_type === 'multiple_choice'" v-model="studentAnswers[question.id]" :disabled="isReadOnly" class="choice-radio-group">
                    <el-checkbox
                      v-for="(choice, choiceIndex) in question.choices"
                      :key="choice.id"
                      :label="choice.id.toString()"
                      class="choice-radio-item"
                    >
                      <span class="choice-label">{{ getChoiceLabel(choiceIndex) }}.</span> {{ choice.text }}
                    </el-checkbox>
                  </el-checkbox-group>
                  <el-radio-group v-else-if="question.question_type === 'true_false'" :model-value="studentAnswers[question.id]" :disabled="isReadOnly">
                    <el-radio label="true" @click="handleRadioClick(question.id, 'true')">正确</el-radio>
                    <el-radio label="false" @click="handleRadioClick(question.id, 'false')">错误</el-radio>
                  </el-radio-group>
                  <el-input v-else-if="question.question_type === 'fill_in_the_blank'" v-model="studentAnswers[question.id]" placeholder="请输入答案" :disabled="isReadOnly" />
                  <el-input v-else-if="question.question_type === 'short_answer'" v-model="studentAnswers[question.id]" type="textarea" :rows="4" placeholder="请输入答案" :disabled="isReadOnly" />
                </div>

                <!-- Graded Result Box -->
                <div v-if="isGraded" class="graded-result-box">
                  <div class="result-answers">
                    <span class="answer-label">我的答案:</span>
                    <span class="answer-text">{{ getStudentAnswerText(question) || '未作答' }}</span>
                    <span class="answer-label" style="margin-left: 20px;">正确答案:</span>
                    <span class="answer-text correct-answer-text">{{ getCorrectAnswerForQuestion(question) }}</span>
                  </div>
                  <div class="result-feedback">
                    <el-icon v-if="isAnswerCorrect(question)" color="green" class="result-icon"><CircleCheckFilled /></el-icon>
                    <el-icon v-else color="red" class="result-icon"><CircleCloseFilled /></el-icon>
                    <span :class="isAnswerCorrect(question) ? 'score-correct' : 'score-incorrect'" class="question-score-display">
                      {{ getAnswerForQuestion(question.id)?.score ?? 0 }} 分
                    </span>
                  </div>
                </div>

                <!-- Submitted, Not Graded Notice -->
                <div v-else-if="isSubmitted" class="submitted-notice">
                  <span>我的答案: </span>
                  <span class="answer-text">{{ getStudentAnswerText(question) || '未作答' }}</span>
                </div>
              </div>
            </div>
            <div class="submission-actions" v-if="!isGraded && !isReadOnly">
              <el-button type="primary" @click="submitAssignment">提交作业</el-button>
            </div>
          </div>

          <!-- Teacher View -->
          <div v-if="isTeacher">
            <!-- Teacher view content remains largely the same but could be styled -->
            <div v-if="!selectedSubmission" class="empty-state">
              <el-empty description="请从右侧选择一个学生以开始批改"></el-empty>
            </div>
            <div v-else>
              <h3>正在批改: {{ selectedSubmission.student }} 的作业</h3>
              <div class="question-list">
                <div v-for="(question, index) in assignment.questions" :key="question.id" class="question-item">
                  <h4>{{ index + 1 }}. [{{ getQuestionTypeName(question.question_type) }}] {{ question.text }} ({{ question.points }}分)</h4>

                  <!-- Teacher's view of choices -->
                  <div v-if="question.question_type === 'single_choice' || question.question_type === 'multiple_choice'" class="choices-display-teacher">
                    <div v-for="(choice, choiceIndex) in question.choices" :key="choice.id" class="choice-item-teacher">
                      <span class="choice-label">{{ getChoiceLabel(choiceIndex) }}.</span>
                      <span class="choice-text">{{ choice.text }}</span>
                      <el-icon v-if="choice.is_correct" color="green" class="correct-choice-icon"><CircleCheckFilled /></el-icon>
                    </div>
                  </div>
                  
                  <div class="answer-display">
                    <div class="answer-row">
                      <span class="answer-label">学生答案:</span>
                      <span class="answer-text">{{ getStudentAnswerText(question) || '未作答' }}</span>
                    </div>
                    <div class="answer-row">
                      <span class="answer-label">正确答案:</span>
                      <span class="answer-text correct-answer-text">{{ getCorrectAnswerForQuestion(question) }}</span>
                    </div>
                  </div>

                  <div class="grading-area">
                    <span>打分:</span>
                    <el-input-number v-model="gradingScores[getAnswerForQuestion(question.id).id]" :min="0" :max="question.points" size="small" />
                  </div>
                </div>
              </div>
              <div class="feedback-area">
                <h3>总评语</h3>
                <el-input v-model="gradingFeedback" type="textarea" :rows="4" placeholder="请输入对本次作业的评语"></el-input>
              </div>
              <div class="submission-actions">
                <el-button type="primary" @click="saveGrades">保存批改</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Sidebar -->
      <el-col :span="6">
        <!-- Student Question Navigator -->
        <el-card v-if="isStudent" class="sidebar-card">
          <template #header>题目导航</template>
          <div class="question-nav-grid">
            <el-button
              v-for="(question, index) in assignment.questions"
              :key="question.id"
              :type="getQuestionNavType(question)"
              plain
              @click="jumpToQuestion(question.id)"
            >
              {{ index + 1 }}
            </el-button>
          </div>
           <div v-if="isGraded" class="sidebar-summary">
            <h4>作业总览</h4>
            <p>最终得分: {{ submission.grade }} / {{ totalPoints }}</p>
            <h4>教师评语</h4>
            <p>{{ submission.feedback || '暂无评语' }}</p>
          </div>
        </el-card>

        <!-- Teacher Submission List -->
        <el-card v-if="isTeacher" class="sidebar-card">
          <template #header>学生列表 ({{ allSubmissions.length }})</template>
          <div class="sidebar-content">
            <el-menu :default-active="selectedSubmission?.id.toString()" @select="handleStudentSelect">
              <el-menu-item v-for="sub_status in allSubmissions" :key="sub_status.student_id" :index="sub_status.submission_id?.toString() || `student-${sub_status.student_id}`" :disabled="!sub_status.submission_id">
                <template #title>
                  <span>{{ sub_status.student_name }}</span>
                  <span>
                    <el-tag v-if="sub_status.status === 'graded'" type="success" size="small">已批改: {{ sub_status.grade }}分</el-tag>
                    <el-tag v-else :type="getStudentStatusTagType(sub_status.status)" size="small">{{ getStudentStatusText(sub_status.status) }}</el-tag>
                  </span>
                </template>
              </el-menu-item>
            </el-menu>
            <el-empty v-if="allSubmissions.length === 0" description="该课程暂无学生"></el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
  <div v-else class="loading-container">
    <el-skeleton :rows="10" animated />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api';
import { ElMessage, ElMessageBox } from 'element-plus';
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue';

const route = useRoute();
const loading = ref(true);
const assignment = ref<any>(null);
const userRole = localStorage.getItem('user_role');
const assignmentId = route.params.id;

// For Student
const submission = ref<any>(null);
const studentAnswers = ref<any>({});

// For Teacher
const allSubmissions = ref<any[]>([]); // This will be populated from assignment.student_submissions
const selectedSubmission = ref<any>(null);
const gradingScores = ref<any>({});
const gradingFeedback = ref('');

onMounted(async () => {
  await fetchData();
});

async function fetchData() {
  try {
    loading.value = true;
    const assignmentRes = await api.get(`/assignments/${assignmentId}/`);
    assignment.value = assignmentRes.data;

    if (userRole === 'student') {
      const submissionRes = await api.get(`/submissions/?assignment=${assignmentId}`);
      if (submissionRes.data && submissionRes.data.length > 0) {
        submission.value = submissionRes.data[0];
        const answersFromServer = submission.value.answers;
        const questionMap = new Map(assignment.value.questions.map((q: any) => [q.id, q]));

        // Initialize all answers first
        assignment.value.questions.forEach((q: any) => {
          if (q.question_type === 'multiple_choice') {
            studentAnswers.value[q.id] = [];
          } else {
            studentAnswers.value[q.id] = '';
          }
        });

        // Pre-fill answers for viewing
        answersFromServer.forEach((ans: any) => {
          const question = questionMap.get(ans.question);
          if (question && question.question_type === 'multiple_choice') {
            try {
              const parsedAns = JSON.parse(ans.text);
              studentAnswers.value[ans.question] = Array.isArray(parsedAns) ? parsedAns.map(String) : [];
            } catch (e) {
              console.error('Failed to parse multiple choice answer:', ans.text);
              studentAnswers.value[ans.question] = [];
            }
          } else {
            studentAnswers.value[ans.question] = ans.text;
          }
        });
      } else {
        // Init empty answers for submission
        assignment.value.questions.forEach((q: any) => {
          if (q.question_type === 'multiple_choice') {
            studentAnswers.value[q.id] = [];
          } else {
            studentAnswers.value[q.id] = '';
          }
        });
      }
    } else if (userRole === 'teacher') {
      // The full list of students and their submission status is now part of the assignment object
      allSubmissions.value = assignment.value.student_submissions || [];
    }
  } catch (error) {
    console.error('Failed to fetch assignment data:', error);
    ElMessage.error('加载作业数据失败');
  } finally {
    loading.value = false;
  }
}

const handleRadioClick = (questionId: number, choiceId: string) => {
  if (isReadOnly.value) return;
  if (studentAnswers.value[questionId] === choiceId) {
    // If the clicked radio is already selected, deselect it
    studentAnswers.value[questionId] = '';
  } else {
    // Otherwise, select the new one
    studentAnswers.value[questionId] = choiceId;
  }
};

const totalPoints = computed(() => {
  if (!assignment.value || !assignment.value.questions) return 0;
  return assignment.value.questions.reduce((sum: number, q: any) => sum + q.points, 0);
});

const getQuestionTypeName = (type: string) => {
  const typeMap: { [key: string]: string } = {
    'single_choice': '单选题',
    'multiple_choice': '多选题',
    'true_false': '判断题',
    'fill_in_the_blank': '填空题',
    'short_answer': '简答题',
  };
  return typeMap[type] || '未知题型';
};

const getChoiceLabel = (index: number) => {
  return String.fromCharCode(65 + index); // A, B, C...
};

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
};

const isStudent = computed(() => userRole === 'student');
const isTeacher = computed(() => userRole === 'teacher');

const isGraded = computed(() => isStudent.value && submission.value?.status === 'graded');

const isSubmitted = computed(() => isStudent.value && submission.value?.status === 'submitted');

const isReadOnly = computed(() => {
  // 教师视图总是只读（不直接作答）
  if (!isStudent.value) return true;
  // 如果作业已提交（无论是否批改），则为只读
  if (submission.value) return true;
  // 如果已过截止日期，则为只读
  if (assignment.value && new Date(assignment.value.due_date) < new Date()) return true;
  // 其他情况均可编辑
  return false;
});

const getAnswerForQuestion = (questionId: number) => {
  const sub = isStudent.value ? submission.value : selectedSubmission.value;
  if (!sub || !sub.answers) return null;
  return sub.answers.find((a: any) => a.question === questionId);
};

const getStudentAnswerText = (question: any) => {
  const answer = getAnswerForQuestion(question.id);
  if (!answer || !answer.text) return '';

  const getChoiceTextById = (choiceId: string) => {
    const choice = question.choices.find((c: any) => c.id.toString() === choiceId);
    const choiceIndex = question.choices.findIndex((c: any) => c.id.toString() === choiceId);
    return choice ? `${getChoiceLabel(choiceIndex)}. ${choice.text}` : '无效选项';
  };

  if (question.question_type === 'single_choice') {
    return getChoiceTextById(answer.text);
  }

  if (question.question_type === 'multiple_choice') {
    try {
      const answerIds = JSON.parse(answer.text);
      if (Array.isArray(answerIds)) {
        return answerIds.map((id: any) => getChoiceTextById(id.toString())).join(', ');
      }
      return '无效答案格式';
    } catch (e) {
      return '无效答案格式';
    }
  }
  if (question.question_type === 'true_false') {
    return answer.text === 'true' ? '正确' : '错误';
  }
  return answer.text;
};

const getCorrectAnswerForQuestion = (question: any) => {
  if (question.question_type === 'single_choice' || question.question_type === 'multiple_choice') {
    const correctChoices = question.choices.filter((c: any) => c.is_correct);
    if (correctChoices.length === 0) return '未提供';
    
    return correctChoices.map((choice: any) => {
      const choiceIndex = question.choices.findIndex((c: any) => c.id === choice.id);
      return `${getChoiceLabel(choiceIndex)}. ${choice.text}`;
    }).join(', ');
  }
  if (question.question_type === 'true_false') {
    return question.correct_answer === 'true' ? '正确' : '错误';
  }
  return question.correct_answer || '未提供';
};

const isAnswerCorrect = (question: any) => {
  const answer = getAnswerForQuestion(question.id);
  if (!answer) return false;

  if (question.question_type === 'single_choice') {
    const correctChoice = question.choices.find((c: any) => c.is_correct);
    return correctChoice ? answer.text === correctChoice.id.toString() : false;
  }

  if (question.question_type === 'multiple_choice') {
    const correctChoiceIds = question.choices.filter((c: any) => c.is_correct).map((c: any) => c.id.toString());
    try {
      const studentAnswerIds = JSON.parse(answer.text).map(String).sort();
      correctChoiceIds.sort();
      return JSON.stringify(correctChoiceIds) === JSON.stringify(studentAnswerIds);
    } catch (e) {
      return false;
    }
  }
  // For other types, the backend scores them, so we check the score
  return answer.score === question.points;
};

const isQuestionAnswered = (questionId: number) => {
  const answer = studentAnswers.value[questionId];
  if (Array.isArray(answer)) {
    return answer.length > 0;
  }
  return !!answer && answer.toString().trim() !== '';
};

const getQuestionNavType = (question: any) => {
  if (isGraded.value) {
    return isAnswerCorrect(question) ? 'success' : 'danger';
  }
  if (isStudent.value) {
    return isQuestionAnswered(question.id) ? 'primary' : 'info';
  }
  return 'info';
};

const jumpToQuestion = (questionId: number) => {
  const element = document.getElementById(`question-${questionId}`);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
};

const getStudentStatusText = (status: string) => {
  const map: { [key: string]: string } = {
    'graded': '已批改',
    'submitted': '待批改',
    'not_submitted': '未提交'
  };
  return map[status] || '未知';
};

const getStudentStatusTagType = (status: string) => {
  const map: { [key: string]: string } = {
    'graded': 'success',
    'submitted': 'warning',
    'not_submitted': 'info'
  };
  return map[status] || 'info';
};

async function handleStudentSelect(submissionId: string) {
  if (!submissionId || submissionId.startsWith('student-')) {
    selectedSubmission.value = null;
    return;
  }
  
  // Fetch the full submission details for the selected student
  try {
    const res = await api.get(`/submissions/${submissionId}/`);
    selectedSubmission.value = res.data;
    
    if (selectedSubmission.value) {
      gradingFeedback.value = selectedSubmission.value.feedback || '';
      const scores: any = {};
      selectedSubmission.value.answers.forEach((ans: any) => {
        scores[ans.id] = ans.score ?? 0;
      });
      gradingScores.value = scores;
    }
  } catch (error) {
    console.error('Failed to fetch submission details:', error);
    ElMessage.error('加载学生提交数据失败');
    selectedSubmission.value = null;
  }
}

async function saveGrades() {
  if (!selectedSubmission.value) return;
  const answersPayload = Object.keys(gradingScores.value).map(answerId => ({
    id: parseInt(answerId),
    score: gradingScores.value[answerId],
  }));
  const payload = { answers: answersPayload, feedback: gradingFeedback.value };
  try {
    await api.post(`/submissions/${selectedSubmission.value.id}/grade/`, payload);
    ElMessage.success('批改已保存！');
    await fetchData();
  } catch (error) {
    console.error('Failed to save grades:', error);
    ElMessage.error('保存失败，请稍后重试。');
  }
}

const submitAssignment = async () => {
  try {
    await ElMessageBox.confirm('确认提交作业吗？提交后将无法修改。', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    });
  } catch (e) {
    return;
  }

  try {
    const questionMap = new Map(assignment.value.questions.map((q: any) => [q.id.toString(), q]));
    const answersPayload = Object.keys(studentAnswers.value)
      .map(questionId => {
        const answer = studentAnswers.value[questionId];
        const question = questionMap.get(questionId);

        if (!question) return null;

        if (question.question_type === 'multiple_choice') {
          if (Array.isArray(answer) && answer.length > 0) {
            return { question: parseInt(questionId), text: JSON.stringify(answer.sort()) };
          }
        } else {
          if (answer && answer.toString().trim() !== '') {
            return { question: parseInt(questionId), text: answer.toString() };
          }
        }
        return null;
      })
      .filter(p => p); // filter out nulls

    if (answersPayload.length === 0) {
      ElMessage.warning('您还没有回答任何问题。');
      return;
    }

    const submissionPayload = { assignment: assignmentId, answers: answersPayload };
    await api.post('/submissions/', submissionPayload);
    ElMessage.success('作业提交成功！');
    await fetchData();
  } catch (error) {
    console.error('Failed to submit assignment:', error);
    ElMessage.error('提交失败，请检查网络或联系教师。');
  }
};
</script>

<style scoped>
.assignment-detail-container {
  padding: 20px;
  background-color: #f4f5f7;
}

.page-header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.assignment-title {
  font-size: 24px;
  font-weight: bold;
}

.header-meta {
  display: flex;
  gap: 20px;
  margin-top: 8px;
  font-size: 14px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: baseline;
}

.score-label {
  font-size: 16px;
  color: #909399;
  margin-right: 10px;
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  color: #e6a23c;
}

.main-content {
  width: 100%;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.question-item {
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 20px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.question-header h4 {
  font-size: 16px;
  margin: 0;
}

.score-correct {
  color: #67c23a;
}

.score-incorrect {
  color: #f56c6c;
}

.answer-display {
  background-color: #f9fafb;
  border-radius: 4px;
  padding: 15px;
  font-size: 14px;
}

.answer-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.answer-row:last-child {
  margin-bottom: 0;
}

.answer-label {
  font-weight: bold;
  color: #303133;
  width: 80px;
}

.answer-text {
  color: #606266;
}

.correct-answer-text {
  color: #67c23a;
  font-weight: 500;
}

.result-icon {
  margin-left: 10px;
  font-size: 18px;
}

.graded-result-box {
  margin-top: 15px;
  padding: 15px;
  background-color: #f9fafb;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-answers {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.result-feedback {
  display: flex;
  align-items: center;
  gap: 8px;
}

.question-score-display {
  font-weight: bold;
  font-size: 16px;
}

.submitted-notice {
  margin-top: 15px;
  padding: 10px 15px;
  background-color: #f4f4f5;
  border-radius: 4px;
  color: #909399;
  font-size: 14px;
}

.answer-area {
  padding-left: 20px;
}

.submission-actions {
  margin-top: 30px;
  text-align: center;
}

.sidebar-card {
  position: sticky;
  top: 20px;
}

.question-nav-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.question-nav-grid .el-button {
  width: 40px;
  height: 40px;
  padding: 0;
  min-width: 40px;
}

.choice-radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.choice-radio-item {
  display: flex;
  align-items: center;
  height: auto;
  padding: 10px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  width: 100%;
  margin-right: 0 !important;
}

.choice-radio-item:hover {
  border-color: #409eff;
}

.choice-radio-item.is-checked {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.choice-label {
  font-weight: 500;
  margin-right: 8px;
}

.sidebar-summary {
  margin-top: 20px;
  border-top: 1px solid #e4e7ed;
  padding-top: 15px;
}

.sidebar-summary h4 {
  font-size: 16px;
  margin-bottom: 10px;
}

.sidebar-summary p {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.loading-container {
  padding: 20px;
}

.choices-display-teacher {
  margin: 15px 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
}

.choice-item-teacher {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.correct-choice-icon {
  margin-left: 4px;
}

/* Teacher view specific styles */
.grading-area {
  margin-top: 10px;
}
.feedback-area {
  margin-top: 30px;
}
.el-menu-item {
  display: flex;
  justify-content: space-between;
}
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #909399;
}
</style>
