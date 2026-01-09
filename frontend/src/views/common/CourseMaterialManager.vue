<template>
  <div class="course-material-manager">
    <div class="toolbar">
      <h1 class="page-title">课程资料</h1>
      <div class="controls">
        <div>
          <el-button type="primary" @click="handleUpload" v-if="isTeacher">上传文件</el-button>
          <el-button type="success" @click="downloadAll" v-if="selectedMaterials.length > 0">全部下载</el-button>
          <el-button type="danger" @click="deleteAll" v-if="selectedMaterials.length > 0 && isTeacher">全部删除</el-button>
        </div>
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件"
          class="search-input"
          clearable
          @clear="fetchMaterials"
          @keyup.enter="fetchMaterials"
        >
          <template #append>
            <el-button @click="fetchMaterials"><el-icon><Search /></el-icon></el-button>
          </template>
        </el-input>
      </div>
    </div>

    <el-table :data="materials" v-loading="loading" class="material-table" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="name" label="文件名" show-overflow-tooltip>
        <template #default="{ row }">
          <a href="#" class="material-name-link" @click.prevent="previewMaterial(row)">
            <span class="file-icon" :style="{ backgroundColor: getFileIcon(row.name).color }">
              {{ getFileIcon(row.name).icon }}
            </span>
            <span style="margin-left: 8px;">{{ row.name }}</span>
          </a>
        </template>
      </el-table-column>
      <el-table-column prop="size" label="大小" width="120">
        <template #default="{ row }">
          {{ formatSize(row.size) }}
        </template>
      </el-table-column>
      <el-table-column prop="uploaded_by.username" label="创建者" width="150" />
      <el-table-column prop="uploaded_at" label="创建日期" width="200">
        <template #default="{ row }">
          {{ new Date(row.uploaded_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button type="primary" link @click="downloadMaterial(row)">下载</el-button>
          <el-button type="danger" link @click="deleteMaterial(row)" v-if="isTeacher">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="uploadDialogVisible" title="上传文件">
      <el-upload
        drag
        :action="uploadActionUrl"
        :headers="uploadHeaders"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        multiple
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
      </el-upload>
    </el-dialog>

    <el-dialog v-model="previewDialogVisible" :title="previewTitle" width="85%" top="5vh" destroy-on-close>
      <iframe :src="previewUrl" width="100%" height="666vh" frameborder="0"></iframe>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage, ElMessageBox, ElTable, ElTableColumn, ElButton, ElInput, ElIcon, ElDialog, ElUpload } from 'element-plus';
import { Search, Document, UploadFilled } from '@element-plus/icons-vue';

interface Material {
  id: number;
  name: string;
  size: number;
  uploaded_at: string;
  uploaded_by: {
    username: string;
  };
  file: string;
}

const route = useRoute();
const courseId = route.params.id as string;

const materials = ref<Material[]>([]);
const loading = ref(true);
const searchQuery = ref('');
const uploadDialogVisible = ref(false);
const selectedMaterials = ref<Material[]>([]);

const previewDialogVisible = ref(false);
const previewUrl = ref('');
const previewTitle = ref('');

const isTeacher = computed(() => localStorage.getItem('user_role') === 'teacher');

const handleSelectionChange = (selection: Material[]) => {
  selectedMaterials.value = selection;
};

const fetchMaterials = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get(`/courses/${courseId}/materials/`, {
      params: { search: searchQuery.value }
    });
    materials.value = response.data;
  } catch (error) {
    ElMessage.error('获取课程资料失败');
  } finally {
    loading.value = false;
  }
};

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const handleUpload = () => {
  uploadDialogVisible.value = true;
};

const uploadActionUrl = computed(() => `${apiClient.defaults.baseURL}/courses/${courseId}/materials/`);
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`
}));

const handleUploadSuccess = () => {
  ElMessage.success('文件上传成功');
  uploadDialogVisible.value = false;
  fetchMaterials();
};

const handleUploadError = (error: any) => {
  const errorMessage = error.response?.data?.detail || '文件上传失败';
  ElMessage.error(errorMessage);
};

const downloadMaterial = async (material: Material) => {
  try {
    const response = await apiClient.get(`/courses/${courseId}/materials/${material.id}/download/`, {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', material.name);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    ElMessage.error('文件下载失败');
  }
};

const deleteMaterial = (material: Material) => {
  ElMessageBox.confirm(`确定要删除文件 "${material.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await apiClient.delete(`/courses/${courseId}/materials/${material.id}/`);
      ElMessage.success('文件删除成功');
      fetchMaterials();
    } catch (error) {
      ElMessage.error('文件删除失败');
    }
  });
};

const downloadAll = () => {
  if (selectedMaterials.value.length === 0) {
    ElMessage.warning('请至少选择一个文件');
    return;
  }
  selectedMaterials.value.forEach(material => {
    downloadMaterial(material);
  });
};

const deleteAll = () => {
  if (selectedMaterials.value.length === 0) {
    ElMessage.warning('请至少选择一个文件');
    return;
  }
  ElMessageBox.confirm(`确定要删除选中的 ${selectedMaterials.value.length} 个文件吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const ids = selectedMaterials.value.map(m => m.id);
      await apiClient.delete(`/courses/${courseId}/materials/bulk_delete/`, { data: { ids } });
      ElMessage.success('文件批量删除成功');
      fetchMaterials();
    } catch (error) {
      ElMessage.error('文件批量删除失败');
    }
  });
};

const previewMaterial = async (material: Material) => {
  previewTitle.value = material.name;
  const fileExtension = material.name.split('.').pop()?.toLowerCase() || '';

  const officeExtensions = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'];
  // All extensions that can be previewed by fetching the blob
  const previewableExtensions = ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'mp4', 'webm', 'ogg', 'mp3', 'wav', 'txt'];

  if (officeExtensions.includes(fileExtension)) {
    ElMessage.warning('该文件类型不支持在线预览，请下载后查看。');
    return;
  }

  if (previewableExtensions.includes(fileExtension)) {
    try {
      // Use the download endpoint which should provide the file with auth
      const response = await apiClient.get(`/courses/${courseId}/materials/${material.id}/download/`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      
      // Revoke the previous object URL to avoid memory leaks
      if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl.value);
      }
      
      previewUrl.value = URL.createObjectURL(blob);
      previewDialogVisible.value = true;
    } catch (error) {
      console.error('File preview error:', error);
      ElMessage.error('加载预览失败，请检查网络或文件是否损坏。');
    }
  } else {
    ElMessage.warning('该文件类型不支持预览，请下载后查看。');
  }
};

const getFileIcon = (name: string) => {
  const extension = name.split('.').pop()?.toLowerCase() || '';
  if (['ppt', 'pptx'].includes(extension)) {
    return { icon: 'P', color: '#d14424' };
  }
  if (['doc', 'docx'].includes(extension)) {
    return { icon: 'W', color: '#2a5699' };
  }
  if (['xls', 'xlsx'].includes(extension)) {
    return { icon: 'X', color: '#1e7145' };
  }
  if (['pdf'].includes(extension)) {
    return { icon: 'PDF', color: '#d11a2a' };
  }
  if (['zip', 'rar', '7z'].includes(extension)) {
    return { icon: 'ZIP', color: '#f9a825' };
  }
  if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg'].includes(extension)) {
    return { icon: 'IMG', color: '#4caf50' };
  }
  if (['mp4', 'webm', 'ogg', 'mp3', 'wav'].includes(extension)) {
    return { icon: 'VID', color: '#673ab7' };
  }
  if (['exe'].includes(extension)) {
    return { icon: 'EXE', color: '#616161' };
  }
  return { icon: 'DOC', color: '#909399' };
};

onMounted(fetchMaterials);
</script>

<style scoped>
.course-material-manager {
  padding: 20px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}
.controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.search-input {
  width: 300px;
}
.material-table {
  width: 100%;
}
.material-name-link {
  color: var(--el-color-primary);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}
.material-name-link:hover {
  color: var(--el-color-primary-light-3);
}
.file-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  color: white;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
  text-align: center;
  line-height: 28px;
}
</style>
