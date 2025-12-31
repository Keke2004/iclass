<template>
  <div class="task-manager">
    <div class="header">
      <h1>任务列表</h1>
      <div v-if="isTeacher">
        <el-button @click="showCreateCheckinDialog = true" type="primary">发起签到</el-button>
        <el-button @click="handleCreateRandomQuestion" type="success">发起提问</el-button>
      </div>
    </div>

    <div v-if="tasks.length > 0">
      <div class="task-section" v-if="ongoingTasks.length > 0">
        <h3 class="section-title">进行中 ({{ ongoingTasks.length }})</h3>
        <div class="task-list">
          <div v-for="task in ongoingTasks" :key="task.task_type + '-' + task.id" class="task-item">
            <div class="task-info" @click="handleTaskClick(task)">
              <div :class="['task-icon-wrapper', getTaskStatusClass(task)]">
                <div class="task-icon">{{ getTaskTypeName(task.task_type) }}</div>
              </div>
              <div class="task-title">{{ getTaskTitle(task) }}</div>
              <div class="task-time">开始时间: {{ formatTime(task.start_time || task.created_at) }}</div>
            </div>
            <el-button
                v-if="isTeacher && task.task_type === 'random_question'"
                @click.stop="handleDeleteRandomQuestion(task)"
                type="danger"
                link
                class="delete-btn"
            >删除</el-button>
          </div>
        </div>
      </div>

      <div class="task-section" v-if="endedTasks.length > 0">
        <h3 class="section-title">已结束 ({{ endedTasks.length }})</h3>
        <div class="task-list">
          <div v-for="task in endedTasks" :key="task.task_type + '-' + task.id" class="task-item">
            <div class="task-info" @click="handleTaskClick(task)">
              <div :class="['task-icon-wrapper', getTaskStatusClass(task)]">
                <div class="task-icon">{{ getTaskTypeName(task.task_type) }}</div>
              </div>
              <div class="task-title">{{ getTaskTitle(task) }}</div>
              <div class="task-time">结束时间: {{ formatTime(task.end_time || task.created_at) }}</div>
            </div>
            <el-button
                v-if="isTeacher && task.task_type === 'random_question'"
                @click.stop="handleDeleteRandomQuestion(task)"
                type="danger"
                link
                class="delete-btn"
            >删除</el-button>
          </div>
        </div>
      </div>
    </div>
    <el-empty v-else description="暂无任务"></el-empty>

    <el-dialog title="发起签到" v-model="showCreateCheckinDialog" width="30%">
      <el-form :model="newCheckinForm">
        <el-form-item label="签到标题">
          <el-input v-model="newCheckinForm.title" autocomplete="off"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateCheckinDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreateCheckin">创建</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getTasks, createCheckin, createRandomQuestion, deleteRandomQuestion } from '@/services/api';
import type { Checkin, RandomQuestion, Task } from '@/types';
import { ElMessage, ElMessageBox } from 'element-plus';

const route = useRoute();
const router = useRouter();
const courseId = Number(route.params.id);

const tasks = ref<Task[]>([]);
const showCreateCheckinDialog = ref(false);
const newCheckinForm = ref({
  title: '课堂签到',
});

const userRole = localStorage.getItem('user_role');
const isTeacher = computed(() => userRole === 'teacher');

const ongoingTasks = computed(() => tasks.value.filter(t => t.is_active));
const endedTasks = computed(() => tasks.value.filter(t => !t.is_active));

const fetchTasks = async () => {
  try {
    const response = await getTasks(courseId);
    tasks.value = response.data;
  } catch (error) {
    console.error('Failed to fetch tasks:', error);
    ElMessage.error('获取任务列表失败');
  }
};

const handleCreateCheckin = async () => {
  try {
    await createCheckin(courseId, { title: newCheckinForm.value.title });
    showCreateCheckinDialog.value = false;
    ElMessage.success('签到发起成功');
    fetchTasks(); // Refresh the list
  } catch (error) {
    console.error('Failed to create checkin:', error);
    ElMessage.error('发起签到失败');
  }
};

const handleCreateRandomQuestion = async () => {
  try {
    const response = await createRandomQuestion(courseId);
    const studentName = response.data.student.username;
    ElMessageBox.alert(`已抽中学生: ${studentName}`, '提问成功', {
      confirmButtonText: '好的',
      type: 'success',
    });
    fetchTasks(); // Refresh the list
  } catch (error) {
    console.error('Failed to create random question:', error);
    ElMessage.error('发起提问失败');
  }
};

const handleDeleteRandomQuestion = async (task: Task) => {
  try {
    await ElMessageBox.confirm(
        '确定要删除这个提问吗?',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
    );
    await deleteRandomQuestion(courseId, task.id);
    ElMessage.success('提问删除成功');
    fetchTasks(); // Refresh the list
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete random question:', error);
      ElMessage.error('删除提问失败');
    }
  }
};

const handleTaskClick = (task: Task) => {
  if (task.task_type === 'checkin') {
    router.push({ name: 'checkin-detail', params: { id: courseId, checkinId: task.id } });
  }
  // Random questions do not have a detail page, so do nothing.
};

const formatTime = (time: string) => {
  return new Date(time).toLocaleString();
};

const getTaskTypeName = (taskType: string) => {
  return taskType === 'checkin' ? '签到' : '提问';
};

const getTaskTitle = (task: Task) => {
  if (task.task_type === 'checkin') {
    return (task as Checkin).title;
  }
  if (task.task_type === 'random_question') {
    return `随机提问 - ${(task as RandomQuestion).student.username}`;
  }
  return '未知任务';
};

const getTaskStatusClass = (task: Task) => {
  return task.is_active ? 'status-ongoing' : 'status-ended';
};

onMounted(() => {
  fetchTasks();
});
</script>

<style scoped>
.task-manager {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.task-section {
  margin-bottom: 30px;
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
}
.task-list {
  background-color: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  transition: background-color 0.3s;
}
.task-info {
  display: flex;
  align-items: center;
  flex-grow: 1;
  cursor: pointer;
}
.task-item:not(:last-child) {
  border-bottom: 1px solid #e8e8e8;
}
.task-item:hover {
  background-color: #f5f7fa;
}
.task-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}
.task-icon {
  color: #fff;
  font-size: 14px;
}
.status-ongoing {
  background-color: #409eff; /* Blue for ongoing */
}
.status-ended {
  background-color: #c0c4cc; /* Gray for ended */
}
.task-title {
  flex-grow: 1;
  font-size: 16px;
  color: #333;
}
.task-time {
  font-size: 14px;
  color: #999;
  margin-left: 15px;
}
.delete-btn {
  margin-left: 15px;
}
</style>
