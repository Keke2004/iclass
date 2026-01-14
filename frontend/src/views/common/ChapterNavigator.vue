<template>
  <div class="chapter-navigator">
    <div class="navigator-header">
      <h4 class="navigator-title">课程大纲</h4>
      <div v-if="userStore.isStudent" class="progress-container">
        <span class="progress-text">已完成任务点: {{ learningProgress.completed }}/{{ learningProgress.total }}</span>
        <el-progress :percentage="learningProgress.percentage" :stroke-width="6" :show-text="false" class="progress-bar" />
      </div>
    </div>
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
            :class="{ 'is-active': section.id === activeSectionId, 'is-read': section.is_read }"
            @click="handleSectionClick(section)"
          >
            <el-icon v-if="section.is_read" class="completion-icon is-read"><SuccessFilled /></el-icon>
            <span v-else class="completion-icon-unread"></span>
            <span class="section-title">{{ `${index + 1}.${secIndex + 1} ${section.title}` }}</span>
          </li>
        </ul>
      </el-collapse-item>
    </el-collapse>
    <el-empty v-else description="暂无章节"></el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, defineProps, computed, defineEmits, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { useUserStore } from '@/stores/user';
import { ElCollapse, ElCollapseItem, ElEmpty, ElIcon, ElProgress } from 'element-plus';
import { SuccessFilled, ArrowRight } from '@element-plus/icons-vue';

interface Chapter {
  id: number;
  title: string;
  is_read: boolean;
  parent?: number | null;
  children?: Chapter[];
}

const props = defineProps<{
  courseId: string;
  activeSectionId: number;
}>();

const emit = defineEmits(['refetchChapters']);

const router = useRouter();
const userStore = useUserStore();
const chapters = ref<Chapter[]>([]);
const course = ref<{ progress: { completed: number, total: number } } | null>(null);
const activeCollapse = ref<number[]>([]);

const learningProgress = computed(() => {
  if (course.value && course.value.progress) {
    const { completed, total } = course.value.progress;
    const percentage = total > 0 ? (completed / total) * 100 : 0;
    return { completed, total, percentage };
  }
  return { completed: 0, total: 0, percentage: 0 };
});

const findChapterIdOfSection = (sectionId: number): number | null => {
  for (const chapter of chapters.value) {
    if (chapter.children?.some(section => section.id === sectionId)) {
      return chapter.id;
    }
  }
  return null;
};

const fetchChapters = async () => {
  try {
    const [chaptersResponse, courseResponse] = await Promise.all([
      apiClient.get(`/courses/${props.courseId}/chapters/`),
      apiClient.get(`/courses/${props.courseId}/`)
    ]);
    chapters.value = chaptersResponse.data;
    course.value = courseResponse.data;
  } catch (error) {
    console.error('获取章节或课程数据失败:', error);
  }
};

const handleSectionClick = (section: Chapter) => {
  if (section.id !== props.activeSectionId) {
    router.push({ name: 'section-detail', params: { id: props.courseId, sectionId: section.id } });
  }
};

const refetchChapters = () => {
  fetchChapters();
  emit('refetchChapters');
};

onMounted(() => {
  fetchChapters();
});

// 监听章节数据变化，自动展开所有章节
watch(chapters, (newChapters) => {
  if (newChapters && newChapters.length > 0) {
    activeCollapse.value = newChapters.map(chapter => chapter.id);
  }
}, { deep: true, immediate: true });

watch(() => props.activeSectionId, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    fetchChapters(); // 当 sectionId 变化时，重新获取章节数据以更新已读状态
  }
});

defineExpose({
  fetchChapters
});

</script>

<style scoped>
.chapter-navigator {
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
}
.navigator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.navigator-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
.progress-container {
  display: flex;
  align-items: center;
  gap: 8px;
}
.progress-text {
  font-size: 12px;
  color: #909399;
}
.progress-bar {
  width: 80px;
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
  margin-left: 8px;
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

.completion-icon-chapter {
  font-size: 16px;
}

.completion-icon {
  font-size: 16px;
}

.completion-icon.is-read, .completion-icon-chapter.is-read {
  color: #67c23a;
}

.completion-icon-unread {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #e6a23c;
  margin: 4px; /* to align with the icon */
}

.section-title {
  flex-grow: 1;
  font-size: 14px;
}

.section-item.is-read .section-title {
  /* color: #909399; */ /* Optional: change color for read sections */
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
