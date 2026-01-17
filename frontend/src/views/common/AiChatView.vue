<template>
  <div class="ai-chat-layout">
    <!-- Sidebar for chat sessions -->
    <div class="chat-sidebar">
      <el-button @click="createNewSession" class="new-chat-btn">
        + 新建聊天
      </el-button>
      <div class="session-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-item"
          :class="{ active: activeSessionId === session.id }"
          @click="selectSession(session.id)"
        >
          <span class="session-topic">{{ session.topic || '新聊天' }}</span>
          <el-icon class="delete-icon" @click.stop="deleteSession(session.id)"><Delete /></el-icon>
        </div>
      </div>
    </div>

    <!-- Main chat window -->
    <div class="ai-chat-container">
      <div class="chat-history">
        <div v-for="message in messages" :key="message.id" class="message" :class="message.is_from_user ? 'user' : 'assistant'">
          <p v-if="message.is_from_user">{{ message.content }}</p>
          <div v-else v-html="marked.parse(message.content)"></div>
        </div>
      </div>
      <div class="chat-input">
        <el-input
          v-model="newMessage"
          placeholder="向 AI 助教提问..."
          @keyup.enter="sendMessage"
          :disabled="!activeSessionId"
        >
          <template #append>
            <el-button @click="sendMessage" :disabled="isSending || !activeSessionId">
              {{ isSending ? '发送中...' : '发送' }}
            </el-button>
          </template>
        </el-input>
        <el-select v-model="selectedModel" placeholder="选择模型" style="width: 250px; margin-left: 10px;">
          <el-option
            v-for="model in models"
            :key="model.id"
            :label="model.name"
            :value="model.id">
          </el-option>
        </el-select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { marked } from 'marked';
import api from '@/services/api';
import type { ChatSession, ChatMessage } from '@/types';
import { ElMessageBox } from 'element-plus';
import { Delete } from '@element-plus/icons-vue';

const newMessage = ref('');
const messages = ref<ChatMessage[]>([]);
const sessions = ref<ChatSession[]>([]);
const activeSessionId = ref<number | null>(null);
const isSending = ref(false);

const models = ref([
  { id: 'google/gemma-3-27b-it:free', name: 'Google Gemma 3' },
  { id: 'xiaomi/mimo-v2-flash:free', name: 'MiMo-V2-Flash' },
  { id: 'tngtech/deepseek-r1t2-chimera:free', name: 'DeepSeek R1T2' },
  { id: 'meta-llama/llama-3.3-70b-instruct:free', name: 'Meta Llama 3.3' },
  { id: 'mistralai/devstral-2512:free', name: 'Mistral Devstral 2 2512' },
]);
const selectedModel = ref(models.value[0].id);

const fetchSessions = async () => {
  try {
    const response = await api.get('/ai/sessions/');
    sessions.value = response.data;
    if (sessions.value.length > 0 && !activeSessionId.value) {
      selectSession(sessions.value[0].id);
    }
  } catch (error) {
    console.error('Error fetching sessions:', error);
  }
};

const fetchMessages = async (sessionId: number) => {
  try {
    const response = await api.get(`/ai/sessions/${sessionId}/messages/`);
    messages.value = response.data;
  } catch (error) {
    console.error('Error fetching messages:', error);
    messages.value = [];
  }
};

const selectSession = (sessionId: number) => {
  activeSessionId.value = sessionId;
  fetchMessages(sessionId);
};

const deleteSession = async (sessionId: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个聊天会话吗？此操作不可撤销。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    await api.delete(`/ai/sessions/${sessionId}/`);
    
    const deletedIndex = sessions.value.findIndex(s => s.id === sessionId);
    if (deletedIndex > -1) {
      sessions.value.splice(deletedIndex, 1);
    }

    if (activeSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        // Select the previous session or the first one
        const newIndex = Math.max(0, deletedIndex - 1);
        selectSession(sessions.value[newIndex].id);
      } else {
        // If no sessions left, create a new one
        createNewSession();
      }
    }

  } catch (error) {
    // If error is 'cancel', it means user clicked cancel, so we do nothing.
    if (error !== 'cancel') {
      console.error('Error deleting session:', error);
    }
  }
};

const createNewSession = async () => {
  try {
    const response = await api.post('/ai/sessions/', {});
    const newSession = response.data;
    sessions.value.unshift(newSession);
    activeSessionId.value = newSession.id;
    messages.value = [];
  } catch (error) {
    console.error('Error creating new session:', error);
  }
};

const sendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value || !activeSessionId.value) return;

  isSending.value = true;

  const userMessageContent = newMessage.value;
  const currentSessionId = activeSessionId.value;
  
  // Add user message to UI immediately
  messages.value.push({
    id: Date.now(), // Temporary ID
    content: userMessageContent,
    is_from_user: true,
    created_at: new Date().toISOString(),
  });

  newMessage.value = '';

  try {
    const response = await api.post(`/ai/sessions/${currentSessionId}/messages/`, { content: userMessageContent, model: selectedModel.value });
    const assistantMessage = response.data;
    messages.value.push(assistantMessage);

    // If the session was new, it now has a topic, so refresh the session list
    const activeSession = sessions.value.find(s => s.id === currentSessionId);
    if (activeSession && !activeSession.topic) {
        fetchSessions();
    }

  } catch (error) {
    console.error('Error fetching AI response:', error);
    messages.value.push({
      id: Date.now(),
      content: '抱歉，AI 助教当前不可用。请稍后再试。',
      is_from_user: false,
      created_at: new Date().toISOString(),
    });
  } finally {
    isSending.value = false;
  }
};

onMounted(() => {
  fetchSessions();
});
</script>

<style scoped>
.ai-chat-layout {
  display: flex;
  height: calc(100vh - 120px); /* Adjust based on your layout's header/footer */
}

.chat-sidebar {
  width: 250px;
  flex-shrink: 0;
  border-right: 1px solid #e0e0e0;
  padding: 15px;
  display: flex;
  flex-direction: column;
  background-color: #fafafa;
}

.new-chat-btn {
  width: 100%;
  margin-bottom: 15px;
}

.session-list {
  flex-grow: 1;
  overflow-y: auto;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  cursor: pointer;
  border-radius: 5px;
  margin-bottom: 5px;
  width: 100%;
  box-sizing: border-box;
}

.session-topic {
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  flex-grow: 1;
}

.delete-icon {
  visibility: hidden; /* Hidden by default but occupies space */
  margin-left: 10px;
  color: #999;
}

.delete-icon:hover {
  color: #f56c6c;
}

.session-item:hover .delete-icon {
  visibility: visible; /* Show on hover */
}

.session-item:hover {
  background-color: #f0f0f0;
}

.session-item.active {
  background-color: #e0e0e0;
  font-weight: bold;
}

.ai-chat-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0 20px 20px 20px;
}

.chat-history {
  flex-grow: 1;
  overflow-y: auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  margin-bottom: 20px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 15px;
  padding: 10px 15px;
  border-radius: 10px;
  max-width: 80%;
}

.message p {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

.message.assistant :deep(p) {
  margin-bottom: 1rem;
}

.message.assistant :deep(p):last-child {
  margin-bottom: 0;
}

.message.assistant :deep(ul), .message.assistant :deep(ol) {
  margin: 0;
  padding-left: 1.5em;
}

.message.user {
  background-color: #dcf8c6;
  align-self: flex-end;
}

.message.assistant {
  background-color: #f1f0f0;
}

.chat-input {
  display: flex;
}
</style>
