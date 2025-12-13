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
      class="chapter-tree"
    >
      <template #default="{ node, data }">
        <span class="custom-tree-node" @click="handleNodeClick(node, data)">
          <span>{{ node.label }}</span>
          <span v-if="isTeacher" class="node-actions">
            <el-button v-if="!data.parent" type="primary" link size="small" @click.stop="openAddChapterDialog(data)">添加节</el-button>
            <el-button type="primary" link size="small" @click.stop="openEditChapterDialog(data)">编辑标题</el-button>
            <el-popconfirm
              title="确定要删除吗？如果删除章，其下的所有节也会被删除。"
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

    <!-- 添加/编辑标题对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="chapterForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="chapterForm.title"></el-input>
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
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElEmpty, ElPopconfirm, ElTree } from 'element-plus';

interface Chapter {
  id: number;
  title: string;
  parent?: number | null;
  children?: Chapter[];
}

const route = useRoute();
const router = useRouter();
const courseId = computed(() => route.params.id as string);

const chapters = ref<Chapter[]>([]);
const dialogVisible = ref(false);
const isEditing = ref(false);
const chapterForm = ref<{
  id: number | null;
  title: string;
  parent: number | null;
}>({
  id: null,
  title: '',
  parent: null,
});

const dialogTitle = computed(() => {
  if (!isEditing.value) {
    return chapterForm.value.parent ? '添加新节' : '添加新章';
  }
  return '编辑标题';
});

const userRole = localStorage.getItem('user_role');
const isTeacher = computed(() => userRole === 'teacher');

const treeProps = {
  children: 'children',
  label: 'title',
};

const fetchChapters = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId.value}/chapters/`);
    chapters.value = response.data;
  } catch (error) {
    console.error('获取章节列表失败:', error);
    ElMessage.error('无法加载章节列表。');
  }
};

const handleNodeClick = (node: any, data: Chapter) => {
  // 如果是节 (有 parent)，则导航到详情页
  if (data.parent) {
    router.push({ name: 'section-detail', params: { id: courseId.value, sectionId: data.id } });
  }
};

const openAddChapterDialog = (parentChapter: Chapter | null) => {
  isEditing.value = false;
  chapterForm.value = {
    id: null,
    title: '',
    parent: parentChapter ? parentChapter.id : null,
  };
  dialogVisible.value = true;
};

const openEditChapterDialog = (chapter: Chapter) => {
  isEditing.value = true;
  chapterForm.value = {
    id: chapter.id,
    title: chapter.title,
    parent: chapter.parent || null,
  };
  dialogVisible.value = true;
};

const saveChapter = async () => {
  if (!chapterForm.value.title.trim()) {
    ElMessage.error('请输入标题。');
    return;
  }

  const payload: { title: string; parent?: number } = {
    title: chapterForm.value.title,
  };
  if (chapterForm.value.parent) {
    payload.parent = chapterForm.value.parent;
  }

  try {
    if (isEditing.value && chapterForm.value.id) {
      await apiClient.patch(`/courses/${courseId.value}/chapters/${chapterForm.value.id}/`, payload);
      ElMessage.success('更新成功！');
    } else {
      await apiClient.post(`/courses/${courseId.value}/chapters/`, payload);
      ElMessage.success('添加成功！');
    }
    dialogVisible.value = false;
    await fetchChapters();
  } catch (error: any) {
    console.error('保存失败:', error);
    const errorMsg = error.response?.data?.detail || '保存失败。';
    ElMessage.error(errorMsg);
  }
};

const deleteChapter = async (chapterId: number) => {
  try {
    await apiClient.delete(`/courses/${courseId.value}/chapters/${chapterId}/`);
    ElMessage.success('删除成功！');
    await fetchChapters();
  } catch (error) {
    console.error('删除失败:', error);
    ElMessage.error('删除失败。');
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
  cursor: pointer;
}

.node-actions {
  display: none;
  cursor: default;
}

.el-tree-node__content:hover .node-actions {
  display: inline-block;
}
</style>
