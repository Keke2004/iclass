<template>
  <div class="assignment-editor">
    <el-form :model="form" label-position="top" ref="formRef" class="main-form">
      <!-- Basic Info -->
      <div class="form-section">
        <h3>1. 基本信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="作业标题" prop="title" :rules="rules.title">
                <el-input v-model="form.title" placeholder="例如：第一章"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="截止日期" prop="due_date" :rules="rules.due_date">
                <el-date-picker
                  v-model="form.due_date"
                  type="datetime"
                  placeholder="选择日期和时间"
                  style="width: 100%;"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="作业说明 (可选)" prop="description">
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入作业的详细说明、要求或注意事项"></el-input>
          </el-form-item>
        </div>

        <!-- Questions -->
        <div class="form-section">
          <div class="section-header">
            <h3>2. 题目列表</h3>
            <el-button @click="addQuestion" :icon="Plus" type="primary">添加题目</el-button>
          </div>
          <div v-if="form.questions.length === 0" class="empty-questions">
            <el-empty description="暂无题目，请点击下方按钮添加"></el-empty>
          </div>
          <div v-else>
            <div v-for="(question, index) in form.questions" :key="index" class="question-card">
              <div class="question-header">
                <span class="question-title">题目 {{ index + 1 }}</span>
                <el-button type="danger" link :icon="Delete" @click="removeQuestion(index)">删除题目</el-button>
              </div>
              <div class="question-body">
                <el-row :gutter="20">
                  <el-col :span="16">
                    <el-form-item label="题干" :prop="`questions[${index}].text`" :rules="rules.questionText">
                      <el-input v-model="question.text" type="textarea" :rows="2" placeholder="请输入题干内容"></el-input>
                    </el-form-item>
                  </el-col>
                  <el-col :span="4">
                    <el-form-item label="题型" :prop="`questions[${index}].question_type`" :rules="rules.questionType">
                      <el-select v-model="question.question_type" @change="onQuestionTypeChange(question)">
                        <el-option label="单选题" value="single_choice"></el-option>
                        <el-option label="多选题" value="multiple_choice"></el-option>
                        <el-option label="判断题" value="true_false"></el-option>
                        <el-option label="填空题" value="fill_in_the_blank"></el-option>
                        <el-option label="简答题" value="short_answer"></el-option>
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="4">
                    <el-form-item label="分值" :prop="`questions[${index}].points`" :rules="rules.points">
                      <el-input-number v-model="question.points" :min="1" controls-position="right" style="width: 100%;"></el-input-number>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- Answer Editors -->
                <div class="answer-editor">
                  <div v-if="question.question_type === 'single_choice'">
                    <el-form-item label="选项与答案" :prop="`questions[${index}].choices`" :rules="rules.choices">
                      <el-radio-group v-model="question.correct_choice_index" class="choice-group">
                        <div v-for="(choice, choiceIndex) in question.choices" :key="choiceIndex" class="choice-item">
                          <el-radio :label="choiceIndex" style="margin-right: 10px;">{{ String.fromCharCode(65 + choiceIndex) }}</el-radio>
                          <el-input v-model="choice.text" placeholder="请输入选项内容" style="flex-grow: 1;"></el-input>
                          <el-button type="danger" link :icon="Close" @click="removeChoice(question, choiceIndex)" class="remove-choice-btn"></el-button>
                        </div>
                      </el-radio-group>
                      <el-button @click="addChoice(question)" :icon="Plus" link type="primary">添加选项</el-button>
                    </el-form-item>
                  </div>
                  <div v-if="question.question_type === 'multiple_choice'">
                    <el-form-item label="选项与答案" :prop="`questions[${index}].choices`" :rules="rules.choices">
                      <el-checkbox-group v-model="question.correct_choice_indices" class="choice-group">
                        <div v-for="(choice, choiceIndex) in question.choices" :key="choiceIndex" class="choice-item">
                          <el-checkbox :label="choiceIndex" style="margin-right: 10px;">{{ String.fromCharCode(65 + choiceIndex) }}</el-checkbox>
                          <el-input v-model="choice.text" placeholder="请输入选项内容" style="flex-grow: 1;"></el-input>
                          <el-button type="danger" link :icon="Close" @click="removeChoice(question, choiceIndex)" class="remove-choice-btn"></el-button>
                        </div>
                      </el-checkbox-group>
                      <el-button @click="addChoice(question)" :icon="Plus" link type="primary">添加选项</el-button>
                    </el-form-item>
                  </div>
                  <div v-if="question.question_type === 'true_false'">
                    <el-form-item label="正确答案" :rules="rules.correctAnswer">
                      <el-radio-group v-model="question.correct_answer">
                        <el-radio label="true">正确</el-radio>
                        <el-radio label="false">错误</el-radio>
                      </el-radio-group>
                    </el-form-item>
                  </div>
                  <div v-if="question.question_type === 'fill_in_the_blank'">
                    <el-form-item label="正确答案" :rules="rules.correctAnswer">
                      <el-input v-model="question.correct_answer" placeholder="请输入正确答案"></el-input>
                    </el-form-item>
                  </div>
                  <div v-if="question.question_type === 'short_answer'">
                    <el-form-item label="参考答案 (可选)">
                      <el-input v-model="question.correct_answer" type="textarea" placeholder="请输入参考答案"></el-input>
                    </el-form-item>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-form>
    
    <!-- Action Buttons -->
    <div class="form-actions">
      <el-button @click="cancel">取消</el-button>
      <el-button type="primary" @click="submitForm" :loading="isSubmitting">
        {{ isEditing ? '保存更新' : '立即创建' }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from 'vue';
import api from '@/services/api';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Delete, Plus, Close } from '@element-plus/icons-vue';

const props = defineProps<{
  assignmentId: number | null;
  courseId: string;
}>();

const emit = defineEmits(['save', 'cancel']);

const formRef = ref();
const isSubmitting = ref(false);
const isEditing = computed(() => !!props.assignmentId);

const form = ref({
  title: '',
  description: '',
  due_date: '',
  questions: [] as any[],
});

const rules = reactive({
  title: [{ required: true, message: '请输入作业标题', trigger: 'blur' }],
  due_date: [{ required: true, message: '请选择截止日期', trigger: 'change' }],
  questionText: [{ required: true, message: '请输入题干', trigger: 'blur' }],
  questionType: [{ required: true, message: '请选择题型', trigger: 'change' }],
  points: [{ required: true, type: 'number', min: 1, message: '分值必须大于0', trigger: 'blur' }],
  choices: [{
    validator: (rule: any, value: any, callback: any, source: any) => {
      const questionIndex = parseInt(rule.field.split('[')[1].split(']')[0]);
      const question = form.value.questions[questionIndex];
      
      if (question.question_type === 'single_choice' || question.question_type === 'multiple_choice') {
        if (question.choices.some((c: any) => !c.text.trim())) {
          return callback(new Error('选项内容不能为空'));
        }
      }

      if (question.question_type === 'single_choice') {
        if (question.correct_choice_index === undefined || question.correct_choice_index === null) {
          return callback(new Error('请为单选题指定一个正确答案'));
        }
      }
      
      if (question.question_type === 'multiple_choice') {
        if (!question.correct_choice_indices || question.correct_choice_indices.length === 0) {
          return callback(new Error('请为多选题至少指定一个正确答案'));
        }
      }
      
      callback();
    },
    trigger: 'change'
  }],
  correctAnswer: [{ required: true, message: '请输入或选择正确答案', trigger: 'blur' }],
});

onMounted(() => {
  if (isEditing.value && props.assignmentId) {
    fetchAssignmentData(props.assignmentId);
  }
});

async function fetchAssignmentData(id: number) {
  try {
    const res = await api.get(`/assignments/${id}/`);
    const assignmentData = res.data;
    assignmentData.questions.forEach((q: any) => {
      if (q.question_type === 'single_choice') {
        const correctChoice = q.choices.findIndex((c: any) => c.is_correct);
        q.correct_choice_index = correctChoice !== -1 ? correctChoice : undefined;
        q.correct_choice_indices = [];
      } else if (q.question_type === 'multiple_choice') {
        q.correct_choice_indices = q.choices
          .map((c: any, index: number) => c.is_correct ? index : -1)
          .filter((index: number) => index !== -1);
        q.correct_choice_index = undefined;
      }
    });
    form.value = assignmentData;
  } catch (error) {
    ElMessage.error('加载作业数据失败');
  }
}

function addQuestion() {
  form.value.questions.push({
    text: '',
    question_type: 'single_choice',
    points: 5,
    choices: [{ text: '' }, { text: '' }],
    correct_choice_index: undefined,
    correct_choice_indices: [],
    correct_answer: null,
  });
}

function removeQuestion(index: number) {
  ElMessageBox.confirm('确定要删除这个题目吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    form.value.questions.splice(index, 1);
  }).catch(() => {});
}

function onQuestionTypeChange(question: any) {
  question.correct_answer = null;
  question.correct_choice_index = undefined;
  question.correct_choice_indices = [];
  if (question.question_type === 'single_choice' || question.question_type === 'multiple_choice') {
    if (!question.choices || question.choices.length === 0) {
      question.choices = [{ text: '' }, { text: '' }];
    }
  }
  if (question.question_type === 'true_false') {
    question.correct_answer = 'true';
  }
}

function addChoice(question: any) {
  question.choices.push({ text: '' });
}

function removeChoice(question: any, index: number) {
  const minChoices = (question.question_type === 'single_choice' || question.question_type === 'multiple_choice') ? 2 : 0;
  if (question.choices.length <= minChoices) {
    ElMessage.warning('选择题至少需要两个选项');
    return;
  }
  
  question.choices.splice(index, 1);

  if (question.question_type === 'single_choice') {
    if (question.correct_choice_index === index) {
      question.correct_choice_index = undefined;
    } else if (question.correct_choice_index > index) {
      question.correct_choice_index--;
    }
  } else if (question.question_type === 'multiple_choice') {
    const removedIndex = question.correct_choice_indices.indexOf(index);
    if (removedIndex > -1) {
      question.correct_choice_indices.splice(removedIndex, 1);
    }
    // Adjust subsequent indices
    question.correct_choice_indices = question.correct_choice_indices.map((i: number) => i > index ? i - 1 : i);
  }
}

function cancel() {
  emit('cancel');
}

async function submitForm() {
  if (!formRef.value) return;

  const isFormValid = await formRef.value.validate();
  if (!isFormValid) {
    ElMessage.error('表单校验失败，请检查红色标记的字段');
    return;
  }

  isSubmitting.value = true;
  try {
    // Manually construct payload to preserve IDs and reactivity references
    const payload = {
      title: form.value.title,
      description: form.value.description,
      due_date: form.value.due_date,
      course: isEditing.value ? form.value.course : props.courseId,
      questions: form.value.questions.map(q => {
        const questionCopy: any = { 
          id: q.id,
          text: q.text,
          question_type: q.question_type,
          points: q.points,
          correct_answer: q.correct_answer
        };

        if (q.question_type === 'single_choice' || q.question_type === 'multiple_choice') {
          questionCopy.choices = q.choices.map((c: any, index: number) => ({
            id: c.id,
            text: c.text,
            is_correct: q.question_type === 'single_choice'
              ? index === q.correct_choice_index
              : q.correct_choice_indices.includes(index),
          }));
        }
        return questionCopy;
      })
    };

    // Sanitize the payload's questions before sending
    payload.questions = payload.questions
      .filter((q: any) => q.text && q.text.trim() !== '') // Remove questions with no text
      .map((q: any) => {
        if (q.question_type === 'single_choice' || q.question_type === 'multiple_choice') {
          q.choices = q.choices.filter((c: any) => c.text && c.text.trim() !== ''); // Remove empty choices
        }
        return q;
      });

    // Submit to backend
    if (isEditing.value) {
      await api.put(`/assignments/${props.assignmentId}/`, payload);
      ElMessage.success('作业更新成功');
    } else {
      await api.post('/assignments/', payload);
      ElMessage.success('作业创建成功');
    }
    emit('save');

  } catch (error: any) {
    console.error('Failed to save assignment:', error.response?.data || error.message);
    const errorMessage = error.response?.data?.course?.[0] || '保存失败，请检查表单内容。';
    ElMessage.error(errorMessage);
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.assignment-editor {
  display: flex;
  flex-direction: column;
  /* Set a max height relative to the viewport height to contain the component */
  height: 70vh;
}
.main-form {
  flex-grow: 1; /* Allow the form to grow and fill available space */
  overflow-y: auto; /* Add a vertical scrollbar ONLY to the form area if needed */
  /* Add some padding to avoid content touching the scrollbar */
  padding: 0 10px 0 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.form-section h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #303133;
  border-left: 4px solid var(--el-color-primary);
  padding-left: 10px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.section-header h3 {
  margin-bottom: 0;
}
.empty-questions {
  text-align: center;
  padding: 40px 0;
}
.question-card {
  background-color: #fcfcfc;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f7fa;
  padding: 10px 20px;
  border-bottom: 1px solid #e4e7ed;
}
.question-title {
  font-weight: 600;
  color: #303133;
}
.question-body {
  padding: 20px;
}
.answer-editor {
  background-color: #fafafa;
  border-radius: 4px;
  padding: 15px;
  margin-top: 10px;
}
.choice-group {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 10px;
}
.choice-item {
  display: flex;
  align-items: center;
  width: 100%;
}
.remove-choice-btn {
  margin-left: 10px;
  opacity: 0.5;
  transition: opacity 0.2s;
}
.choice-item:hover .remove-choice-btn {
  opacity: 1;
}
.form-actions {
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  padding-top: 20px; /* Keep space above buttons */
  margin-top: 15px; /* Add margin to separate from content */
  border-top: 1px solid #e4e7ed;
  background-color: #fff;
  /* The negative margins were causing the horizontal scrollbar. Removing them. */
}
</style>
