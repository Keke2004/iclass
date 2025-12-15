<template>
  <div class="chapter-navigator">
    <h4 class="navigator-title">课程大纲</h4>
    <el-collapse v-if="chapters.length > 0" v-model="activeCollapse" class="chapter-collapse">
      <el-collapse-item v-for="(chapter, index) in chapters" :key="chapter.id" :name="chapter.id">
        <template #title>
          <span class="chapter-title">{{ `第 ${index + 1} 章 ${chapter.title}` }}</span>
        </template>
        <ul class="section-list">
          <li 
            v-for="(section, secIndex) in chapter.children" 
            :key="section.id" 
            class="section-item" 
            :class="{ 'is-active': section.id === activeSectionId }"
            @click="handleSectionClick(section)"
          >
            <el-icon class="completion-icon"><CircleCheckFilled /></el-icon>
            <span class="section-title">{{ `${index + 1}.${secIndex + 1} ${section.title}` }}</span>
            <el-icon class="arrow-icon"><ArrowRight /></el-icon>
          </li>
        </ul>
      </el-collapse-item>
    </el-collapse>
    <el-empty v-else description="暂无章节"></el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, defineProps } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { ElCollapse, ElCollapseItem, ElEmpty, ElIcon } from 'element-plus';
import { CircleCheckFilled, ArrowRight } from '@element-plus/icons-vue';

interface Chapter {
  id: number;
  title: string;
  parent?: number | null;
  children?: Chapter[];
}

const props = defineProps<{
  courseId: string;
  activeSectionId: number;
}>();

const router = useRouter();
const chapters = ref<Chapter[]>([]);
const activeCollapse = ref<string[]>([]);

const findChapterIdOfSection = (sectionId: number): string | null => {
  for (const chapter of chapters.value) {
    if (chapter.children?.some(section => section.id === sectionId)) {
      return chapter.id.toString();
    }
  }
  return null;
};

const fetchChapters = async () => {
  try {
    const response = await apiClient.get(`/courses/${props.courseId}/chapters/`);
    chapters.value = response.data;
    // 默认展开包含当前激活节的章
    const activeChapterId = findChapterIdOfSection(props.activeSectionId);
    if (activeChapterId) {
      activeCollapse.value = [activeChapterId];
    } else if (chapters.value.length > 0) {
      // 否则默认展开第一章
      activeCollapse.value = [chapters.value[0].id.toString()];
    }
  } catch (error) {
    console.error('获取章节列表失败:', error);
  }
};

const handleSectionClick = (section: Chapter) => {
  if (section.id !== props.activeSectionId) {
    router.push({ name: 'section-detail', params: { id: props.courseId, sectionId: section.id } });
  }
};

onMounted(() => {
  fetchChapters();
});

watch(() => props.activeSectionId, (newVal) => {
  const activeChapterId = findChapterIdOfSection(newVal);
  if (activeChapterId && !activeCollapse.value.includes(activeChapterId)) {
    activeCollapse.value.push(activeChapterId);
  }
});
</script>

<style scoped>
.chapter-navigator {
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
}
.navigator-title {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
.chapter-collapse {
  border: none;
}

:deep(.el-collapse-item__header) {
  background-color: #f7f8fa;
  border-radius: 6px;
  margin-bottom: 8px;
  padding: 0 15px;
  height: 50px;
  font-size: 15px;
  font-weight: 500;
  border: none;
}

:deep(.el-collapse-item__wrap) {
  background-color: transparent;
  border: none;
  padding-left: 15px;
}

:deep(.el-collapse-item__content) {
  padding-bottom: 0;
}

.chapter-title {
  flex: 1;
}

.section-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.section-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  margin-bottom: 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
  gap: 10px;
}

.section-item:hover {
  background-color: #f0f5ff;
}

.section-item.is-active {
  background-color: #e6f7ff;
  color: #409eff;
  font-weight: bold;
}

.section-item.is-active .completion-icon,
.section-item.is-active .arrow-icon {
  color: #409eff;
}

.completion-icon {
  color: #909399;
  font-size: 16px;
}

.section-title {
  flex-grow: 1;
  font-size: 14px;
}

.arrow-icon {
  color: #909399;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.3s;
}

.section-item:hover .arrow-icon,
.section-item.is-active .arrow-icon {
  opacity: 1;
}
</style>
