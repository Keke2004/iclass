<template>
  <div class="profile-view">
    <h1 class="main-title">个人中心</h1>
    <el-card class="profile-card">
      <el-tabs v-model="activeTab" type="card">
        <el-tab-pane label="基本资料" name="basic">
          <div class="basic-info-tab">
            <el-row :gutter="40">
              <el-col :span="8" class="profile-sidebar">
                <div class="avatar-container">
                  <el-avatar :size="100" class="user-avatar">{{ user?.username?.charAt(0)?.toUpperCase() }}</el-avatar>
                </div>
                <h3 class="username">{{ user?.username }}</h3>
                <p class="user-id">ID: {{ user?.id }}</p>
              </el-col>
              <el-col :span="16">
                <h4 class="form-title">基本信息</h4>
                <el-form class="profile-form" :model="editableUser" label-width="80px" label-position="right">
                  <el-form-item label="姓名">
                    <el-input v-model="editableUser.first_name" placeholder="请输入姓名"></el-input>
                  </el-form-item>
                  <el-form-item label="性别">
                    <el-radio-group v-model="editableUser.gender">
                      <el-radio label="male">男</el-radio>
                      <el-radio label="female">女</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="手机号">
                    <el-input v-model="editableUser.phone_number" placeholder="请输入手机号"></el-input>
                  </el-form-item>
                  <el-form-item label="邮箱">
                    <el-input v-model="editableUser.email" placeholder="请输入邮箱"></el-input>
                  </el-form-item>
                  <el-form-item label="单位">
                    <el-input v-model="editableUser.school" placeholder="请输入单位/学校"></el-input>
                  </el-form-item>
                  <el-form-item label="学号/工号">
                    <el-input v-model="editableUser.student_id" placeholder="请输入学号/工号"></el-input>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="updateUserInfo">保存</el-button>
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
        <el-tab-pane label="密码管理" name="password">
          <div class="password-management-tab">
            <el-form :model="passwordData" label-width="100px" label-position="right" class="password-form">
              <el-form-item label="当前密码">
                <el-input type="password" v-model="passwordData.old_password" show-password></el-input>
              </el-form-item>
              <el-form-item label="新密码">
                <el-input type="password" v-model="passwordData.new_password1" show-password></el-input>
              </el-form-item>
              <el-form-item label="确认新密码">
                <el-input type="password" v-model="passwordData.new_password2" show-password></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="changePassword">确认修改</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { getProfile, updateProfile } from '@/services/api';
import { changePassword as changePasswordService } from '@/services/auth';
import { ElMessage } from 'element-plus';

const activeTab = ref('basic');
const user = ref<any>(null);

const editableUser = reactive({
  first_name: '',
  gender: '',
  phone_number: '',
  school: '',
  student_id: '',
  email: '',
});

const passwordData = reactive({
  old_password: '',
  new_password1: '',
  new_password2: '',
});

onMounted(async () => {
  try {
    const response = await getProfile();
    user.value = response.data;
    Object.assign(editableUser, {
      first_name: response.data.first_name || '',
      gender: response.data.gender || '',
      phone_number: response.data.phone_number || '',
      school: response.data.school || '',
      student_id: response.data.student_id || '',
      email: response.data.email || '',
    });
  } catch (error) {
    console.error('获取用户信息失败:', error);
    ElMessage.error('获取用户信息失败，请稍后重试。');
  }
});

const updateUserInfo = async () => {
  try {
    const response = await updateProfile(editableUser);
    user.value = response.data;
    ElMessage.success('用户信息更新成功！');
  } catch (error) {
    console.error('更新用户信息失败:', error);
    ElMessage.error('更新用户信息失败，请稍后重试。');
  }
};

const changePassword = async () => {
  if (passwordData.new_password1 !== passwordData.new_password2) {
    ElMessage.error('新密码和确认密码不匹配！');
    return;
  }
  try {
    await changePasswordService(passwordData);
    ElMessage.success('密码修改成功！');
    Object.assign(passwordData, {
      old_password: '',
      new_password1: '',
      new_password2: '',
    });
  } catch (error) {
    console.error('修改密码失败:', error);
    ElMessage.error('修改密码失败，请检查当前密码是否正确。');
  }
};
</script>

<style scoped>
.profile-view {
  padding: 20px;
  background-color: #f5f7fa;
}

.main-title {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 20px;
  color: #303133;
}

.profile-card {
  border: none;
}

:deep(.el-tabs--card > .el-tabs__header) {
  border-bottom: none;
  margin: 0 auto 20px;
  display: table;
}

:deep(.el-tabs__nav) {
  border: 1px solid #E4E7ED !important;
  border-radius: 4px;
  overflow: hidden;
}

:deep(.el-tabs__item) {
  border: none !important;
  height: 40px;
  line-height: 40px;
  padding: 0 25px !important;
  color: #606266;
  background-color: #fff;
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
}

:deep(.el-tabs__item.is-active) {
  color: #fff !important;
  background-color: #409EFF !important;
  border-right: none;
}

:deep(.el-tabs__item:not(.is-active):hover) {
  color: #409EFF;
  background-color: #f5f7fa;
}

:deep(.el-tabs__item + .el-tabs__item) {
  border-left: 1px solid #E4E7ED !important;
}

.basic-info-tab {
  padding-top: 20px;
}

.profile-sidebar {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #e4e7ed;
  padding: 0 20px;
}

.avatar-container {
  margin-bottom: 20px;
}

.user-avatar {
  background-color: #409EFF;
  font-size: 48px;
}

.username {
  font-size: 20px;
  font-weight: 500;
  margin: 10px 0;
}

.user-id {
  color: #999;
  font-size: 14px;
}

.form-title {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 20px;
  padding-left: 20px;
}

.profile-form {
  padding-left: 20px;
  max-width: 500px;
}

.password-management-tab {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.password-form {
  width: 100%;
  max-width: 400px;
}
</style>
