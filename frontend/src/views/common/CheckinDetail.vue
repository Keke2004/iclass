<template>
  <div v-if="checkin" class="checkin-detail-container">
    <el-page-header @back="goBack" :content="checkin.title"></el-page-header>

    <div class="info-card">
      <p><strong>状态:</strong> {{ checkin.is_active ? '进行中' : '已结束' }}</p>
      <p><strong>开始时间:</strong> {{ formatTime(checkin.start_time) }}</p>
      <p v-if="checkin.end_time"><strong>结束时间:</strong> {{ formatTime(checkin.end_time) }}</p>
    </div>

    <!-- 学生视图 -->
    <div v-if="!isTeacher">
      <div v-if="checkin.is_active && !checkin.is_checked_in" class="action-card">
        <el-button type="primary" @click="handleStudentCheckin" :loading="loading">立即签到</el-button>
      </div>
      <div v-if="checkin.is_checked_in" class="success-message">
        <el-icon color="green" size="50"><CircleCheckFilled /></el-icon>
        <p>签到成功</p>
      </div>
       <div v-if="!checkin.is_active && !checkin.is_checked_in" class="info-message">
        <p>签到已结束</p>
      </div>
    </div>

    <!-- 教师视图 -->
    <div v-if="isTeacher">
      <div class="action-card">
        <el-button v-if="checkin.is_active" type="warning" @click="handleEndCheckin" :loading="loading">结束签到</el-button>
        <el-button v-else disabled>签到已结束</el-button>
        <el-button type="danger" @click="handleDeleteCheckin" :loading="loading">删除签到</el-button>
      </div>

      <div class="records-card">
        <h3>签到记录 ({{ records.length }})</h3>
        <el-table :data="records" stripe style="width: 100%">
          <el-table-column prop="student.username" label="姓名"></el-table-column>
          <el-table-column prop="checkin_time" label="签到时间">
            <template #default="scope">
              {{ formatTime(scope.row.checkin_time) }}
            </template>
          </el-table-column>
          <el-table-column label="状态">
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)">
                {{ getStatusDisplayName(scope.row.status) }}
                <span v-if="scope.row.is_manual"> (代签)</span>
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="proxy-card">
        <h3>代签/修改状态</h3>
        <el-select v-model="selectedStudent" placeholder="选择学生" filterable>
          <el-option
            v-for="student in allStudents"
            :key="student.id"
            :label="student.username"
            :value="student.id">
          </el-option>
        </el-select>
        <el-select v-model="selectedStatus" placeholder="选择状态">
          <el-option
            v-for="status in statusOptions"
            :key="status.value"
            :label="status.label"
            :value="status.value">
          </el-option>
        </el-select>
        <el-button type="primary" @click="handleProxyCheckin" :loading="proxyLoading" :disabled="!selectedStudent">确认操作</el-button>
      </div>
    </div>
  </div>
  <div v-else>
    <p>加载中...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getCheckinDetail, studentCheckin, endCheckin, proxyCheckin, getCourseMembers, deleteCheckin } from '@/services/api';
import type { Checkin, CheckinRecord, User } from '@/types';
import { CircleCheckFilled } from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();

const checkin = ref<Checkin | null>(null);
const records = ref<CheckinRecord[]>([]);
const allStudents = ref<User[]>([]);
const loading = ref(false);
const proxyLoading = ref(false);
const selectedStudent = ref<number | null>(null);
const selectedStatus = ref('present'); // 默认代签状态为'出勤'

const statusOptions = [
  { value: 'present', label: '出勤' },
  { value: 'late', label: '迟到' },
  { value: 'absent', label: '缺勤' },
  { value: 'sick_leave', label: '病假' },
  { value: 'personal_leave', label: '事假' },
];

const getStatusDisplayName = (status: string) => {
  const option = statusOptions.find(o => o.value === status);
  return option ? option.label : '未知';
};

const getStatusTagType = (status: string) => {
  switch (status) {
    case 'present':
      return 'success';
    case 'late':
      return 'warning';
    case 'absent':
      return 'danger';
    case 'sick_leave':
    case 'personal_leave':
      return 'info';
    default:
      return 'primary';
  }
};

const courseId = Number(route.params.id);
const checkinId = Number(route.params.checkinId);
const isTeacher = computed(() => localStorage.getItem('user_role') === 'teacher');

const fetchCheckinDetail = async () => {
  try {
    const response = await getCheckinDetail(courseId, checkinId);
    checkin.value = response.data;
    records.value = response.data.records || [];
  } catch (error) {
    ElMessage.error('获取签到详情失败');
    console.error(error);
  }
};

const fetchCourseMembers = async () => {
  if (!isTeacher.value) return;
  try {
    const response = await getCourseMembers(courseId);
    // The backend returns an object with 'teacher' and 'students' keys.
    allStudents.value = response.data.students.filter((user: User) => user.role === 'student');
  } catch (error) {
    ElMessage.error('获取学生列表失败');
  }
}

// 代签下拉列表显示所有学生，因为教师可能需要修改已签到学生的状态
// const uncheckinStudents = computed(() => {
//   const checkedInStudentIds = new Set(records.value.map(r => r.student.id));
//   return allStudents.value.filter(s => !checkedInStudentIds.has(s.id));
// });

onMounted(() => {
  fetchCheckinDetail();
  fetchCourseMembers();
});

const goBack = () => {
  router.push(`/courses/${courseId}/tasks`);
};

const formatTime = (timeStr: string | null) => {
  if (!timeStr) {
    return '---';
  }
  return new Date(timeStr).toLocaleString();
};

const handleStudentCheckin = async () => {
  loading.value = true;
  try {
    await studentCheckin(courseId, checkinId);
    ElMessage.success('签到成功！');
    await fetchCheckinDetail(); // 重新获取数据刷新状态
  } catch (error: any) {
    if (error.response && error.response.data.detail) {
        ElMessage.error(error.response.data.detail);
    } else {
        ElMessage.error('签到失败');
    }
  } finally {
    loading.value = false;
  }
};

const handleEndCheckin = async () => {
  ElMessageBox.confirm('确定要结束本次签到吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    loading.value = true;
    try {
      await endCheckin(courseId, checkinId);
      ElMessage.success('签到已结束');
      await fetchCheckinDetail();
    } catch (error) {
      ElMessage.error('操作失败');
    } finally {
      loading.value = false;
    }
  });
};

const handleDeleteCheckin = async () => {
  ElMessageBox.confirm('确定要删除本次签到吗？此操作不可恢复。', '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'error',
  }).then(async () => {
    loading.value = true;
    try {
      await deleteCheckin(courseId, checkinId);
      ElMessage.success('签到已删除');
      goBack(); // Redirect to the list page
    } catch (error) {
      ElMessage.error('删除失败');
    } finally {
      loading.value = false;
    }
  });
};

const handleProxyCheckin = async () => {
  if (!selectedStudent.value || !selectedStatus.value) {
    ElMessage.warning('请选择学生和要设置的状态');
    return;
  }
  proxyLoading.value = true;
  try {
    await proxyCheckin(courseId, checkinId, selectedStudent.value, selectedStatus.value);
    ElMessage.success('操作成功');
    selectedStudent.value = null;
    // selectedStatus.value = 'present'; // Optionally reset status
    await fetchCheckinDetail(); // 刷新签到记录
    // Since we now allow modifying existing records, we don't need to refresh the student list based on who has/hasn't checked in.
    // await fetchCourseMembers(); 
  } catch (error) {
    ElMessage.error('操作失败');
    console.error(error);
  } finally {
    proxyLoading.value = false;
  }
};
</script>

<style scoped>
.checkin-detail-container {
  padding: 20px;
}
.info-card, .action-card, .records-card, .proxy-card, .success-message, .info-message {
  background-color: #fff;
  padding: 20px;
  margin-top: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}
.success-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 18px;
  color: #67c23a;
}
.info-message {
  text-align: center;
  font-size: 18px;
  color: #909399;
}
.proxy-card .el-select {
  margin-right: 10px;
  width: 150px;
}
.action-card {
  display: flex;
}
.action-card .el-button {
  margin-left: 10px;
}
.action-card .el-button:first-child {
  margin-left: 0;
}
</style>
