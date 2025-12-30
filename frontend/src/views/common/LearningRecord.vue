<template>
  <div class="learning-record-page">
    <h1 class="page-title">学习记录</h1>

    <!-- 教师视图：学生选择器 -->
    <div v-if="isTeacher" class="teacher-controls">
      <el-select
        v-model="selectedStudent"
        placeholder="请选择学生查看记录"
        filterable
        clearable
        @change="handleStudentChange"
        style="width: 300px;"
      >
        <el-option
          v-for="student in studentList"
          :key="student.id"
          :label="student.first_name || student.username"
          :value="student.id"
        />
      </el-select>
    </div>

    <div v-if="loading" class="loading">正在加载...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <!-- 学习记录卡片 -->
    <div v-else-if="record" class="record-display">
      <el-card class="record-card">
        <template #header>
          <div class="card-header">
            <span>签到</span>
            <el-tag type="info">共 {{ record.checkin_summary.total }} 次</el-tag>
          </div>
        </template>
        <div class="checkin-stats">
          <div class="stat-item">
            <span class="stat-value">{{ record.checkin_summary.present }}</span>
            <span class="stat-label">出勤</span>
          </div>
          <div class="stat-item">
            <span class="stat-value absent-value">{{ record.checkin_summary.absent }}</span>
            <span class="stat-label">缺勤</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ record.checkin_summary.late }}</span>
            <span class="stat-label">迟到</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ record.checkin_summary.sick_leave }}</span>
            <span class="stat-label">病假</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ record.checkin_summary.personal_leave }}</span>
            <span class="stat-label">事假</span>
          </div>
        </div>
        <div class="attendance-progress">
          <div class="progress-label">
            <span>出勤率</span>
            <span>{{ record.checkin_summary.attendance_rate.toFixed(0) }}%</span>
          </div>
          <el-progress :percentage="parseFloat(record.checkin_summary.attendance_rate.toFixed(2))" :show-text="false" />
        </div>
      </el-card>

      <el-card class="record-card">
        <template #header><div class="card-header">学习任务</div></template>
        <div class="task-item-new">
          <span class="task-title">课程作业</span>
          <div class="task-progress-new">
            <el-progress :percentage="parseFloat(record.assignment_summary.completion_rate.toFixed(2))" :show-text="false" color="#e6a23c" />
          </div>
          <span class="task-ratio">{{ record.assignment_summary.completed }}/{{ record.assignment_summary.total }}</span>
        </div>
        <div class="task-item-new">
          <span class="task-title">在线考试</span>
          <div class="task-progress-new">
            <el-progress :percentage="parseFloat(record.exam_summary.completion_rate.toFixed(2))" :show-text="false" color="#f56c6c" />
          </div>
          <span class="task-ratio">{{ record.exam_summary.completed }}/{{ record.exam_summary.total }}</span>
        </div>
      </el-card>

      <el-card class="record-card">
        <template #header><div class="card-header">讨论</div></template>
        <div class="discussion-stats">
          <div class="stat-item">
            <span class="stat-value">{{ record.discussion_summary.topic_count }}</span>
            <span class="stat-label">发帖</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ record.discussion_summary.reply_count }}</span>
            <span class="stat-label">回帖</span>
          </div>
        </div>
      </el-card>
    </div>
    
    <div v-else class="no-data">
        <p v-if="isTeacher">请选择一名学生以查看其学习记录。</p>
        <p v-else>暂无您的学习记录。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage, ElCard, ElProgress, ElSelect, ElOption, ElTag } from 'element-plus';

// 数据结构定义
interface CheckinSummary {
  total: number;
  present: number;
  late: number;
  absent: number;
  sick_leave: number;
  personal_leave: number;
  attendance_rate: number;
}

interface TaskSummary {
  total: number;
  completed: number;
  completion_rate: number;
}

interface DiscussionSummary {
  topic_count: number;
  reply_count: number;
}

interface LearningRecord {
  student_id: number;
  student_name: string;
  checkin_summary: CheckinSummary;
  assignment_summary: TaskSummary;
  exam_summary: TaskSummary;
  discussion_summary: DiscussionSummary;
}

interface Student {
  id: number;
  username: string;
  first_name: string;
}

const route = useRoute();
const loading = ref(false);
const error = ref<string | null>(null);
const record = ref<LearningRecord | null>(null);
const studentList = ref<Student[]>([]);
const selectedStudent = ref<number | null>(null);

const courseId = computed(() => route.params.id as string);
const userRole = localStorage.getItem('user_role');
const isTeacher = computed(() => userRole === 'teacher');

// 获取学习记录
const fetchLearningRecords = async (studentId: number | null = null) => {
  loading.value = true;
  error.value = null;
  record.value = null;
  try {
    let url = `/courses/${courseId.value}/learning_records/`;
    if (isTeacher.value && studentId) {
      url += `?student_id=${studentId}`;
    }
    
    const response = await apiClient.get<LearningRecord[]>(url);
    
    if (response.data && response.data.length > 0) {
      record.value = response.data[0];
    } else if (isTeacher.value && studentId) {
      error.value = '未找到该学生的学习记录。';
    }
  } catch (err) {
    console.error('获取学习记录失败:', err);
    error.value = '无法加载学习记录，请稍后重试。';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
};

// 获取学生列表（仅教师）
const fetchStudents = async () => {
  if (!isTeacher.value) return;
  try {
    const response = await apiClient.get(`/courses/${courseId.value}/members/`);
    studentList.value = response.data.students;
  } catch (err) {
    console.error('获取学生列表失败:', err);
    ElMessage.error('无法加载学生列表。');
  }
};

// 教师选择学生后的处理
const handleStudentChange = (studentId: number | null) => {
  if (studentId) {
    fetchLearningRecords(studentId);
  } else {
    record.value = null; // 清空选择时清除记录
  }
};

onMounted(() => {
  if (isTeacher.value) {
    fetchStudents();
  } else {
    fetchLearningRecords();
  }
});
</script>

<style scoped>
.learning-record-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px); /* 假设顶部导航和标签页等固定高度为 150px */
  padding: 20px;
  background-color: #f4f5f7;
  box-sizing: border-box;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  flex-shrink: 0; /* 防止标题被压缩 */
}

.teacher-controls {
  margin-bottom: 20px;
  flex-shrink: 0; /* 防止选择器被压缩 */
}

.loading, .error, .no-data {
  text-align: center;
  color: #909399;
  padding: 40px;
  font-size: 16px;
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.record-display {
  flex-grow: 1; /* 占据剩余空间 */
  overflow-y: auto; /* 内容超出时显示垂直滚动条 */
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-right: 10px; /* 为滚动条留出空间，防止内容紧贴 */
}

.record-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  flex-shrink: 0; /* 防止卡片在flex布局中被压缩 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.checkin-stats, .discussion-stats {
  display: flex;
  justify-content: space-around;
  text-align: center;
  padding: 10px 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.absent-value {
  color: #f56c6c; /* 红色 */
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.attendance-progress {
  margin-top: 20px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.task-item-new {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.task-item-new:last-child {
  margin-bottom: 0;
}

.task-title {
  width: 80px; /* 固定宽度以便对齐 */
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
}

.task-progress-new {
  flex-grow: 1;
}

.task-ratio {
  font-size: 14px;
  color: #909399;
  white-space: nowrap;
  width: 50px; /* 固定宽度以便对齐 */
  text-align: right;
}
</style>
