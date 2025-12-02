<template>
  <div class="users-container">
    <h1>用户管理</h1>
    <div class="toolbar">
      <div class="filters-grid">
        <el-input v-model="filters.username" placeholder="用户名" @keyup.enter="handleSearch" clearable />
        <el-input v-model="filters.first_name" placeholder="姓名" @keyup.enter="handleSearch" clearable />
        <el-input v-model="filters.email" placeholder="邮箱" @keyup.enter="handleSearch" clearable />
        <el-input v-model="filters.school" placeholder="单位/学校" @keyup.enter="handleSearch" clearable />
        <el-input v-model="filters.student_id" placeholder="学号/工号" @keyup.enter="handleSearch" clearable />
        <el-select v-model="filters.role" placeholder="角色" clearable>
          <el-option label="学生" value="student" />
          <el-option label="教师" value="teacher" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </div>
      <div class="actions">
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>
    <el-table :data="users" v-loading="loading" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="first_name" label="姓名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="school" label="单位/学校" />
      <el-table-column prop="student_id" label="学号/工号" />
      <el-table-column prop="role" label="角色" width="120" />
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-popconfirm
            title="确定要删除该用户吗？"
            @confirm="deleteUser(scope.row.id)"
          >
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 编辑用户对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑用户">
      <el-form v-if="currentUser" :model="currentUser" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="currentUser.username" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="currentUser.first_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="currentUser.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="currentUser.role" placeholder="选择角色">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="currentUser.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="currentUser.phone_number" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="currentUser.school" />
        </el-form-item>
        <el-form-item label="学号/工号">
          <el-input v-model="currentUser.student_id" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateUser">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '../../services/api';
import { ElMessage } from 'element-plus';

interface User {
  id: number;
  username: string;
  email: string;
  role: 'student' | 'teacher' | 'admin';
  first_name: string;
  gender: 'male' | 'female' | null;
  phone_number: string | null;
  school: string | null;
  student_id: string | null;
}

const users = ref<User[]>([]);
const loading = ref(true);
const editDialogVisible = ref(false);
const currentUser = ref<User | null>(null);

const initialFilters = {
  username: '',
  first_name: '',
  email: '',
  school: '',
  student_id: '',
  role: '',
};
const filters = ref({ ...initialFilters });

const fetchUsers = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    // Iterate over the filters object and append non-empty values to params
    for (const key in filters.value) {
      const value = filters.value[key as keyof typeof filters.value];
      if (value) {
        params.append(key, value);
      }
    }
    const response = await apiClient.get(`/users/`, { params });
    users.value = response.data;
  } catch (error) {
    console.error('获取用户列表失败:', error);
    ElMessage.error('无法加载用户列表。');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  fetchUsers();
};

const resetFilters = () => {
  filters.value = { ...initialFilters };
  fetchUsers();
};

const openEditDialog = (user: User) => {
  // 创建一个副本以避免直接修改表格数据
  currentUser.value = { ...user };
  editDialogVisible.value = true;
};

const updateUser = async () => {
  if (!currentUser.value) return;
  try {
    // 从 currentUser 中提取需要更新的字段
    const { role, first_name, email, gender, phone_number, school, student_id } = currentUser.value;
    const payload = { role, first_name, email, gender, phone_number, school, student_id };

    await apiClient.patch(`/users/${currentUser.value.id}/`, payload);
    ElMessage.success('用户信息更新成功！');
    editDialogVisible.value = false;
    await fetchUsers(); // 使用当前筛选条件重新加载数据
  } catch (error) {
    console.error('更新用户失败:', error);
    ElMessage.error('更新用户失败。');
  }
};

const deleteUser = async (userId: number) => {
  try {
    await apiClient.delete(`/users/${userId}/`);
    ElMessage.success('用户删除成功！');
    await fetchUsers(); // 使用当前筛选条件重新加载数据
  } catch (error) {
    console.error('删除用户失败:', error);
    ElMessage.error('删除用户失败。');
  }
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.users-container {
  padding: 20px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.filters-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  flex-grow: 1;
  margin-right: 20px; /* Add margin to the right of filters */
}
.filters-grid .el-input,
.filters-grid .el-select {
  width: 100%;
}
.actions {
  display: flex;
  gap: 10px;
}
</style>
