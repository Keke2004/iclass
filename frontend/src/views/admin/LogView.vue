<template>
  <div class="logs-container">
    <h1>系统日志</h1>
    <div class="toolbar">
      <div class="filters">
        <el-input v-model="filters.message" placeholder="信息" @keyup.enter="handleSearch" clearable />
        <el-select v-model="filters.level" placeholder="级别" clearable>
          <el-option label="INFO" value="INFO" />
          <el-option label="WARNING" value="WARNING" />
          <el-option label="ERROR" value="ERROR" />
        </el-select>
      </div>
      <div class="actions">
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>
    <div class="table-wrapper">
      <el-table :data="logs" v-loading="loading" style="width: 100%" height="100%">
        <el-table-column prop="timestamp" label="时间" :formatter="formatTimestamp"></el-table-column>
        <el-table-column prop="level" label="级别"></el-table-column>
        <el-table-column prop="message" label="信息"></el-table-column>
      </el-table>
    </div>
    <el-pagination
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-sizes="[10, 20, 50, 100]"
      :page-size="pageSize"
      layout="total, sizes, prev, pager, next, jumper"
      :total="totalLogs">
    </el-pagination>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { ElMessage } from 'element-plus';

interface Log {
  id: number;
  timestamp: string;
  level: string;
  message: string;
}

const logs = ref<Log[]>([]);
const loading = ref(true);
const currentPage = ref(1);
const pageSize = ref(20);
const totalLogs = ref(0);

const initialFilters = {
  message: '',
  level: '',
};
const filters = ref({ ...initialFilters });

const formatTimestamp = (row: any, column: any, cellValue: string) => {
  const date = new Date(cellValue);
  return date.toLocaleString();
};

const fetchLogs = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString(),
    });
    if (filters.value.message) {
      params.append('message', filters.value.message);
    }
    if (filters.value.level) {
      params.append('level', filters.value.level);
    }
    const response = await api.get('/logs/', { params });
    logs.value = response.data.results;
    totalLogs.value = response.data.count;
  } catch (error) {
    console.error('Failed to fetch logs:', error);
    ElMessage.error('无法加载日志列表。');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchLogs();
};

const resetFilters = () => {
  filters.value = { ...initialFilters };
  currentPage.value = 1;
  fetchLogs();
};

const handleSizeChange = (val: number) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchLogs();
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  fetchLogs();
};

onMounted(() => {
  fetchLogs();
});
</script>

<style scoped>
.logs-container {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  height: calc(100vh - 120px);
  max-width: 1400px;
  margin: 0 auto;
  width: 95%;
}
.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
.filters {
  display: flex;
  gap: 10px;
  align-items: center;
}
.filters > .el-input {
  width: 200px;
}
.filters > .el-select {
  width: 120px;
}
.actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
  margin-right: 20px;
}
h1 {
  margin-bottom: 20px;
  flex-shrink: 0;
}
.toolbar {
  flex-shrink: 0;
}
.table-wrapper {
  flex-grow: 1;
  overflow: hidden;
}
.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
  flex-shrink: 0;
}
</style>
