<template>
  <div class="topic-detail-container">
    <el-card v-if="topic" class="topic-main-card">
      <template #header>
        <div class="topic-header">
          <h2>{{ topic.title }}</h2>
          <span class="topic-meta">
            由 {{ topic.author.username }} 发布于 {{ new Date(topic.created_at).toLocaleString() }}
          </span>
        </div>
      </template>
      <div class="topic-content" v-html="topic.content"></div>
    </el-card>

    <div class="replies-section">
      <h3>{{ replies.length }} 条回复</h3>
      <el-card v-for="reply in replies" :key="reply.id" class="reply-card">
        <div class="reply-header">
          <span class="reply-author">{{ reply.author.username }}</span>
          <span class="reply-time">{{ new Date(reply.created_at).toLocaleString() }}</span>
        </div>
        <div class="reply-content" v-html="reply.content"></div>
      </el-card>
      <el-card v-if="replies.length === 0" class="no-replies-card">
        <p>还没有人回复，快来抢沙发吧！</p>
      </el-card>
    </div>

    <div class="new-reply-section">
      <h3>发表你的回复</h3>
      <el-input
        v-model="newReply.content"
        type="textarea"
        :rows="4"
        placeholder="请输入你的回复..."
      ></el-input>
      <el-button type="primary" @click="postReply" style="margin-top: 15px;">发表回复</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '@/services/api';
import { ElMessage, ElCard, ElInput, ElButton } from 'element-plus';

interface User {
  id: number;
  username: string;
}

interface Topic {
  id: number;
  title: string;
  content: string;
  author: User;
  created_at: string;
}

interface Reply {
  id: number;
  content: string;
  author: User;
  created_at: string;
}

const route = useRoute();
const courseId = route.params.id;
const topicId = route.params.topicId;

const topic = ref<Topic | null>(null);
const replies = ref<Reply[]>([]);
const newReply = ref({ content: '' });

const fetchTopicDetail = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId}/discussions/${topicId}/`);
    topic.value = response.data;
  } catch (error) {
    console.error('Failed to fetch topic details:', error);
    ElMessage.error('加载话题详情失败');
  }
};

const fetchReplies = async () => {
  try {
    const response = await apiClient.get(`/courses/${courseId}/discussions/${topicId}/replies/`);
    replies.value = response.data;
  } catch (error) {
    console.error('Failed to fetch replies:', error);
    ElMessage.error('加载回复列表失败');
  }
};

const postReply = async () => {
  if (!newReply.value.content.trim()) {
    ElMessage.warning('回复内容不能为空');
    return;
  }
  try {
    await apiClient.post(`/courses/${courseId}/discussions/${topicId}/replies/`, newReply.value);
    ElMessage.success('回复成功');
    newReply.value.content = '';
    await fetchReplies(); // Refresh replies
  } catch (error) {
    console.error('Failed to post reply:', error);
    ElMessage.error('回复失败');
  }
};

onMounted(() => {
  fetchTopicDetail();
  fetchReplies();
});
</script>

<style scoped>
.topic-detail-container {
  padding: 20px;
}
.topic-main-card {
  margin-bottom: 20px;
}
.topic-header {
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 15px;
  margin-bottom: 15px;
}
.topic-header h2 {
  margin: 0;
}
.topic-meta {
  font-size: 0.9em;
  color: #909399;
}
.topic-content {
  line-height: 1.6;
}
.replies-section {
  margin-bottom: 20px;
}
.reply-card {
  margin-bottom: 15px;
}
.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 0.9em;
}
.reply-author {
  font-weight: bold;
}
.reply-time {
  color: #909399;
}
.no-replies-card {
  text-align: center;
  color: #909399;
}
.new-reply-section {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}
</style>
