<template>
  <div class="assignment-manager">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span>课程作业</span>
          <el-button v-if="isTeacher" type="primary" @click="openCreateDialog" :icon="Plus">创建新作业</el-button>
        </div>
      </template>
      
      <el-tabs v-if="isTeacher" v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="全部作业" name="all"></el-tab-pane>
        <el-tab-pane label="批改中" name="grading"></el-tab-pane>
        <el-tab-pane label="批改完成" name="graded_completed"></el-tab-pane>
      </el-tabs>
      <el-tabs v-else v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="全部作业" name="all"></el-tab-pane>
        <el-tab-pane label="进行中" name="pending"></el-tab-pane>
        <el-tab-pane label="已完成" name="completed"></el-tab-pane>
      </el-tabs>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="filteredAssignments.length === 0" class="empty-state">
        <el-empty description="暂无作业"></el-empty>
      </div>

      <div v-else class="assignment-grid">
        <el-card v-for="assignment in filteredAssignments" :key="assignment.id" class="assignment-card" shadow="hover" @click="goToDetail(assignment.id)">
          <div class="card-content-wrapper">
            <div class="card-header-line">
              <span class="assignment-title">{{ assignment.title }}</span>
              <el-tag v-if="isTeacher" :type="getTeacherAssignmentStatus(assignment).type" size="small" effect="light">
                {{ getTeacherAssignmentStatus(assignment).text }}
              </el-tag>
              <el-tag v-else :type="getSubmissionStatus(assignment).type" size="small" effect="light">
                {{ getSubmissionStatus(assignment).text }}
              </el-tag>
            </div>
            <div class="assignment-meta">
              <span>截止时间: {{ formatDate(assignment.due_date) }}</span>
              <span>总分: {{ assignment.total_points }}</span>
            </div>
            <!-- Teacher's View: Grading Progress -->
            <div v-if="isTeacher && assignment.submission_stats" class="score-progress">
              <el-progress :percentage="getGradingPercentage(assignment)" :stroke-width="10" :color="getProgressColor(getGradingPercentage(assignment))">
                  <span class="progress-text">
                    已批改 {{ assignment.submission_stats.graded_submissions }} / {{ assignment.submission_stats.total_students }}
                  </span>
              </el-progress>
            </div>
            <!-- Student's View: Score Progress -->
            <div v-if="!isTeacher && getSubmissionStatus(assignment).key === 'graded'" class="score-progress">
              <el-progress :percentage="getScorePercentage(assignment)" :stroke-width="10" :color="getProgressColor(getScorePercentage(assignment))">
                <span class="progress-text">{{ getSubmissionGrade(assignment) }} / {{ assignment.total_points }}</span>
              </el-progress>
            </div>
          </div>
          <div class="card-footer-actions">
            <el-button type="primary" link @click="goToDetail(assignment.id)">查看详情</el-button>
            <el-button v-if="isTeacher" type="primary" link @click.stop="openEditDialog(assignment.id)">编辑</el-button>
            <el-popconfirm
              v-if="isTeacher"
              title="确定要删除这个作业吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm.stop="deleteAssignment(assignment.id)"
            >
              <template #reference>
                <el-button type="danger" link @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- Assignment Editor Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingAssignmentId ? '编辑作业' : '创建新作业'"
      width="80%"
      top="5vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div style="height: 75vh; overflow-y: auto;">
        <AssignmentEditor
          v-if="dialogVisible"
          :assignment-id="editingAssignmentId"
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
import AssignmentEditor from '@/views/teacher/AssignmentEditor.vue';

const router = useRouter();
const route = useRoute();
const userRole = localStorage.getItem('user_role');
const courseId = computed(() => route.params.id as string);
const activeTab = ref('all');
const loading = ref(true);
const assignments = ref<any[]>([]);
const submissions = ref<any[]>([]);
const dialogVisible = ref(false);
const editingAssignmentId = ref<number | null>(null);

async function fetchData() {
  if (!courseId.value) {
    console.error("Course ID not found in route params.");
    loading.value = false;
    return;
  }
  try {
    loading.value = true;
    const [assignmentsRes, submissionsRes] = await Promise.all([
      api.get(`/assignments/?course=${courseId.value}`),
      api.get('/submissions/')
    ]);
    
    assignments.value = assignmentsRes.data.map((assignment: any) => ({
      ...assignment,
      total_points: assignment.questions.reduce((sum: number, q: any) => sum + q.points, 0)
    }));

    submissions.value = submissionsRes.data;
  } catch (error) {
    console.error('Failed to fetch assignments or submissions:', error);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);

const filteredAssignments = computed(() => {
  if (activeTab.value === 'all') {
    return assignments.value;
  }

  if (isTeacher.value) {
    return assignments.value.filter(assignment => {
      const stats = assignment.submission_stats;
      if (!stats) return false;
      if (activeTab.value === 'grading') {
        // Show if there are submissions that are not yet fully graded
        return stats.graded_submissions < stats.total_students;
      }
      if (activeTab.value === 'graded_completed') {
        // Show if all students' submissions are graded (or if there are no students)
        return stats.graded_submissions === stats.total_students;
      }
      return false;
    });
  } else {
    return assignments.value.filter(assignment => {
      const statusInfo = getSubmissionStatus(assignment);
      if (activeTab.value === 'completed') {
        return statusInfo.key === 'graded' || statusInfo.key === 'submitted';
      }
      if (activeTab.value === 'pending') {
        return statusInfo.key === 'pending';
      }
      return false;
    });
  }
});

const getTeacherAssignmentStatus = (assignment: any) => {
  const stats = assignment.submission_stats;
  if (!stats) return { text: '加载中', type: 'info' };

  if (stats.graded_submissions === stats.total_students) {
    return { text: '批改完成', type: 'success' };
  }
  if (stats.total_submissions > 0) {
    return { text: '批改中', type: 'warning' };
  }
  const dueDate = new Date(assignment.due_date);
  if (dueDate < new Date()) {
    return { text: '已截止', type: 'info' };
  }
  return { text: '进行中', type: 'primary' };
};

const getGradingPercentage = (assignment: any) => {
  const stats = assignment.submission_stats;
  if (!stats || stats.total_students === 0) return 0;
  return Math.round((stats.graded_submissions / stats.total_students) * 100);
};

const getSubmissionStatus = (assignment: any) => {
  const submission = submissions.value.find(s => s.assignment === assignment.id);
  if (submission) {
    if (submission.status === 'graded') {
      return { text: '已批改', type: 'success', key: 'graded' };
    }
    return { text: '已提交', type: 'warning', key: 'submitted' };
  }
  const dueDate = new Date(assignment.due_date);
  if (dueDate < new Date()) {
    return { text: '已截止', type: 'info', key: 'missed' };
  }
  return { text: '进行中', type: 'danger', key: 'pending' };
};

const getSubmissionGrade = (assignment: any) => {
  const submission = submissions.value.find(s => s.assignment === assignment.id);
  return submission ? submission.grade : 0;
};

const getScorePercentage = (assignment: any) => {
  const grade = getSubmissionGrade(assignment);
  if (!assignment.total_points || assignment.total_points === 0) return 0;
  return Math.round((grade / assignment.total_points) * 100);
};

const getProgressColor = (percentage: number) => {
  if (percentage < 60) return '#f56c6c';
  if (percentage < 85) return '#e6a23c';
  return '#67c23a';
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
};

const goToDetail = (assignmentId: number) => {
  router.push({ name: 'assignment-detail', params: { id: assignmentId } });
};

const isTeacher = computed(() => userRole === 'teacher');

const openCreateDialog = () => {
  editingAssignmentId.value = null;
  dialogVisible.value = true;
};

const openEditDialog = (assignmentId: number) => {
  editingAssignmentId.value = assignmentId;
  dialogVisible.value = true;
};

const handleSave = () => {
  dialogVisible.value = false;
  fetchData();
};

const handleCancel = () => {
  dialogVisible.value = false;
};

const deleteAssignment = async (assignmentId: number) => {
  try {
    await api.delete(`/assignments/${assignmentId}/`);
    ElMessage.success('作业删除成功');
    assignments.value = assignments.value.filter(a => a.id !== assignmentId);
  } catch (error) {
    console.error('Failed to delete assignment:', error);
    ElMessage.error('删除失败，请稍后重试');
  }
};
</script>

<style scoped>
.assignment-manager {
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
.assignment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}
.assignment-card {
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.assignment-card:hover {
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
.assignment-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
}
.assignment-meta {
  font-size: 13px;
  color: #909399;
  margin-bottom: 16px;
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
