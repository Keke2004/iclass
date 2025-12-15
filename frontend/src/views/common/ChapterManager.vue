<template>
  <div class="chapter-manager-container">
    <div class="header">
      <div class="header-left">
        <h3>课程目录</h3>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchQuery"
          placeholder="搜索章节内容"
          clearable
          class="search-input"
        />
        <el-button v-if="isTeacher" type="primary" @click="openAddChapterDialog(null)">添加章</el-button>
      </div>
    </div>

    <el-collapse v-if="filteredChapters.length > 0" ref="collapseRef" class="chapter-collapse">
      <el-collapse-item v-for="(chapter, index) in filteredChapters" :key="chapter.id" :name="chapter.id.toString()">
        <template #title>
          <div class="chapter-header-content">
            <span class="chapter-title" v-html="highlightText(`第 ${chapter.originalIndex + 1} 章 ${chapter.title}`, searchQuery)"></span>
            <span v-if="isTeacher" class="node-actions">
              <el-button type="primary" link size="small" @click.stop="openAddChapterDialog(chapter)">添加节</el-button>
              <el-button type="primary" link size="small" @click.stop="openEditChapterDialog(chapter)">编辑</el-button>
              <el-popconfirm title="确定要删除吗？如果删除章，其下的所有节也会被删除。" @confirm.stop="deleteChapter(chapter.id)">
                <template #reference>
                  <el-button type="danger" link size="small" @click.stop>删除</el-button>
                </template>
              </el-popconfirm>
            </span>
          </div>
        </template>
        <ul class="section-list">
          <li v-for="(section, secIndex) in chapter.children" :key="section.id" class="section-item" @click="handleSectionClick(section)">
            <div class="section-content">
              <el-icon class="completion-icon"><CircleCheckFilled /></el-icon>
              <span class="section-title" v-html="highlightText(`${chapter.originalIndex + 1}.${secIndex + 1} ${section.title}`, searchQuery)"></span>
            </div>
            <div v-if="isTeacher" class="node-actions">
              <el-button type="primary" link size="small" @click.stop="openEditChapterDialog(section)">编辑</el-button>
              <el-popconfirm title="确定要删除吗？" @confirm.stop="deleteChapter(section.id)">
                <template #reference>
                  <el-button type="danger" link size="small" @click.stop>删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </li>
        </ul>
      </el-collapse-item>
    </el-collapse>
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
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import type { CollapseInstance } from 'element-plus';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage, ElButton, ElDialog, ElForm, ElFormItem, ElInput, ElEmpty, ElPopconfirm, ElCollapse, ElCollapseItem, ElIcon } from 'element-plus';
import { CircleCheckFilled } from '@element-plus/icons-vue';

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
const searchQuery = ref('');
const collapseRef = ref<CollapseInstance>();
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

const highlightText = (text: string, query: string) => {
  if (!query) {
    return text;
  }
  const regex = new RegExp(`(${query})`, 'gi');
  return text.replace(regex, '<span class="highlight">$1</span>');
};

const filteredChapters = computed(() => {
  const query = searchQuery.value.toLowerCase();
  if (!query) {
    return chapters.value.map((chapter, index) => ({ ...chapter, originalIndex: index }));
  }

  const result: any[] = [];
  chapters.value.forEach((chapter, index) => {
    const chapterTitleMatch = chapter.title.toLowerCase().includes(query);
    
    const matchingSections = chapter.children?.filter(section => 
      section.title.toLowerCase().includes(query)
    ) || [];

    if (chapterTitleMatch || matchingSections.length > 0) {
      result.push({
        ...chapter,
        originalIndex: index,
        // If chapter title matches, show all children; otherwise, show only matching children.
        children: chapterTitleMatch ? chapter.children : matchingSections,
      });
    }
  });
  return result;
});

watch(searchQuery, () => {
  nextTick(() => {
    if (collapseRef.value) {
      let idsToExpand: string[];
      if (searchQuery.value) {
        idsToExpand = filteredChapters.value.map(c => c.id.toString());
      } else {
        idsToExpand = chapters.value.map(c => c.id.toString());
      }
      // 直接操作组件实例的内部状态
      collapseRef.value.setActiveNames(idsToExpand);
    }
  });
});

const fetchChapters = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId.value}/chapters/`);
    chapters.value = response.data;
    // 默认展开所有章
    nextTick(() => {
      if (collapseRef.value && chapters.value.length > 0) {
        collapseRef.value.setActiveNames(chapters.value.map(c => c.id.toString()));
      }
    });
  } catch (error) {
    console.error('获取章节列表失败:', error);
    ElMessage.error('无法加载章节列表。');
  }
};

const handleSectionClick = (section: Chapter) => {
  router.push({ name: 'section-detail', params: { id: courseId.value, sectionId: section.id } });
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
  padding: 24px;
  background-color: #f7f8fa; /* 参考背景色 */
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  width: 240px;
}

.chapter-collapse {
  border: none;
}

:deep(.el-collapse-item__header) {
  background-color: #fff;
  border-radius: 8px;
  margin-bottom: 10px;
  padding: 0 20px;
  height: 60px;
  font-size: 16px;
  font-weight: 500;
  border: 1px solid #e8e8e8;
  transition: all 0.3s;
}

:deep(.el-collapse-item__header:hover) {
  border-color: #409eff;
}

:deep(.el-collapse-item__wrap) {
  background-color: transparent;
  border: none;
  padding-left: 20px;
}

:deep(.el-collapse-item__content) {
  padding-bottom: 0;
}

.chapter-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.chapter-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.section-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.section-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  margin-bottom: 8px;
  background-color: #fff;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.section-item:hover {
  background-color: #f0f5ff;
}

.section-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.completion-icon {
  color: #67c23a; /* 绿色对勾 */
  font-size: 18px;
}

.section-title {
  font-size: 14px;
  color: #333;
}

.node-actions {
  display: none;
  gap: 16px; /* 增加按钮间距 */
  flex-shrink: 0; /* 防止操作按钮被压缩 */
}

:deep(.el-collapse-item__header):hover .node-actions,
.section-item:hover .node-actions {
  display: flex;
  align-items: center;
}

.node-actions .el-button {
  font-size: 14px; /* 统一字体大小 */
}

:deep(.highlight) {
  color: #409eff;
  font-weight: bold;
}
</style>
