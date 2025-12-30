<template>
  <div class="task-manager">
    <div class="header">
      <h1>签到任务</h1>
      <el-button v-if="isTeacher" @click="showCreateCheckinDialog = true" type="primary">发起签到</el-button>
    </div>

    <div v-if="checkins.length > 0">
      <div class="checkin-section" v-if="ongoingCheckins.length > 0">
        <h3 class="section-title">进行中 ({{ ongoingCheckins.length }})</h3>
        <div class="checkin-list">
          <div v-for="checkin in ongoingCheckins" :key="checkin.id" class="checkin-item" @click="goToCheckinDetail(checkin.id)">
            <div class="checkin-icon-wrapper status-ongoing">
              <div class="checkin-icon">签到</div>
            </div>
            <div class="checkin-title">{{ checkin.title }}</div>
            <div class="checkin-time">开始时间: {{ formatTime(checkin.start_time) }}</div>
          </div>
        </div>
      </div>

      <div class="checkin-section" v-if="endedCheckins.length > 0">
        <h3 class="section-title">已结束 ({{ endedCheckins.length }})</h3>
        <div class="checkin-list">
          <div v-for="checkin in endedCheckins" :key="checkin.id" class="checkin-item" @click="goToCheckinDetail(checkin.id)">
            <div class="checkin-icon-wrapper status-ended">
              <div class="checkin-icon">签到</div>
            </div>
            <div class="checkin-title">{{ checkin.title }}</div>
            <div class="checkin-time">结束时间: {{ formatTime(checkin.end_time || checkin.start_time) }}</div>
          </div>
        </div>
      </div>
    </div>
    <el-empty v-else description="暂无签到任务"></el-empty>

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
import { getCheckins, createCheckin } from '@/services/api';
import type { Checkin } from '@/types';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const courseId = Number(route.params.id);

const checkins = ref<Checkin[]>([]);
const showCreateCheckinDialog = ref(false);
const newCheckinForm = ref({
  title: '课堂签到',
});

const userRole = localStorage.getItem('user_role');
const isTeacher = computed(() => userRole === 'teacher');

const ongoingCheckins = computed(() => checkins.value.filter(c => c.is_active));
const endedCheckins = computed(() => checkins.value.filter(c => !c.is_active));

const fetchCheckins = async () => {
  try {
    const response = await getCheckins(courseId);
    checkins.value = response.data;
  } catch (error) {
    console.error('Failed to fetch checkins:', error);
    ElMessage.error('获取签到列表失败');
  }
};

const handleCreateCheckin = async () => {
  try {
    await createCheckin(courseId, { title: newCheckinForm.value.title });
    showCreateCheckinDialog.value = false;
    ElMessage.success('签到发起成功');
    fetchCheckins(); // Refresh the list
  } catch (error) {
    console.error('Failed to create checkin:', error);
    ElMessage.error('发起签到失败');
  }
};

const goToCheckinDetail = (checkinId: number) => {
  router.push({ name: 'checkin-detail', params: { id: courseId, checkinId } });
};

const formatTime = (time: string) => {
  return new Date(time).toLocaleString();
};

onMounted(() => {
  fetchCheckins();
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
.checkin-section {
  margin-bottom: 30px;
}
.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
}
.checkin-list {
  background-color: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
}
.checkin-item {
  display: flex;
  align-items: center;
  padding: 15px;
  cursor: pointer;
  transition: background-color 0.3s;
}
.checkin-item:not(:last-child) {
  border-bottom: 1px solid #e8e8e8;
}
.checkin-item:hover {
  background-color: #f5f7fa;
}
.checkin-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}
.checkin-icon {
  color: #fff;
  font-size: 14px;
}
.status-ongoing {
  background-color: #409eff; /* Blue for ongoing */
}
.status-ended {
  background-color: #c0c4cc; /* Gray for ended */
}
.checkin-title {
  flex-grow: 1;
  font-size: 16px;
  color: #333;
}
.checkin-time {
  font-size: 14px;
  color: #999;
  margin-left: 15px;
}
</style>
