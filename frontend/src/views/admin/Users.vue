<template>
  <div class="users-container">
    <h1>用户管理</h1>
    <el-table :data="users" v-loading="loading" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="email" label="邮箱" />
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
      <el-form v-if="currentUser" :model="currentUser">
        <el-form-item label="用户名">
          <el-input v-model="currentUser.username" disabled />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="currentUser.role" placeholder="选择角色">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
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
}

const users = ref<User[]>([]);
const loading = ref(true);
const editDialogVisible = ref(false);
const currentUser = ref<User | null>(null);

const fetchUsers = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/users/');
    users.value = response.data;
  } catch (error) {
    console.error('获取用户列表失败:', error);
    ElMessage.error('无法加载用户列表。');
  } finally {
    loading.value = false;
  }
};

const openEditDialog = (user: User) => {
  // 创建一个副本以避免直接修改表格数据
  currentUser.value = { ...user };
  editDialogVisible.value = true;
};

const updateUser = async () => {
  if (!currentUser.value) return;
  try {
    await apiClient.patch(`/users/${currentUser.value.id}/`, {
      role: currentUser.value.role,
    });
    ElMessage.success('用户角色更新成功！');
    editDialogVisible.value = false;
    await fetchUsers(); // 重新加载数据
  } catch (error) {
    console.error('更新用户失败:', error);
    ElMessage.error('更新用户失败。');
  }
};

const deleteUser = async (userId: number) => {
  try {
    await apiClient.delete(`/users/${userId}/`);
    ElMessage.success('用户删除成功！');
    await fetchUsers(); // 重新加载数据
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
</style>
