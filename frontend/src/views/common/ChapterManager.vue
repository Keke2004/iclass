<template>
  <div class="chapter-manager-container">
    <div class="header">
      <h3>课程目录</h3>
      <el-button v-if="isTeacher" type="primary" @click="openAddChapterDialog(null)">添加章</el-button>
    </div>

    <el-tree
      v-if="chapters.length > 0"
      :data="chapters"
      :props="treeProps"
      node-key="id"
      default-expand-all
      :expand-on-click-node="false"
      @node-click="handleChapterSelect"
      class="chapter-tree"
    >
      <template #default="{ node, data }">
        <span class="custom-tree-node">
          <span>{{ node.label }}</span>
          <span v-if="isTeacher" class="node-actions">
            <el-button type="primary" link size="small" @click.stop="openAddChapterDialog(data)">添加节</el-button>
            <el-button type="primary" link size="small" @click.stop="openEditChapterDialog(data)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个章节吗？"
              @confirm.stop="deleteChapter(data.id)"
            >
              <template #reference>
                <el-button type="danger" link size="small" @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
          </span>
        </span>
      </template>
    </el-tree>
    <el-empty v-else description="暂无章节内容"></el-empty>

    <!-- 添加/编辑章节对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="60%">
      <el-form :model="chapterForm" label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="chapterForm.title"></el-input>
        </el-form-item>
        <el-form-item label="内容（可选）">
          <el-input type="textarea" :rows="5" v-model="chapterForm.content"></el-input>
        </el-form-item>
        <el-form-item label="视频文件（可选）">
          <el-upload
            :auto-upload="false"
            :on-change="handleVideoChange"
            :file-list="videoFileList"
            :limit="1"
          >
            <el-button type="primary">选择视频</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="PDF文件（可选）">
          <el-upload
            :auto-upload="false"
            :on-change="handlePdfChange"
            :file-list="pdfFileList"
            :limit="1"
          >
            <el-button type="primary">选择PDF</el-button>
          </el-upload>
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
import { ref, onMounted, computed, defineProps, defineEmits } from 'vue';
import apiClient from '../../services/api';
import { ElMessage, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElEmpty, ElPopconfirm, ElTree, ElUpload } from 'element-plus';
import type { UploadFile } from 'element-plus';

interface Chapter {
  id: number;
  title: string;
  content: string;
  parent?: number | null;
  children?: Chapter[];
  video?: string;
  pdf?: string;
}

const props = defineProps<{
  courseId: string;
}>();

const emit = defineEmits<{
  (e: 'select-chapter', chapter: Chapter): void;
}>();

const chapters = ref<Chapter[]>([]);
const dialogVisible = ref(false);
const isEditing = ref(false);
const chapterForm = ref<{
  id: number | null;
  title: string;
  content: string;
  parent: number | null;
  video: File | null;
  pdf: File | null;
}>({
  id: null,
  title: '',
  content: '',
  parent: null,
  video: null,
  pdf: null,
});

const videoFileList = ref<UploadFile[]>([]);
const pdfFileList = ref<UploadFile[]>([]);

const dialogTitle = computed(() => {
  if (!isEditing.value) {
    return chapterForm.value.parent ? '添加新节' : '添加新章';
  }
  return '编辑章节';
});

const userRole = localStorage.getItem('user_role');
const isTeacher = computed(() => userRole === 'teacher');

const treeProps = {
  children: 'children',
  label: 'title',
};

const fetchChapters = async () => {
  try {
    const response = await apiClient.get(`/courses/${props.courseId}/chapters/`);
    chapters.value = response.data;
  } catch (error) {
    console.error('获取章节列表失败:', error);
    ElMessage.error('无法加载章节列表。');
  }
};

const handleChapterSelect = (chapter: Chapter) => {
  emit('select-chapter', chapter);
};

const openAddChapterDialog = (parentChapter: Chapter | null) => {
  isEditing.value = false;
  chapterForm.value = {
    id: null,
    title: '',
    content: '',
    parent: parentChapter ? parentChapter.id : null,
    video: null,
    pdf: null,
  };
  videoFileList.value = [];
  pdfFileList.value = [];
  dialogVisible.value = true;
};

const openEditChapterDialog = (chapter: Chapter) => {
  isEditing.value = true;
  chapterForm.value = {
    id: chapter.id,
    title: chapter.title,
    content: chapter.content,
    parent: chapter.parent || null,
    video: null, // 编辑时不直接显示旧文件，需要重新上传
    pdf: null,
  };
  videoFileList.value = [];
  pdfFileList.value = [];
  dialogVisible.value = true;
};

const handleVideoChange = (file: UploadFile) => {
  chapterForm.value.video = file.raw as File;
};

const handlePdfChange = (file: UploadFile) => {
  chapterForm.value.pdf = file.raw as File;
};

const saveChapter = async () => {
  if (!chapterForm.value.title.trim()) {
    ElMessage.error('请输入章节标题。');
    return;
  }

  const formData = new FormData();
  formData.append('title', chapterForm.value.title);
  formData.append('content', chapterForm.value.content);
  if (chapterForm.value.parent) {
    formData.append('parent', String(chapterForm.value.parent));
  }
  if (chapterForm.value.video) {
    formData.append('video', chapterForm.value.video);
  }
  if (chapterForm.value.pdf) {
    formData.append('pdf', chapterForm.value.pdf);
  }

  try {
    if (isEditing.value && chapterForm.value.id) {
      await apiClient.patch(`/courses/${props.courseId}/chapters/${chapterForm.value.id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      ElMessage.success('章节更新成功！');
    } else {
      await apiClient.post(`/courses/${props.courseId}/chapters/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
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
    await apiClient.delete(`/courses/${props.courseId}/chapters/${chapterId}/`);
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
  padding: 16px;
  background-color: #fff;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 8px;
}

.chapter-tree {
  flex-grow: 1;
  overflow-y: auto;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.node-actions {
  display: none;
}

.el-tree-node__content:hover .node-actions {
  display: inline-block;
}
</style>
