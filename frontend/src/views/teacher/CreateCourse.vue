<template>
  <div class="create-course-container">
    <h1>创建课程</h1>
    <el-card class="form-card">
      <el-form :model="courseForm" :rules="rules" ref="courseFormRef" label-width="100px">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="courseForm.name" placeholder="请输入课程名称"></el-input>
        </el-form-item>
        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="courseForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入课程描述"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">立即创建</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage } from 'element-plus';
import apiClient from '../../services/api'; // Corrected path

// 表单引用
const courseFormRef = ref<FormInstance>();
const router = useRouter();

// 表单数据
const courseForm = reactive({
  name: '',
  description: '',
});

// 表单验证规则
const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入课程描述', trigger: 'blur' }],
});

// 提交表单
const submitForm = async () => {
  if (!courseFormRef.value) return;
  await courseFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await apiClient.post('/courses/', courseForm);
        ElMessage.success('课程创建成功！');
        router.push({ name: 'teacher-courses' });
      } catch (error) {
        console.error('创建课程失败:', error);
        ElMessage.error('课程创建失败，请稍后重试。');
      }
    } else {
      ElMessage.error('请检查表单输入是否正确。');
    }
  });
};

// 重置表单
const resetForm = () => {
  if (!courseFormRef.value) return;
  courseFormRef.value.resetFields();
};
</script>

<style scoped>
.create-course-container {
  padding: 20px;
}
.form-card {
  max-width: 600px;
  margin-top: 20px;
}
</style>
