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
import { login } from '../services/auth';

const router = useRouter();
const loginFormRef = ref<FormInstance>();

const loginForm = reactive({
  username: '',
  password: '',
});

const loginRules = reactive<FormRules>({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
});

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const { access, refresh } = await login(loginForm);
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        ElMessage.success('登录成功');
        // 这里可以根据用户角色跳转到不同页面
        router.push('/');
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

.register-link {
  text-align: center;
  margin-top: 10px;
}
</style>
