<template>
  <div class="announcement-manager">
    <div class="header">
      <h3>课程公告</h3>
      <el-button v-if="isTeacher" type="primary" @click="openAddDialog">发布新公告</el-button>
    </div>

    <el-timeline v-if="announcements.length > 0" class="announcement-list">
      <el-timeline-item
        v-for="announcement in announcements"
        :key="announcement.id"
        :timestamp="formatDate(announcement.created_at)"
        placement="top"
      >
        <el-card class="announcement-card">
          <h4>{{ announcement.title }}</h4>
          <p>{{ announcement.content }}</p>
          <div v-if="isTeacher" class="card-actions">
            <el-button type="primary" link @click="openEditDialog(announcement)">编辑</el-button>
            <el-button type="danger" link @click="deleteAnnouncement(announcement.id)">删除</el-button>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
    <el-empty v-else description="暂无公告"></el-empty>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="50%">
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
          <el-button @click="dialogVisible = false">取消</el-button>
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
import { ElMessage, ElButton, ElTimeline, ElTimelineItem, ElCard, ElEmpty, ElDialog, ElForm, ElFormItem, ElInput } from 'element-plus';

interface Announcement {
  id: number;
  title: string;
  content: string;
  created_at: string;
}

const route = useRoute();
const announcements = ref<Announcement[]>([]);
const dialogVisible = ref(false);
const isEditMode = ref(false);
const currentAnnouncement = ref<Partial<Announcement>>({});

const courseId = route.params.id;
const isTeacher = ref(localStorage.getItem('user_role') === 'teacher');

const dialogTitle = computed(() => (isEditMode.value ? '编辑公告' : '发布新公告'));

const fetchAnnouncements = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId}/announcements/`);
    announcements.value = response.data;
  } catch (error) {
    console.error('获取公告列表失败:', error);
    ElMessage.error('获取公告列表失败');
  }
};

const openAddDialog = () => {
  isEditMode.value = false;
  currentAnnouncement.value = { title: '', content: '' };
  dialogVisible.value = true;
};

const openEditDialog = (announcement: Announcement) => {
  isEditMode.value = true;
  currentAnnouncement.value = { ...announcement };
  dialogVisible.value = true;
};

const saveAnnouncement = async () => {
  try {
    if (isEditMode.value) {
      await apiClient.put(`/courses/${courseId}/announcements/${currentAnnouncement.value.id}/`, currentAnnouncement.value);
      ElMessage.success('公告更新成功');
    } else {
      await apiClient.post(`/courses/${courseId}/announcements/`, currentAnnouncement.value);
      ElMessage.success('公告发布成功');
    }
    dialogVisible.value = false;
    fetchAnnouncements();
  } catch (error) {
    console.error('保存公告失败:', error);
    ElMessage.error('保存公告失败');
  }
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
  const date = new Date(dateString);
  return date.toLocaleString();
};

onMounted(() => {
  fetchAnnouncements();
});
</script>

<style scoped>
.announcement-manager {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.announcement-list {
  margin-top: 20px;
}
.announcement-card h4 {
  margin-top: 0;
}
.card-actions {
  text-align: right;
  margin-top: 10px;
}
</style>
