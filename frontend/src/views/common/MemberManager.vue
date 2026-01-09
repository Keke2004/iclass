<template>
  <div class="member-manager">
    <h1>课程成员</h1>

    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>教师</span>
        </div>
      </template>
      <div class="user-item">
        <el-avatar>{{ teacher.username ? teacher.username[0].toUpperCase() : '' }}</el-avatar>
        <span class="username">{{ teacher.username }}</span>
        <el-tag type="success" size="small">教师</el-tag>
      </div>
    </el-card>

    <el-card class="box-card student-card">
      <template #header>
        <div class="card-header">
          <span>学生 ({{ students.length }})</span>
          <el-button v-if="isTeacher" type="primary" @click="addStudentDialogVisible = true">添加学生</el-button>
        </div>
      </template>
      <div v-for="student in students" :key="student.id" class="user-item">
        <el-avatar>{{ student.username ? student.username[0].toUpperCase() : '' }}</el-avatar>
        <span class="username">{{ student.username }}</span>
        <el-tag type="info" size="small">学生</el-tag>
        <el-button v-if="isTeacher" type="danger" link @click="removeStudent(student.id)" class="remove-btn">移除</el-button>
      </div>
      <el-empty v-if="students.length === 0" description="暂无学生"></el-empty>
    </el-card>

    <!-- Add Student Dialog -->
    <el-dialog v-model="addStudentDialogVisible" title="添加学生" width="30%">
      <el-form>
        <el-form-item label="选择学生">
          <el-select v-model="studentIdToAdd" placeholder="请选择要添加的学生" filterable>
            <el-option
              v-for="student in availableStudents"
              :key="student.id"
              :label="student.username"
              :value="student.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addStudentDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addStudent">确认添加</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage, ElCard, ElAvatar, ElTag, ElButton, ElEmpty, ElDialog, ElForm, ElFormItem, ElSelect, ElOption } from 'element-plus';

interface User {
  id: number;
  username: string;
  role: string;
}

const route = useRoute();
const teacher = ref<User>({} as User);
const students = ref<User[]>([]);
const availableStudents = ref<User[]>([]);
const addStudentDialogVisible = ref(false);
const studentIdToAdd = ref<number | null>(null);

const courseId = route.params.id;
const isTeacher = ref(localStorage.getItem('user_role') === 'teacher');

const fetchMembers = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId}/`);
    teacher.value = response.data.teacher;
    students.value = response.data.students;
  } catch (error) {
    console.error('获取成员列表失败:', error);
    ElMessage.error('获取成员列表失败');
  }
};

const fetchAvailableStudents = async () => {
  try {
    const response = await apiClient.get(`/users/?role=student&exclude_course=${courseId}`);
    availableStudents.value = response.data.results;
  } catch (error) {
    console.error('获取可用学生列表失败:', error);
    ElMessage.error('获取可用学生列表失败');
  }
};

const addStudent = async () => {
  if (!studentIdToAdd.value) {
    ElMessage.warning('请选择一个学生');
    return;
  }
  try {
    await apiClient.post(`/courses/${courseId}/add_student/`, { student_id: studentIdToAdd.value });
    ElMessage.success('学生添加成功');
    addStudentDialogVisible.value = false;
    studentIdToAdd.value = null;
    fetchMembers(); // Refresh the list
    fetchAvailableStudents(); // Also refresh the available students list
  } catch (error: any) {
    console.error('添加学生失败:', error);
    const errorMsg = error.response?.data?.error || '添加学生失败';
    ElMessage.error(errorMsg);
  }
};

const removeStudent = async (studentId: number) => {
  try {
    await apiClient.post(`/courses/${courseId}/remove_student/`, { student_id: studentId });
    ElMessage.success('学生移除成功');
    fetchMembers(); // Refresh the list
    fetchAvailableStudents(); // Also refresh the available students list
  } catch (error: any) {
    console.error('移除学生失败:', error);
    const errorMsg = error.response?.data?.error || '移除学生失败';
    ElMessage.error(errorMsg);
  }
};

onMounted(() => {
  fetchMembers();
  fetchAvailableStudents();
});
</script>

<style scoped>
.member-manager {
  padding: 20px;
}
.box-card {
  margin-bottom: 20px;
}
.student-card {
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.user-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}
.user-item:last-child {
  border-bottom: none;
}
.username {
  margin-left: 10px;
  flex-grow: 1;
}
.remove-btn {
  margin-left: auto;
}
</style>
