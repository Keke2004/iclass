<template>
  <div>
    <div class="chapter-header">
      <h2>课程章节</h2>
      <el-button v-if="isTeacher" type="primary" @click="openAddChapterDialog">添加新章节</el-button>
    </div>
    <el-collapse v-model="activeChapter" accordion>
      <el-collapse-item v-for="chapter in chapters" :key="chapter.id" :name="chapter.id">
        <template #title>
          <span class="chapter-title">{{ chapter.title }}</span>
          <div v-if="isTeacher" class="chapter-actions">
            <el-button type="text" @click.stop="openEditChapterDialog(chapter)">编辑</el-button>
            <el-button type="text" @click.stop="deleteChapter(chapter.id)">删除</el-button>
          </div>
        </template>
        <div class="chapter-content" v-html="chapter.content"></div>
      </el-collapse-item>
    </el-collapse>

    <!-- 添加/编辑章节对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEditing ? '编辑章节' : '添加新章节'" width="50%">
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
import { ElMessage, ElButton, ElCollapse, ElCollapseItem, ElDialog, ElForm, ElFormItem, ElInput } from 'element-plus';

interface Chapter {
  id: number;
  title: string;
  content: string;
  order: number;
}

const route = useRoute();
const courseId = route.params.id;

const chapters = ref<Chapter[]>([]);
const activeChapter = ref<number | null>(null);
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
.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.chapter-title {
  font-weight: bold;
}
.chapter-actions {
  margin-left: auto;
  padding-left: 20px;
}
.chapter-content {
  padding: 15px;
  line-height: 1.6;
}
</style>
