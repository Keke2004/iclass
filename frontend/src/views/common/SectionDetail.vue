<template>
  <div class="section-detail-container">
    <!-- 左侧内容区 -->
    <div class="content-area">
      <div v-if="loading" class="loading-state">加载中...</div>
      <div v-else-if="error" class="error-state">{{ error }}</div>
      <div v-else-if="section">
        <!-- 显示模式 -->
        <div v-if="!isEditing">
          <div class="header">
            <h2>{{ section.title }}</h2>
            <el-button v-if="isTeacher" type="primary" @click="isEditing = true">编辑本节</el-button>
          </div>
          <div v-if="section.content" v-html="section.content" class="rich-text-content"></div>
          <div v-if="section.video" class="media-container">
            <h4>视频</h4>
            <video controls :src="section.video" class="video-player"></video>
          </div>
          <div v-if="section.pdf" class="media-container">
            <h4>PDF 文档</h4>
            <embed :src="section.pdf" type="application/pdf" class="pdf-viewer" />
          </div>
        </div>
        <!-- 编辑模式 -->
        <div v-else>
          <div class="header">
            <h2>正在编辑: {{ section.title }}</h2>
          </div>
          <el-form :model="editForm" label-position="top">
            <el-form-item label="标题">
              <el-input v-model="editForm.title" />
            </el-form-item>
            <el-form-item label="内容">
              <el-input type="textarea" :rows="10" v-model="editForm.content" />
            </el-form-item>
            <el-form-item label="替换视频 (可选)">
              <el-upload :auto-upload="false" :on-change="handleVideoChange" :limit="1">
                <el-button type="primary">选择新视频</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item label="替换PDF (可选)">
              <el-upload :auto-upload="false" :on-change="handlePdfChange" :limit="1">
                <el-button type="primary">选择新PDF</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveChanges">保存</el-button>
              <el-button @click="isEditing = false">取消</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 右侧导航栏 -->
    <div class="navigation-sidebar">
      <ChapterNavigator :course-id="courseId" :active-section-id="sectionId" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../../services/api';
import ChapterNavigator from './ChapterNavigator.vue';
import { ElMessage, ElButton, ElForm, ElFormItem, ElInput, ElUpload } from 'element-plus';
import type { UploadFile } from 'element-plus';

interface Section {
  id: number;
  title: string;
  content: string;
  video?: string;
  pdf?: string;
}

const route = useRoute();
const courseId = computed(() => route.params.id as string);
const sectionId = computed(() => Number(route.params.sectionId));

const section = ref<Section | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const isEditing = ref(false);

const editForm = ref<{
  title: string;
  content: string;
  video: File | null;
  pdf: File | null;
}>({
  title: '',
  content: '',
  video: null,
  pdf: null,
});

const userRole = localStorage.getItem('user_role');
const isTeacher = computed(() => userRole === 'teacher');

const fetchSectionDetail = async (id: number) => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get(`/courses/${courseId.value}/chapters/${id}/`);
    section.value = response.data;
    // 初始化编辑表单
    editForm.value = {
      title: response.data.title,
      content: response.data.content,
      video: null,
      pdf: null,
    };
  } catch (err) {
    console.error('获取节详情失败:', err);
    error.value = '无法加载内容。';
  } finally {
    loading.value = false;
  }
};

const handleVideoChange = (file: UploadFile) => {
  editForm.value.video = file.raw as File;
};

const handlePdfChange = (file: UploadFile) => {
  editForm.value.pdf = file.raw as File;
};

const saveChanges = async () => {
  if (!section.value) return;

  const formData = new FormData();
  formData.append('title', editForm.value.title);
  formData.append('content', editForm.value.content);
  if (editForm.value.video) {
    formData.append('video', editForm.value.video);
  }
  if (editForm.value.pdf) {
    formData.append('pdf', editForm.value.pdf);
  }

  try {
    await apiClient.patch(`/courses/${courseId.value}/chapters/${section.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    ElMessage.success('更新成功！');
    isEditing.value = false;
    await fetchSectionDetail(sectionId.value); // 重新加载数据
  } catch (err) {
    console.error('保存失败:', err);
    ElMessage.error('保存失败。');
  }
};

watch(sectionId, (newId) => {
  if (newId) {
    fetchSectionDetail(newId);
  }
}, { immediate: true });

onMounted(() => {
  if (!sectionId.value) {
    error.value = "未指定有效的节ID。";
    loading.value = false;
  }
});
</script>

<style scoped>
.section-detail-container {
  display: flex;
  height: calc(100vh - 150px); /* 减去顶部和底部导航的高度 */
  overflow: hidden; /* 防止整个容器滚动 */
}
.content-area {
  flex-grow: 1;
  padding: 24px;
  overflow-y: auto; /* 使内容区可滚动 */
}
.navigation-sidebar {
  width: 300px;
  min-width: 300px;
  border-left: 1px solid #e0e0e0;
  height: 100%; /* 保持高度以适应flex容器 */
  overflow-y: auto; /* 导航器内部也可以滚动 */
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.rich-text-content {
  line-height: 1.8;
}
.media-container {
  margin-top: 30px;
}
.video-player, .pdf-viewer {
  width: 100%;
  max-width: 800px;
  border-radius: 8px;
}
.pdf-viewer {
  height: 800px;
}
</style>
