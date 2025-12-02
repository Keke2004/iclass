<template>
  <div class="account-management">
    <h1 class="title">个人中心</h1>
    <div class="tabs">
      <div
        class="tab"
        :class="{ active: activeTab === 'basic' }"
        @click="activeTab = 'basic'"
      >
        基本资料
      </div>
      <div
        class="tab"
        :class="{ active: activeTab === 'password' }"
        @click="activeTab = 'password'"
      >
        密码管理
      </div>
    </div>

    <div class="tab-content">
      <!-- 基本资料 -->
      <div v-if="activeTab === 'basic'" class="basic-info">
        <form @submit.prevent="updateUserInfo">
          <div class="info-item">
            <span class="label">用户名</span>
            <span class="value">{{ user?.username }}</span>
          </div>
          <div class="info-item">
            <span class="label">姓名</span>
            <div class="value">
              <input type="text" v-model="editableUser.first_name" placeholder="请输入姓名" />
            </div>
          </div>
          <div class="info-item">
            <span class="label">ID</span>
            <span class="value">{{ user?.id }}</span>
          </div>
          <div class="info-item">
            <span class="label">性别</span>
            <div class="value">
              <label><input type="radio" v-model="editableUser.gender" value="male" /> 男</label>
              <label><input type="radio" v-model="editableUser.gender" value="female" /> 女</label>
            </div>
          </div>
          <div class="info-item">
            <span class="label">手机号</span>
            <div class="value">
              <input type="text" v-model="editableUser.phone_number" placeholder="请输入手机号" />
            </div>
          </div>
          <div class="info-item">
            <span class="label">单位</span>
            <div class="value">
              <input type="text" v-model="editableUser.school" placeholder="请输入单位/学校" />
            </div>
          </div>
           <div class="info-item">
            <span class="label">学号/工号</span>
            <div class="value">
              <input type="text" v-model="editableUser.student_id" placeholder="请输入学号/工号" />
            </div>
          </div>
          <div class="info-item">
            <span class="label"></span>
            <div class="value">
              <button type="submit" class="save-btn">保存</button>
            </div>
          </div>
        </form>
      </div>

      <!-- 密码管理 -->
      <div v-if="activeTab === 'password'" class="password-management">
        <form @submit.prevent="changePassword">
          <div class="form-group">
            <label for="current-password">当前密码</label>
            <div class="password-input">
              <input :type="passwordVisible.current ? 'text' : 'password'" id="current-password" v-model="passwordData.old_password" />
              <span class="toggle-password" @click="togglePasswordVisibility('current')">
                <el-icon><component :is="passwordVisible.current ? View : Hide" /></el-icon>
              </span>
            </div>
          </div>
          <div class="form-group">
            <label for="new-password">新密码</label>
            <div class="password-input">
              <input :type="passwordVisible.new ? 'text' : 'password'" id="new-password" v-model="passwordData.new_password1" />
              <span class="toggle-password" @click="togglePasswordVisibility('new')">
                <el-icon><component :is="passwordVisible.new ? View : Hide" /></el-icon>
              </span>
            </div>
          </div>
          <div class="form-group">
            <label for="confirm-password">确认新密码</label>
            <div class="password-input">
              <input :type="passwordVisible.confirm ? 'text' : 'password'" id="confirm-password" v-model="passwordData.new_password2" />
              <span class="toggle-password" @click="togglePasswordVisibility('confirm')">
                <el-icon><component :is="passwordVisible.confirm ? View : Hide" /></el-icon>
              </span>
            </div>
          </div>
          <button type="submit" class="save-btn">修改密码</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { View, Hide } from '@element-plus/icons-vue';
import { getProfile, updateProfile } from '@/services/api';
import apiClient from '@/services/api';

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

const passwordVisible = reactive({
  current: false,
  new: false,
  confirm: false,
});

const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
  passwordVisible[field] = !passwordVisible[field];
};

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
  }
});

const updateUserInfo = async () => {
  try {
    const response = await updateProfile(editableUser);
    user.value = response.data;
    alert('用户信息更新成功！');
  } catch (error) {
    console.error('更新用户信息失败:', error);
    alert('更新用户信息失败，请稍后重试。');
  }
};

const changePassword = async () => {
  if (passwordData.new_password1 !== passwordData.new_password2) {
    alert('新密码和确认密码不匹配！');
    return;
  }
  try {
    await apiClient.post('/auth/password/change/', passwordData);
    alert('密码修改成功！');
    Object.assign(passwordData, {
      old_password: '',
      new_password1: '',
      new_password2: '',
    });
  } catch (error) {
    console.error('修改密码失败:', error);
    alert('修改密码失败，请检查当前密码是否正确。');
  }
};
</script>

<style scoped>
.account-management {
  background-color: #fff;
  padding: 24px;
  border-radius: 8px;
}

.title {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 24px;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e8e8e8;
  margin-bottom: 24px;
}

.tab {
  padding: 12px 16px;
  cursor: pointer;
  font-size: 16px;
  color: #555;
  margin-bottom: -1px;
}

.tab.active {
  color: #1890ff;
  border-bottom: 2px solid #1890ff;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
}

.label {
  width: 100px;
  color: #888;
}

.value {
  color: #333;
  flex: 1;
}

.value input[type="text"],
.value input[type="email"] {
  width: 300px;
  padding: 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.value label {
  margin-right: 20px;
}

.save-btn {
  padding: 8px 24px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:hover {
  background-color: #40a9ff;
}

.password-management .form-group {
  margin-bottom: 20px;
}

.password-management label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
}

.password-management .password-input {
  position: relative;
  width: 300px;
}

.password-management input {
  width: 100%;
  padding: 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  padding-right: 30px; /* 为图标留出空间 */
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
}
</style>
