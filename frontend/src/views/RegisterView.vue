<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <span>创建新账户</span>
        </div>
      </template>
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" size="large" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" size="large" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            size="large"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
            size="large"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="registerForm.role" placeholder="请选择角色" size="large" style="width: 100%">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" class="register-button" size="large">
            注 册
          </el-button>
        </el-form-item>
        <div class="login-link">
          <el-link type="primary" @click="$router.push('/login')">已有账户？立即登录</el-link>
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
import { register } from '../services/auth';

const router = useRouter();
const registerFormRef = ref<FormInstance>();

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'student' as 'student' | 'teacher' | 'admin',
});

const validatePass = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== registerForm.password) {
    callback(new Error("两次输入的密码不一致!"));
  } else {
    callback();
  }
};

const registerRules = reactive<FormRules>({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] },
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [{ validator: validatePass, trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
});

const handleRegister = async () => {
  if (!registerFormRef.value) return;
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          role: registerForm.role,
        });
        ElMessage.success('注册成功！');
        router.push('/login');
      } catch (error: any) {
        if (error.response && error.response.data) {
          const errors = Object.values(error.response.data).flat().join('\n');
          ElMessage.error(`注册失败: ${errors}`);
        } else {
          ElMessage.error('注册失败，请稍后重试');
        }
        console.error('Registration failed:', error);
      }
    } else {
      console.log('error submit!');
      return false;
    }
  });
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.register-card {
  width: 450px;
}

.card-header {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
}

.register-button {
  width: 100%;
}

.login-link {
  text-align: center;
  margin-top: 10px;
}
</style>
