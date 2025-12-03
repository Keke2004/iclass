<template>
  <div>
    <h1>系统日志</h1>
    <el-table :data="logs" style="width: 100%">
      <el-table-column prop="timestamp" label="时间" :formatter="formatTimestamp"></el-table-column>
      <el-table-column prop="level" label="级别"></el-table-column>
      <el-table-column prop="message" label="信息"></el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const logs = ref([]);

const formatTimestamp = (row: any, column: any, cellValue: string) => {
  const date = new Date(cellValue);
  return date.toLocaleString();
};

const fetchLogs = async () => {
  try {
    const response = await api.get('/logs/');
    logs.value = response.data;
  } catch (error) {
    console.error('Failed to fetch logs:', error);
  }
};

onMounted(() => {
  fetchLogs();
});
</script>

<style scoped>
h1 {
  margin-bottom: 20px;
}
</style>
