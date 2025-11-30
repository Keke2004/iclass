<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>智慧课堂互动平台</span>
        </div>
      </template>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" size="large" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            size="large"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="loginForm.role" class="role-radio-group">
            <el-radio-button label="student">学生</el-radio-button>
            <el-radio-button label="teacher">教师</el-radio-button>
            <el-radio-button label="admin">管理员</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" class="login-button" size="large">
            登 录
          </el-button>
        </el-form-item>
        <div class="register-link">
          <el-link type="primary" @click="$router.push('/register')">没有账户？立即注册</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage } from 'element-plus';
import { login, getUserProfile } from '../services/auth';
import apiClient from '../services/api';

const router = useRouter();
const loginFormRef = ref<FormInstance>();

const loginForm = reactive({
  username: '',
  password: '',
  role: 'student',
});

const loginRules = reactive<FormRules>({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
});

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 1. 获取token
        const { access, refresh } = await login(loginForm);
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);

        // 2. 设置api客户端的header，以便后续请求能通过认证
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`;

        // 3. 获取用户真实角色信息
        const userProfile = await getUserProfile();
        const realRole = userProfile.role;

        // 4. 比较选择的角色和真实角色
        if (loginForm.role === realRole) {
          localStorage.setItem('user_role', realRole);
          localStorage.setItem('username', userProfile.username || '用户'); // 保存用户名
          ElMessage.success('登录成功');
          // 根据角色跳转
          switch (realRole) {
            case 'student':
              router.push('/student/dashboard');
              break;
            case 'teacher':
              router.push('/teacher/dashboard');
              break;
            case 'admin':
              router.push('/admin/dashboard');
              break;
            default:
              router.push('/');
              break;
          }
        } else {
          // 角色不匹配，清除token并提示错误
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          ElMessage.error(`角色选择错误，该用户不是'${loginForm.role}'`);
        }
      } catch (error) {
        ElMessage.error('用户名或密码错误');
        console.error('Login failed:', error);
      }
    } else {
      console.log('error submit!');
      return false;
    }
  });
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
}

.login-button {
  width: 100%;
}

.role-radio-group {
  width: 100%;
  justify-content: space-around;
}

.register-link {
  text-align: center;
  margin-top: 10px;
}
</style>
