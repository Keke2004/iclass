<template>
  <div class="task-manager">
    <div class="header">
      <h1>任务列表</h1>
      <div v-if="isTeacher">
        <el-button @click="showCreateCheckinDialog = true" type="primary">发起签到</el-button>
        <el-button @click="handleCreateRandomQuestion" type="success">发起提问</el-button>
        <el-button @click="showCreateVoteDialog = true" type="warning">发起投票</el-button>
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

    <el-dialog title="发起投票" v-model="showCreateVoteDialog" width="40%">
      <el-form :model="newVoteForm" label-width="80px">
        <el-form-item label="投票标题">
          <el-input v-model="newVoteForm.title" autocomplete="off"></el-input>
        </el-form-item>
        <el-form-item
          v-for="(choice, index) in newVoteForm.choices"
          :key="index"
          :label="'选项 ' + (index + 1)"
        >
          <el-input v-model="choice.text" style="width: 80%; margin-right: 10px;"></el-input>
          <el-button @click.prevent="removeVoteOption(index)" type="danger" link>删除</el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="addVoteOption" type="primary" link>+ 添加选项</el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateVoteDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreateVote">创建</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getTasks, createCheckin, createRandomQuestion, deleteRandomQuestion, createVote } from '@/services/api';
import type { Checkin, RandomQuestion, Task, User, Vote } from '@/types';
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();
const courseId = Number(route.params.id);

const tasks = ref<Task[]>([]);
const showCreateCheckinDialog = ref(false);
const newCheckinForm = ref({
  title: '课堂签到',
});

const showCreateVoteDialog = ref(false);
const newVoteForm = ref({
  title: '',
  choices: [{ text: '' }, { text: '' }],
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
    const newQuestion = response.data;
    ElMessage.success('发起提问成功');
    router.push({ name: 'RandomQuestionDetail', params: { id: courseId, taskId: newQuestion.id } });
    fetchTasks(); // Refresh the list
  } catch (error) {
    console.error('Failed to create random question:', error);
    ElMessage.error('发起提问失败');
  }
};

const addVoteOption = () => {
  newVoteForm.value.choices.push({ text: '' });
};

const removeVoteOption = (index: number) => {
  if (newVoteForm.value.choices.length > 1) {
    newVoteForm.value.choices.splice(index, 1);
  } else {
    ElMessage.warning('至少需要一个选项');
  }
};

const handleCreateVote = async () => {
  if (!newVoteForm.value.title.trim()) {
    ElMessage.error('请输入投票标题');
    return;
  }
  const validChoices = newVoteForm.value.choices.filter(c => c.text.trim() !== '');
  if (validChoices.length < 2) {
    ElMessage.error('请至少输入两个有效选项');
    return;
  }

  try {
    await createVote(courseId, { title: newVoteForm.value.title, choices_create: validChoices });
    showCreateVoteDialog.value = false;
    newVoteForm.value = { title: '', choices: [{ text: '' }, { text: '' }] }; // Reset form
    ElMessage.success('投票发起成功');
    fetchTasks(); // Refresh the list
  } catch (error) {
    console.error('Failed to create vote:', error);
    ElMessage.error('发起投票失败');
  }
};

const handleDeleteTask = async (task: Task) => {
  const taskTypeName = getTaskTypeName(task.task_type);
  try {
    await ElMessageBox.confirm(
        `确定要删除这个${taskTypeName}吗?`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
    );

    if (task.task_type === 'random_question') {
      await deleteRandomQuestion(courseId, task.id);
    }

    ElMessage.success(`${taskTypeName}删除成功`);
    fetchTasks(); // Refresh the list
  } catch (error) {
    if (error !== 'cancel') {
      console.error(`Failed to delete ${task.task_type}:`, error);
      ElMessage.error(`删除${taskTypeName}失败`);
    }
  }
};

const handleTaskClick = (task: Task) => {
  if (task.task_type === 'checkin') {
    router.push({ name: 'checkin-detail', params: { id: courseId, checkinId: task.id } });
  } else if (task.task_type === 'vote') {
    router.push({ name: 'vote-detail', params: { id: courseId, voteId: task.id } });
  } else if (task.task_type === 'random_question') {
    router.push({ name: 'RandomQuestionDetail', params: { id: courseId, taskId: task.id } });
  }
};

const formatTime = (time: string) => {
  return new Date(time).toLocaleString();
};

const getTaskTypeName = (taskType: string) => {
  switch (taskType) {
    case 'checkin':
      return '签到';
    case 'random_question':
      return '提问';
    case 'vote':
      return '投票';
    default:
      return '未知';
  }
};

const getTaskTitle = (task: Task) => {
  switch (task.task_type) {
    case 'checkin':
      return (task as Checkin).title;
    case 'random_question':
      const rq = task as RandomQuestion;
      if (rq.student) {
        return `随机提问 - ${rq.student.username}`;
      }
      return '随机提问';
    case 'vote':
      return (task as Vote).title;
    default:
      return '未知任务';
  }
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
