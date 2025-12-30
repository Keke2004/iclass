<template>
  <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
    <el-form-item label="课程名称" prop="name">
      <el-input v-model="form.name" placeholder="请输入课程名称"></el-input>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, defineExpose } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import apiClient from '../services/api';

const formRef = ref<FormInstance>();
const form = reactive({
  name: '',
});

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
});

const submit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate();
  return apiClient.post('/courses/', form);
};

const reset = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }
};

defineExpose({
  submit,
  reset,
});
</script>
