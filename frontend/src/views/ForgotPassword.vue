<template>
  <div class="forgot-password-container">
    <el-card class="forgot-password-card">
      <template #header>
        <div class="card-header">
          <span>重置密码</span>
        </div>
      </template>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入您的用户名" size="large" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password1">
          <el-input v-model="form.new_password1" type="password" placeholder="请输入新密码" size="large" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="new_password2">
          <el-input v-model="form.new_password2" type="password" placeholder="请再次输入新密码" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" class="submit-button" size="large" :loading="loading">
            重置密码
          </el-button>
        </el-form-item>
        <div class="back-to-login">
          <el-link type="primary" @click="$router.push('/login')">返回登录</el-link>
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
import { directPasswordReset } from '../services/auth';

const router = useRouter();
const formRef = ref<FormInstance>();
const loading = ref(false);

const form = reactive({
  username: '',
  new_password1: '',
  new_password2: '',
});

const validatePass = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== form.new_password1) {
    callback(new Error("两次输入的新密码不一致"));
  } else {
    callback();
  }
};

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  new_password1: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  new_password2: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validatePass, trigger: 'blur' }
  ],
});

const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        await directPasswordReset(form);
        ElMessage.success('密码已成功重置，请使用新密码登录。');
        router.push('/login');
      } catch (error: any) {
        if (error.response && error.response.data) {
          const errors = error.response.data;
          if (errors.username) {
            ElMessage.error(errors.username[0]);
          } else if (errors.detail) {
            ElMessage.error(errors.detail);
          } else {
            ElMessage.error('密码重置失败，请稍后重试。');
          }
        } else {
          ElMessage.error('密码重置失败，请稍后重试。');
        }
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.forgot-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.forgot-password-card {
  width: 400px;
}

.card-header {
  text-align: center;
  font-size: 24px;
  font-weight: bold;
}

.submit-button {
  width: 100%;
}

.back-to-login {
  text-align: center;
  margin-top: 10px;
}
</style>
