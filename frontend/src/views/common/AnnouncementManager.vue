<template>
  <div class="announcement-manager">
    <div class="header">
      <h1 class="page-title">课程公告</h1>
      <el-button v-if="isTeacher" type="primary" @click="openAddDialog">发布新公告</el-button>
    </div>

    <div class="scroll-container">
      <div v-if="announcements.length > 0" class="announcement-list">
        <el-card v-for="announcement in announcements" :key="announcement.id" class="announcement-card" @click="toggleExpand(announcement.id)">
          <template #header>
            <div class="card-header">
              <span>{{ announcement.title }}</span>
              <span class="timestamp">{{ formatDate(announcement.created_at) }}</span>
            </div>
          </template>
          <div class="content-display">
            <p v-if="expandedAnnouncementId === announcement.id" class="full-content">{{ announcement.content }}</p>
            <p v-else class="content-preview">{{ truncate(announcement.content, 100) }}</p>
          </div>
          <div v-if="isTeacher" class="card-footer">
            <div class="card-actions">
              <el-button type="primary" link @click.stop="openEditDialog(announcement)">编辑</el-button>
              <el-button type="danger" link @click.stop="confirmDelete(announcement.id)">删除</el-button>
            </div>
          </div>
        </el-card>
      </div>
      <el-empty v-else description="暂无公告"></el-empty>
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="editDialogVisible" :title="dialogTitle" width="50%">
      <el-form :model="currentAnnouncement" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="currentAnnouncement.title"></el-input>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="currentAnnouncement.content" type="textarea" :rows="5"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAnnouncement">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage, ElMessageBox, ElButton, ElCard, ElEmpty, ElDialog, ElForm, ElFormItem, ElInput } from 'element-plus';

interface Announcement {
  id: number;
  title: string;
  content: string;
  created_at: string;
}

const route = useRoute();
const announcements = ref<Announcement[]>([]);
const editDialogVisible = ref(false);
const isEditMode = ref(false);
const currentAnnouncement = ref<Partial<Announcement>>({});
const expandedAnnouncementId = ref<number | null>(null);

const courseId = route.params.id;
const isTeacher = ref(localStorage.getItem('user_role') === 'teacher');

const dialogTitle = computed(() => (isEditMode.value ? '编辑公告' : '发布新公告'));

const fetchAnnouncements = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId}/announcements/`);
    announcements.value = response.data.sort((a: Announcement, b: Announcement) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  } catch (error) {
    console.error('获取公告列表失败:', error);
    ElMessage.error('获取公告列表失败');
  }
};

const openAddDialog = () => {
  isEditMode.value = false;
  currentAnnouncement.value = { title: '', content: '' };
  editDialogVisible.value = true;
};

const openEditDialog = (announcement: Announcement) => {
  isEditMode.value = true;
  currentAnnouncement.value = { ...announcement };
  editDialogVisible.value = true;
};

const toggleExpand = (id: number) => {
  if (expandedAnnouncementId.value === id) {
    expandedAnnouncementId.value = null;
  } else {
    expandedAnnouncementId.value = id;
  }
};

const saveAnnouncement = async () => {
  if (!currentAnnouncement.value.title || !currentAnnouncement.value.content) {
    ElMessage.warning('标题和内容不能为空');
    return;
  }
  try {
    if (isEditMode.value) {
      await apiClient.put(`/courses/${courseId}/announcements/${currentAnnouncement.value.id}/`, currentAnnouncement.value);
      ElMessage.success('公告更新成功');
    } else {
      await apiClient.post(`/courses/${courseId}/announcements/`, currentAnnouncement.value);
      ElMessage.success('公告发布成功');
    }
    editDialogVisible.value = false;
    fetchAnnouncements();
  } catch (error) {
    console.error('保存公告失败:', error);
    ElMessage.error('保存公告失败');
  }
};

const confirmDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除这条公告吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    deleteAnnouncement(id);
  }).catch(() => {
    // a
  });
};

const deleteAnnouncement = async (id: number) => {
  try {
    await apiClient.delete(`/courses/${courseId}/announcements/${id}/`);
    ElMessage.success('公告删除成功');
    fetchAnnouncements();
  } catch (error) {
    console.error('删除公告失败:', error);
    ElMessage.error('删除公告失败');
  }
};

const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
};

const truncate = (text: string, length: number) => {
  if (text.length <= length) {
    return text;
  }
  return text.substring(0, length) + '...';
};

onMounted(() => {
  fetchAnnouncements();
});
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: bold;
}
.announcement-manager {
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
  box-sizing: border-box;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}
.scroll-container {
  flex-grow: 1;
  overflow-y: auto;
}
.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.announcement-card {
  border-radius: 8px;
  cursor: pointer;
  transition: box-shadow 0.3s;
}
.announcement-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
.timestamp {
  font-size: 0.85em;
  color: #909399;
}
.content-display p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}
.card-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}
.card-actions {
  display: flex;
  gap: 10px;
}
</style>
