<template>
  <div class="task-manager">
    <div class="header">
      <h1>签到任务</h1>
      <el-button v-if="isTeacher" @click="showCreateCheckinDialog = true" type="primary">发起签到</el-button>
    </div>

    <el-timeline v-if="checkins.length > 0">
      <el-timeline-item
        v-for="checkin in checkins"
        :key="checkin.id"
        :timestamp="formatTime(checkin.start_time)"
        placement="top"
      >
        <el-card @click="goToCheckinDetail(checkin.id)" class="checkin-card">
          <h4>{{ checkin.title }}</h4>
          <p>
            状态:
            <el-tag :type="checkin.is_active ? 'success' : 'info'">
              {{ checkin.is_active ? '进行中' : '已结束' }}
            </el-tag>
          </p>
          <p v-if="!isTeacher">
            我的状态:
            <el-tag :type="checkin.is_checked_in ? 'success' : 'danger'">
              {{ checkin.is_checked_in ? '已签到' : '未签到' }}
            </el-tag>
          </p>
        </el-card>
      </el-timeline-item>
    </el-timeline>
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
.checkin-card {
  cursor: pointer;
}
.checkin-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
