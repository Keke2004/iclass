<template>
  <div class="login-container">
    <div class="login-box">
      <div class="illustration-wrapper"></div>
      <div class="form-wrapper">
        <h1 class="title">智慧课堂互动平台</h1>
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-position="top"
          @submit.prevent="handleLogin"
          class="login-form"
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
          <div class="extra-links">
            <el-link type="primary" @click="$router.push('/forgot-password')">忘记密码？</el-link>
            <el-link type="primary" @click="$router.push('/register')">没有账户？立即注册</el-link>
          </div>
        </el-form>
      </div>
    </div>
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
        const { access, refresh } = await login(loginForm);
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        
        // 后端已经验证了角色，这里直接从登录表单中获取角色
        const role = loginForm.role;
        localStorage.setItem('user_role', role);
        localStorage.setItem('username', loginForm.username); // 保存用户名

        apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`;

        ElMessage.success('登录成功');

        switch (role) {
          case 'student':
            router.push('/student/courses');
            break;
          case 'teacher':
            router.push('/teacher/courses');
            break;
          case 'admin':
            router.push('/admin/users');
            break;
          default:
            router.push('/');
            break;
        }
      } catch (error: any) {
        if (error.response && error.response.data) {
          // 检查详细错误信息
          // Django REST Framework 的 ValidationError 可能是字符串数组
          let errorMessage = '登录失败';
          if (typeof error.response.data === 'object' && error.response.data !== null) {
            if (error.response.data.detail) {
              errorMessage = error.response.data.detail;
            } else if (Array.isArray(error.response.data) && error.response.data.length > 0) {
              errorMessage = error.response.data[0];
            } else if (error.response.data.non_field_errors) {
              errorMessage = error.response.data.non_field_errors[0];
            }
          }
          ElMessage.error(errorMessage);
        } else {
          // 通用网络错误或其它问题
          ElMessage.error('登录请求失败，请检查网络连接');
        }
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

.login-box {
  display: flex;
  width: 1080px; /* Adjusted width for better proportions */
  height: 480px; /* Make it flatter */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  overflow: hidden;
  background-color: #fff;
}

.illustration-wrapper {
  flex: 2.0; /* Make illustration even wider */
  background-image: url('/login.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #eef4ff;
}

.form-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px 30px;
}

.title {
  font-size: 26px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.login-form .el-form-item {
  margin-bottom: 20px;
}

/* Style for required fields */
.login-form .el-form-item.is-required .el-form-item__label::before {
  content: '*';
  color: #f56c6c;
  margin-right: 4px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
}

.role-radio-group {
  display: flex;
  justify-content: flex-start; /* Align to the left */
}

.extra-links {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  font-size: 14px;
}
</style>
