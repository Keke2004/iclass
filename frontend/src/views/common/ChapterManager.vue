<template>
  <div class="chapter-manager-container">
    <div class="header">
      <h2>课程章节</h2>
      <el-button v-if="isTeacher" type="primary" @click="openAddChapterDialog">添加新章节</el-button>
    </div>

    <div v-if="chapters.length > 0" class="chapter-list">
      <div v-for="(chapter, index) in chapters" :key="chapter.id" class="chapter-item">
        <div class="chapter-item-header" @click="toggleChapter(chapter.id)">
          <div class="chapter-number" :class="{ active: activeChapterId === chapter.id }">{{ index + 1 }}</div>
          <div class="chapter-title">{{ chapter.title }}</div>
          <div v-if="isTeacher" class="chapter-actions">
            <el-button type="primary" link @click.stop="openEditChapterDialog(chapter)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个章节吗？"
              confirm-button-text="确认"
              cancel-button-text="取消"
              @confirm="deleteChapter(chapter.id)"
            >
              <template #reference>
                <el-button type="danger" link @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
        <div v-if="activeChapterId === chapter.id" class="chapter-content" v-html="chapter.content"></div>
      </div>
    </div>
    <el-empty v-else description="暂无章节内容"></el-empty>

    <!-- 添加/编辑章节对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEditing ? '编辑章节' : '添加新章节'" width="60%">
      <el-form :model="chapterForm" label-width="80px">
        <el-form-item label="章节标题">
          <el-input v-model="chapterForm.title"></el-input>
        </el-form-item>
        <el-form-item label="章节内容">
          <el-input type="textarea" :rows="10" v-model="chapterForm.content"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveChapter">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElEmpty, ElPopconfirm } from 'element-plus';

interface Chapter {
  id: number;
  title: string;
  content: string;
}

const route = useRoute();
const courseId = route.params.id;

const chapters = ref<Chapter[]>([]);
const activeChapterId = ref<number | null>(null);
const dialogVisible = ref(false);
const isEditing = ref(false);
const chapterForm = ref({
  id: null as number | null,
  title: '',
  content: ''
});

const userRole = localStorage.getItem('user_role');
const isTeacher = computed(() => userRole === 'teacher');

const fetchChapters = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId}/chapters/`);
    chapters.value = response.data;
  } catch (error) {
    console.error('获取章节列表失败:', error);
    ElMessage.error('无法加载章节列表。');
  }
};

const toggleChapter = (chapterId: number) => {
  if (activeChapterId.value === chapterId) {
    activeChapterId.value = null; // Collapse if already active
  } else {
    activeChapterId.value = chapterId; // Expand new one
  }
};

const openAddChapterDialog = () => {
  isEditing.value = false;
  chapterForm.value = { id: null, title: '', content: '' };
  dialogVisible.value = true;
};

const openEditChapterDialog = (chapter: Chapter) => {
  isEditing.value = true;
  chapterForm.value = { ...chapter };
  dialogVisible.value = true;
};

const saveChapter = async () => {
  try {
    if (isEditing.value && chapterForm.value.id) {
      await apiClient.put(`/courses/${courseId}/chapters/${chapterForm.value.id}/`, chapterForm.value);
      ElMessage.success('章节更新成功！');
    } else {
      await apiClient.post(`/courses/${courseId}/chapters/`, chapterForm.value);
      ElMessage.success('章节添加成功！');
    }
    dialogVisible.value = false;
    await fetchChapters();
  } catch (error) {
    console.error('保存章节失败:', error);
    ElMessage.error('保存章节失败。');
  }
};

const deleteChapter = async (chapterId: number) => {
  try {
    await apiClient.delete(`/courses/${courseId}/chapters/${chapterId}/`);
    ElMessage.success('章节删除成功！');
    await fetchChapters();
  } catch (error) {
    console.error('删除章节失败:', error);
    ElMessage.error('删除章节失败。');
  }
};

onMounted(() => {
  fetchChapters();
});
</script>

<style scoped>
.chapter-manager-container {
  padding: 24px;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chapter-list {
  position: relative;
}

.chapter-item {
  background-color: #fff;
  border-radius: 8px;
  margin-bottom: 16px;
  transition: box-shadow 0.3s;
}

.chapter-item:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.chapter-item-header {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  cursor: pointer;
}

.chapter-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #e0e0e0;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 16px;
  flex-shrink: 0;
  transition: background-color 0.3s;
}

.chapter-number.active {
    background-color: #409eff;
}

.chapter-title {
  flex-grow: 1;
  font-size: 16px;
  font-weight: 500;
}

.chapter-actions {
  margin-left: auto;
  display: flex;
  gap: 16px;
}

.chapter-content {
  padding: 0 24px 16px 72px; /* 24px + 32px + 16px */
  color: #606266;
  line-height: 1.8;
  border-top: 1px solid #ebeef5;
  margin-top: -1px;
  padding-top: 16px;
}

/* Vertical line */
.chapter-list::before {
  content: '';
  position: absolute;
  left: 40px; /* (24px padding + 16px) */
  top: 16px;
  bottom: 16px;
  width: 2px;
  background-color: #e0e0e0;
  transform: translateX(-50%);
}
</style>
