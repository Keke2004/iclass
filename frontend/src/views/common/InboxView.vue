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
            <div class="notification-type-name">{{ getNotificationTypeName(notification.content_type) }}</div>
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
  // Navigate to the related object's detail page
  // This needs a mapping from content_type to a route name
  const { content_type, object_id } = notification;
  const route = getRouteForContentType(content_type, object_id);
  if (route) {
    router.push(route);
  }
};

const getRouteForContentType = (contentTypeId: number, objectId: number) => {
    // This is a simplified mapping. In a real app, you might get this from the API
    // or have a more robust system.
    // You need to map content_type ID to your frontend routes.
    // The IDs depend on the order of your models in INSTALLED_APPS.
    // You can find the content_type IDs in your database's `django_content_type` table.
    // Let's assume some IDs for now.
    // 10: assignment, 11: submission, 12: exam, 13: examsubmission, etc.
    // This part is highly dependent on your project's `django_content_type` table.
    // You should replace these with the actual IDs from your database.
    const contentTypeMap: { [key: number]: string } = {
        10: 'AssignmentDetail', // Placeholder
        11: 'SubmissionDetail', // Placeholder
        12: 'ExamDetail', // Placeholder
        13: 'ExamSubmissionDetail', // Placeholder
        18: 'DiscussionTopicDetail', // Placeholder
        8: 'CheckinDetail', // Placeholder
    };
    const routeName = contentTypeMap[contentTypeId];
    if (routeName) {
        return { name: routeName, params: { id: objectId } };
    }
    return null;
}

const getNotificationTypeName = (contentTypeId: number) => {
    const contentTypeMap: { [key: number]: string } = {
        9: '公告',
        10: '作业',
        35: '签到',
        28: '讨论',
        30: '考试',
        20: '提问',
        21: '反馈',
        36: '提问',
        15: '投票',
    };
    return contentTypeMap[contentTypeId] || '通知';
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
