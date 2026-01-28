<template>
  <div class="discussion-manager-container">
    <!-- Action and Filter Bar -->
    <div class="action-filter-bar">
      <div class="top-row">
        <el-button type="primary" @click="showCreateDialog = true" :icon="ElIconPlus">新建话题</el-button>
        <el-menu :default-active="activeFilter" mode="horizontal" class="filter-menu" @select="handleFilterChange">
          <el-menu-item index="all">
            <el-icon><ElIconCollection /></el-icon>
            <span>全部话题</span>
          </el-menu-item>
          <el-menu-item index="my-posts">
            <el-icon><ElIconDocument /></el-icon>
            <span>我发布的</span>
          </el-menu-item>
          <el-menu-item index="my-replies">
            <el-icon><ElIconChatLineRound /></el-icon>
            <span>我回复的</span>
          </el-menu-item>
        </el-menu>
      </div>
      <div class="bottom-row">
        <el-date-picker
          v-model="filter.dateRange"
          type="daterange"
          range-separator="-"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          style="margin-right: 10px;"
          clearable
        ></el-date-picker>
        <el-input v-model="filter.search" placeholder="搜索标题或内容" :prefix-icon="ElIconSearch" style="width: 240px;" clearable></el-input>
      </div>
    </div>

    <!-- Topic List -->
    <div class="topic-list-section">
      <div class="scrollable-area">
        <h3>{{ filterTitles[activeFilter] }} ({{ filteredTopics.length }} 条)</h3>
        <el-card v-if="loading" shadow="never" class="loading-card">
          <p>正在加载...</p>
        </el-card>
        <div v-else-if="filteredTopics.length === 0" class="no-topics">
          <p>这里还没有内容哦~</p>
        </div>
        <div v-else class="topic-list">
          <el-card v-for="topic in filteredTopics" :key="topic.id" class="topic-card" shadow="hover" @click="navigateToTopic(topic.id)">
            <div class="topic-main">
              <div class="topic-header">
                <span class="topic-title">{{ topic.title }}</span>
              </div>
              <div class="topic-content">
                {{ topic.content }}
              </div>
            </div>
            <div class="topic-aside">
              <div class="topic-meta">
                <span>{{ topic.author.username }} | {{ new Date(topic.created_at).toLocaleString() }}</span>
                <el-button
                  v-if="currentUser && (currentUser.id === topic.author.id || isTeacher)"
                  type="danger"
                  size="small"
                  @click.stop="deleteTopic(topic.id)"
                  :icon="ElIconDelete"
                  circle
                ></el-button>
              </div>
              <div class="topic-stats">
                  <el-icon><ElIconChatLineRound /></el-icon>
                  <span class="reply-count">{{ topic.reply_count }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- New Topic Dialog -->
    <el-dialog v-model="showCreateDialog" title="新建话题" width="50%">
      <el-input v-model="newTopic.title" placeholder="请输入标题"></el-input>
      <el-input
        v-model="newTopic.content"
        type="textarea"
        :rows="5"
        placeholder="请输入内容"
        class="topic-content-input"
      ></el-input>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="createTopic">发布</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import { getUserProfile } from '@/services/auth';
import type { User as UserType } from '@/types';
import { ElMessage, ElMessageBox, ElCard, ElButton, ElDatePicker, ElInput, ElMenu, ElMenuItem, ElIcon, ElDialog } from 'element-plus';
import {
  Plus as ElIconPlus,
  Search as ElIconSearch,
  Delete as ElIconDelete,
  Collection as ElIconCollection,
  Document as ElIconDocument,
  ChatLineRound as ElIconChatLineRound,
} from '@element-plus/icons-vue';
import { debounce } from 'lodash-es';

interface Author {
  id: number;
  username: string;
}

interface Topic {
  id: number;
  title: string;
  content: string;
  author: Author;
  created_at: string;
  course: number;
  reply_count: number;
}

const route = useRoute();
const router = useRouter();
const courseId = route.params.id;

const currentUser = ref<UserType | null>(null);
const isTeacher = computed(() => currentUser.value?.role === 'teacher');

const showCreateDialog = ref(false);

type FilterKey = 'all' | 'my-posts' | 'my-replies';

const filter = ref({
  dateRange: null as [Date, Date] | null,
  search: ''
});
const activeFilter = ref<FilterKey>('all');
const filterTitles: Record<FilterKey, string> = {
  all: '全部话题',
  'my-posts': '我发布的',
  'my-replies': '我回复的'
};

const allTopics = ref<Topic[]>([]);
const loading = ref(true);

const newTopic = ref({
  title: '',
  content: ''
});

const filteredTopics = computed(() => {
  let topics = allTopics.value;

  // Always apply client-side filtering for a consistent experience
  if (filter.value.search) {
    const searchTerm = filter.value.search.toLowerCase();
    topics = topics.filter(topic =>
      topic.title.toLowerCase().includes(searchTerm) ||
      topic.content.toLowerCase().includes(searchTerm)
    );
  }
  if (filter.value.dateRange) {
    const [startDate, endDate] = filter.value.dateRange;
    // Adjust endDate to be inclusive of the whole day
    const inclusiveEndDate = new Date(endDate);
    inclusiveEndDate.setHours(23, 59, 59, 999);

    topics = topics.filter(topic => {
      const topicDate = new Date(topic.created_at);
      return topicDate >= startDate && topicDate <= inclusiveEndDate;
    });
  }
  
  return topics;
});

const navigateToTopic = (topicId: number) => {
  router.push({ name: 'course-discussion-detail', params: { id: courseId, topicId } });
};

const fetchCurrentUser = async () => {
  try {
    currentUser.value = await getUserProfile();
  } catch (error) {
    console.error("Failed to fetch user profile:", error);
    ElMessage.error('无法获取用户信息');
  }
};

const handleFilterChange = (index: string) => {
  activeFilter.value = index as FilterKey;
};

const fetchTopics = async () => {
  loading.value = true;
  try {
    let response;
    if (activeFilter.value === 'all') {
      const params = new URLSearchParams();
      if (filter.value.search) {
        params.append('search', filter.value.search);
      }
      if (filter.value.dateRange) {
        const startDateStr = filter.value.dateRange[0].toISOString().split('T')[0];
        if (startDateStr) {
          params.append('start_date', startDateStr);
        }
        
        const endDate = new Date(filter.value.dateRange[1]);
        endDate.setDate(endDate.getDate() + 1); // Backend range is exclusive on end date
        const endDateStr = endDate.toISOString().split('T')[0];
        if (endDateStr) {
          params.append('end_date', endDateStr);
        }
      }
      response = await apiClient.get(`/courses/${courseId}/discussions/`, { params });
      allTopics.value = response.data;
    } else {
      // For 'my-posts' and 'my-replies', fetch all and filter on client
      response = await apiClient.get('/mydiscussions/');
      if (activeFilter.value === 'my-posts') {
        allTopics.value = response.data.my_topics;
      } else if (activeFilter.value === 'my-replies') {
        allTopics.value = response.data.replied_topics;
      }
    }
  } catch (error) {
    ElMessage.error('无法加载讨论列表');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const debouncedFetchTopics = debounce(fetchTopics, 300);

watch(activeFilter, fetchTopics);

watch(filter, () => {
  // For 'all' tab, filtering is done by the backend, so refetch
  if (activeFilter.value === 'all') {
    debouncedFetchTopics();
  }
  // For other tabs, filtering is done client-side by the `filteredTopics` computed property,
  // so no network request is needed.
}, { deep: true });


const createTopic = async () => {
  if (!newTopic.value.title.trim() || !newTopic.value.content.trim()) {
    ElMessage.warning('标题和内容不能为空');
    return;
  }
  try {
    await apiClient.post(`/courses/${courseId}/discussions/`, newTopic.value);
    ElMessage.success('话题发布成功');
    newTopic.value.title = '';
    newTopic.value.content = '';
    showCreateDialog.value = false;
    if (activeFilter.value !== 'all') {
      activeFilter.value = 'all'; // Switch to all to see the new post
    } else {
      await fetchTopics(); // Refetch if already on all
    }
  } catch (error) {
    ElMessage.error('发布失败，请稍后重试');
    console.error(error);
  }
};

const deleteTopic = async (topicId: number) => {
  ElMessageBox.confirm('确定要删除这个话题吗？此操作无法撤销。', '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await apiClient.delete(`/courses/${courseId}/discussions/${topicId}/`);
      ElMessage.success('话题已删除');
      await fetchTopics();
    } catch (error) {
      ElMessage.error('删除失败，请稍后重试');
      console.error(error);
    }
  }).catch(() => {
    // User cancelled
  });
};

onMounted(async () => {
  await fetchCurrentUser();
  await fetchTopics();
});
</script>

<style scoped>
.discussion-manager-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
  padding: 20px;
  box-sizing: border-box;
  background-color: #fff;
  border-radius: 8px;
}
.action-filter-bar {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  flex-shrink: 0;
}
.top-row {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}
.bottom-row {
  display: flex;
  align-items: center;
}
.filter-menu {
  border-bottom: none;
  flex-grow: 1;
  margin-left: 20px;
}
.topic-list-section {
  flex-grow: 1;
  overflow: hidden;
}
.scrollable-area {
  height: 100%;
  overflow-y: auto;
  padding-right: 15px; /* for scrollbar */
}

.scrollable-area > h3 {
  margin-bottom: 20px;
  font-size: 1.2em;
  font-weight: 600;
  color: #303133;
  letter-spacing: 0.5px;
}
.no-topics {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}
.topic-content-input {
  margin: 15px 0;
}
.loading-card {
  text-align: center;
  color: #909399;
}
.topic-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.topic-card {
  cursor: pointer;
}

.topic-card :deep(.el-card__body) {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 15px;
}

.topic-main {
  flex-grow: 1;
  margin-right: 20px;
  overflow: hidden;
}

.topic-header {
  margin-bottom: 10px;
}

.topic-title {
  font-weight: bold;
  font-size: 1.1em;
}

.topic-content {
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* Show 2 lines */
  -webkit-box-orient: vertical;
}

.topic-aside {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
}

.topic-meta {
  font-size: 0.9em;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.topic-stats {
  display: flex;
  flex-direction: row;
  align-items: center;
  color: #8c939d;
  background-color: rgba(0, 0, 0, 0.04);
  border-radius: 16px;
  padding: 4px 12px;
}

.topic-stats .el-icon {
  font-size: 1.1em;
  margin-right: 6px;
}

.reply-count {
  font-weight: 500;
  font-size: 0.9em;
  margin-top: 0;
}
</style>
