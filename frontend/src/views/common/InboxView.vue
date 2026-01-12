<template>
  <div class="inbox-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>收件箱</span>
          <div>
            <el-button type="primary" @click="markAllAsRead">全部已读</el-button>
          </div>
        </div>
      </template>
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="notifications.length === 0" class="empty-container">
        <el-empty description="收件箱是空的"></el-empty>
      </div>
      <div v-else class="notification-list-wrapper">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ 'is-read': notification.is_read }"
          @click="handleNotificationClick(notification)"
        >
          <div class="notification-icon-wrapper" :class="notification.is_read ? 'status-read' : 'status-unread'">
            <div class="notification-type-name">{{ getNotificationTypeName(notification.content_type_name) }}</div>
          </div>
          <div class="notification-content">
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-header">
              <span class="notification-sender">{{ notification.sender.username }}</span>
              <span class="notification-timestamp">{{ formatTimestamp(notification.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import api from '@/services/api';
import { ElMessage } from 'element-plus';

const router = useRouter();
const userStore = useUserStore();
const notifications = ref<any[]>([]);
const loading = ref(true);

const fetchAllNotifications = async () => {
  loading.value = true;
  try {
    const response = await api.get('/notifications/');
    notifications.value = response.data;
  } catch (error) {
    ElMessage.error('无法加载通知');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleNotificationClick = async (notification: any) => {
  if (!notification.is_read) {
    try {
      await api.post(`/notifications/${notification.id}/mark_as_read/`);
      notification.is_read = true;
      userStore.fetchUnreadCount(); // Re-fetch the count from the server
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }

  const { content_type_name, related_object_info } = notification;
  if (!related_object_info) {
    console.warn('No routing info for this notification.');
    return;
  }

  const { course_id, id: object_id } = related_object_info;
  let route: any = null;

  switch (content_type_name) {
    case 'assignment':
      route = { name: 'course-assignments', params: { id: course_id } };
      break;
    case 'exam':
      route = { name: 'course-exams', params: { id: course_id } };
      break;
    case 'discussiontopic':
      route = { name: 'course-discussion-detail', params: { id: course_id, topicId: object_id } };
      break;
    case 'announcement':
      route = { name: 'course-announcements', params: { id: course_id } };
      break;
    case 'assignment':
    case 'submission':
      route = { name: 'assignment-detail', params: { id: object_id } };
      break;
    case 'exam':
    case 'examsubmission':
      route = { name: 'ExamDetail', params: { id: object_id } };
      break;
    case 'discussiontopic':
      case 'discussionreply':
        route = { name: 'course-discussion-detail', params: { id: course_id, topicId: object_id } };
        break;
      case 'feedbackresponse':
        route = { name: 'course-feedback-results', params: { id: course_id, feedbackId: object_id } };
        break;
    case 'announcement':
      route = { name: 'course-announcements', params: { id: course_id } };
      break;
    case 'vote':
    case 'voteresponse':
      route = { name: 'vote-detail', params: { id: course_id, voteId: object_id } };
      break;
    case 'checkin':
    case 'checkinrecord':
      route = { name: 'checkin-detail', params: { id: course_id, checkinId: object_id } };
      break;
    case 'question':
      route = { name: 'QuestionDetail', params: { id: course_id, taskId: object_id } };
      break;
    case 'randomquestion':
        route = { name: 'RandomQuestionDetail', params: { id: course_id, taskId: object_id } };
        break;
    case 'questionnaire':
        // Assuming student fills feedback, teacher sees results
        if (userStore.user?.role === 'student') {
            route = { name: 'course-feedback-fill', params: { id: course_id, feedbackId: object_id } };
        } else {
            route = { name: 'course-feedback-results', params: { id: course_id, feedbackId: object_id } };
        }
        break;
    default:
      console.warn(`Unhandled content type: ${content_type_name}`);
  }

  if (route) {
    router.push(route);
  }
};

const getNotificationTypeName = (contentTypeName: string) => {
    const contentTypeMap: { [key: string]: string } = {
        'announcement': '公告',
        'assignment': '作业',
        'submission': '作业',
        'checkin': '签到',
        'checkinrecord': '签到',
        'discussiontopic': '讨论',
        'discussionreply': '讨论',
        'exam': '考试',
        'examsubmission': '考试',
        'question': '提问',
        'questionnaire': '反馈',
        'feedbackresponse': '反馈',
        'vote': '投票',
        'voteresponse': '投票',
        'randomquestion': '提问',
    };
    return contentTypeMap[contentTypeName] || '通知';
};


const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const markAllAsRead = async () => {
  try {
    await api.post('/notifications/mark_all_as_read/');
    notifications.value.forEach(n => n.is_read = true);
    userStore.fetchUnreadCount(); // Re-fetch the count from the server
    ElMessage.success('所有通知已标记为已读');
  } catch (error) {
    ElMessage.error('无法标记所有通知为已读');
    console.error(error);
  }
};

onMounted(() => {
  fetchAllNotifications();
});
</script>

<style scoped>
.inbox-container {
  padding: 20px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.box-card {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.el-card__body) {
  padding: 0;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.notification-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}
.notification-item:hover {
  background-color: #f5f7fa;
}
.notification-item.is-read {
  color: #909399;
}
.notification-item.is-read .notification-sender {
  font-weight: normal;
}
.notification-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
  color: #fff;
}
.notification-type-name {
  font-size: 14px;
  font-weight: 500;
}
.status-unread {
  background-color: #409eff;
}
.status-read {
  background-color: #c0c4cc;
}
.notification-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}
.notification-header {
  display: flex;
  justify-content: space-between;
  order: 2;
}
.notification-sender {
  font-weight: normal;
}
.notification-message {
  font-weight: bold;
  order: 1;
  margin-bottom: 5px;
}
.notification-timestamp {
  font-size: 12px;
  color: #909399;
}
.loading-container,
.empty-container {
  padding: 20px;
  text-align: center;
  flex-grow: 1; /* Allow empty/loading states to center in the flex body */
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-list-wrapper {
  overflow-y: auto;
  flex-grow: 1;
}
</style>
