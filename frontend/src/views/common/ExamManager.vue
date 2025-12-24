<template>
  <div class="exam-manager">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span>课程考试</span>
          <el-button v-if="isTeacher" type="primary" @click="openCreateDialog" :icon="Plus">创建新考试</el-button>
        </div>
      </template>
      
      <el-tabs v-if="isTeacher" v-model="activeTab" @tab-change="fetchData" class="custom-tabs">
        <el-tab-pane label="全部考试" name="all"></el-tab-pane>
        <el-tab-pane label="批改中" name="grading"></el-tab-pane>
        <el-tab-pane label="批改完成" name="graded_completed"></el-tab-pane>
      </el-tabs>
      <el-tabs v-else v-model="activeTab" @tab-change="fetchData" class="custom-tabs">
        <el-tab-pane label="全部考试" name="all"></el-tab-pane>
        <el-tab-pane label="进行中" name="pending"></el-tab-pane>
        <el-tab-pane label="已完成" name="completed"></el-tab-pane>
      </el-tabs>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="exams.length === 0" class="empty-state">
        <el-empty description="暂无考试"></el-empty>
      </div>

      <div v-else class="exam-grid">
        <el-card v-for="exam in exams" :key="exam.id" class="exam-card" shadow="hover" @click="goToDetail(exam)">
          <div class="card-content-wrapper">
            <div class="card-header-line">
              <span class="exam-title">{{ exam.title }}</span>
              <el-tag v-if="isTeacher" :type="getTeacherExamStatus(exam).type" size="small" effect="light">
                {{ getTeacherExamStatus(exam).text }}
              </el-tag>
              <el-tag v-else :type="getStudentExamStatus(exam).type" size="small" effect="light">
                {{ getStudentExamStatus(exam).text }}
              </el-tag>
            </div>
            <div class="exam-meta">
              <span>开始: {{ formatDate(exam.start_time) }}</span>
              <span>结束: {{ formatDate(exam.end_time) }}</span>
            </div>
            <div class="exam-meta">
              <span>时长: {{ exam.time_limit }} 分钟</span>
              <span>总分: {{ exam.total_points }}</span>
            </div>
            
            <!-- Teacher's View: Grading Progress -->
            <div v-if="isTeacher && exam.submission_stats" class="score-progress">
              <el-progress :percentage="getGradingPercentage(exam)" :stroke-width="10" :color="getProgressColor(getGradingPercentage(exam))">
                  <span class="progress-text">
                    已批改 {{ exam.submission_stats.graded_submissions }} / {{ exam.submission_stats.total_students }}
                  </span>
              </el-progress>
            </div>
            
            <!-- Student's View: Score Progress -->
            <div v-if="!isTeacher && exam.submission?.status === 'graded'" class="score-progress">
              <el-progress :percentage="getScorePercentage(exam)" :stroke-width="10" :color="getProgressColor(getScorePercentage(exam))">
                <span class="progress-text">{{ exam.submission.grade }} / {{ exam.total_points }}</span>
              </el-progress>
            </div>
          </div>
          <div class="card-footer-actions">
            <el-button type="primary" link @click.stop="goToDetail(exam)">查看详情</el-button>
            <el-button v-if="isTeacher" type="primary" link @click.stop="openEditDialog(exam.id)">编辑</el-button>
            <el-popconfirm
              v-if="isTeacher"
              title="确定要删除这个考试吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm.stop="deleteExam(exam.id)"
            >
              <template #reference>
                <el-button type="danger" link @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </el-card>
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingExamId ? '编辑考试' : '创建新考试'"
      width="80%"
      top="5vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div style="height: 75vh; overflow-y: auto;">
        <ExamEditor
          v-if="dialogVisible"
          :exam-id="editingExamId"
          :course-id="courseId"
          @save="handleSave"
          @cancel="handleCancel"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Plus } from '@element-plus/icons-vue';
import api from '@/services/api';
import { ElMessage } from 'element-plus';
import ExamEditor from '@/views/teacher/ExamEditor.vue';

const router = useRouter();
const route = useRoute();
const userRole = localStorage.getItem('user_role');
const courseId = computed(() => route.params.id as string);
const activeTab = ref('all');
const loading = ref(true);
const exams = ref<any[]>([]);
const dialogVisible = ref(false);
const editingExamId = ref<number | null>(null);

const isTeacher = computed(() => userRole === 'teacher');

async function fetchData() {
  if (!courseId.value) {
    console.error("Course ID not found in route params.");
    loading.value = false;
    return;
  }
  try {
    loading.value = true;
    let url = `/exams/?course=${courseId.value}`;
    if (activeTab.value !== 'all') {
      url += `&status=${activeTab.value}`;
    }
    const res = await api.get(url);
    exams.value = res.data.map((exam: any) => ({
      ...exam,
      total_points: exam.questions.reduce((sum: number, q: any) => sum + q.points, 0)
    }));
  } catch (error) {
    console.error('Failed to fetch exams:', error);
    ElMessage.error('获取考试列表失败');
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);

const getTeacherExamStatus = (exam: any) => {
  const stats = exam.submission_stats;
  if (!stats) return { text: '加载中', type: 'info' };

  if (stats.graded_submissions === stats.total_students) {
    return { text: '批改完成', type: 'success' };
  }
  if (stats.total_submissions > 0) {
    return { text: '批改中', type: 'warning' };
  }
  const now = new Date();
  const endTime = new Date(exam.end_time);
  if (endTime < now) {
    return { text: '已结束', type: 'info' };
  }
  return { text: '进行中', type: 'primary' };
};

const getStudentExamStatus = (exam: any) => {
  const submission = exam.submission;
  if (submission) {
    if (submission.status === 'graded') {
      return { text: '已批改', type: 'success' };
    }
    if (submission.status === 'submitted') {
      return { text: '已提交', type: 'warning' };
    }
  }
  const now = new Date();
  const endTime = new Date(exam.end_time);
  if (endTime < now) {
    return { text: '已截止', type: 'info' };
  }
  return { text: '进行中', type: 'danger' };
};

const getGradingPercentage = (exam: any) => {
  const stats = exam.submission_stats;
  if (!stats || stats.total_students === 0) return 0;
  return Math.round((stats.graded_submissions / stats.total_students) * 100);
};

const getScorePercentage = (exam: any) => {
  const submission = exam.submission;
  if (!submission || !exam.total_points || exam.total_points === 0) return 0;
  return Math.round((submission.grade / exam.total_points) * 100);
};

const getProgressColor = (percentage: number) => {
  if (percentage < 60) return '#f56c6c';
  if (percentage < 85) return '#e6a23c';
  return '#67c23a';
};

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
};

const goToDetail = (exam: any) => {
  if (isTeacher.value) {
    router.push({ name: 'ExamDetail', params: { id: exam.id } });
  } else {
    // For students, check if they have a submission already
    if (exam.submission && (exam.submission.status === 'submitted' || exam.submission.status === 'graded')) {
      // If submitted or graded, go directly to the detail/result page
      router.push({ name: 'ExamDetail', params: { id: exam.id } });
    } else {
      // Otherwise, go to the notice page to start the exam
      router.push({ name: 'ExamNotice', params: { id: exam.id } });
    }
  }
};

const openCreateDialog = () => {
  editingExamId.value = null;
  dialogVisible.value = true;
};

const openEditDialog = (examId: number) => {
  editingExamId.value = examId;
  dialogVisible.value = true;
};

const handleSave = () => {
  dialogVisible.value = false;
  fetchData();
};

const handleCancel = () => {
  dialogVisible.value = false;
};

const deleteExam = async (examId: number) => {
  try {
    await api.delete(`/exams/${examId}/`);
    ElMessage.success('考试删除成功');
    exams.value = exams.value.filter(e => e.id !== examId);
  } catch (error) {
    console.error('Failed to delete exam:', error);
    ElMessage.error('删除失败，请稍后重试');
  }
};
</script>

<style scoped>
.exam-manager {
  padding: 20px;
  background-color: #f4f5f7;
  height: calc(100vh - 150px);
  overflow: auto;
}
.page-card {
  border-radius: 8px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
}
.custom-tabs {
  margin-bottom: 20px;
}
.loading-container, .empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
.exam-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}
.exam-card {
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.exam-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--el-box-shadow-light);
}
.card-content-wrapper {
  padding: 20px;
}
.card-header-line {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}
.exam-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
}
.exam-meta {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
}
.score-progress {
  margin-top: 16px;
}
.progress-text {
  font-size: 12px;
  color: #606266;
}
.card-footer-actions {
  border-top: 1px solid #ebeef5;
  padding: 10px 20px;
  text-align: right;
  background-color: #fcfcfc;
}
</style>
