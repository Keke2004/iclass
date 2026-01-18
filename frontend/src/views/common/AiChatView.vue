<template>
  <div class="ai-chat-layout">
    <!-- Sidebar for chat sessions -->
    <div class="chat-sidebar">
      <el-button @click="createNewSession" class="new-chat-btn" type="primary" plain>
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
      <div class="chat-history-wrapper" ref="chatHistoryWrapper">
        <div class="chat-history">
          <div v-for="message in messages" :key="message.id" 
               class="message-container" 
               :class="message.is_from_user ? 'user-container' : 'assistant-container'">
            <div class="message" :class="message.is_from_user ? 'user' : 'assistant'">
              <p v-if="message.is_from_user">{{ message.content }}</p>
              <div v-else v-html="marked.parse(message.content)"></div>
            </div>
            <button class="copy-message-btn" @click="copyToClipboard(message.content, $event.currentTarget)">
              <el-icon><CopyDocument /></el-icon>
            </button>
          </div>
        </div>
      </div>
      <div class="chat-input-area">
        <el-select v-model="selectedModel" placeholder="选择模型" class="model-selector">
          <el-option
            v-for="model in models"
            :key="model.id"
            :label="model.name"
            :value="model.id">
          </el-option>
        </el-select>
        <div class="chat-input">
          <el-input
            v-model="newMessage"
            placeholder="向 AI 助教提问..."
            @keyup.enter="sendMessage"
            :disabled="!activeSessionId"
            size="large"
          />
          <el-button @click="sendMessage" :disabled="isSending || !activeSessionId" type="primary" size="large">
            {{ isSending ? '...' : '发送' }}
          </el-button>
        </div>
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
import { Delete, CopyDocument } from '@element-plus/icons-vue';

const chatHistoryWrapper = ref<HTMLElement | null>(null);

const copyToClipboard = async (text: string, button: EventTarget | null) => {
  if (!button || !(button instanceof HTMLElement)) return;
  try {
    await navigator.clipboard.writeText(text);
    const originalContent = button.innerHTML;
    button.innerHTML = '✓';
    button.classList.add('copied');
    setTimeout(() => {
      button.innerHTML = originalContent;
      button.classList.remove('copied');
    }, 2000);
  } catch (err) {
    console.error('Failed to copy: ', err);
    const originalContent = button.innerHTML;
    button.innerHTML = 'X';
    setTimeout(() => {
      button.innerHTML = originalContent;
    }, 2000);
  }
};

const setupMarked = () => {
  const renderer = new marked.Renderer();
  const originalCodeRenderer = renderer.code;

  renderer.code = (code, lang, escaped) => {
    const rawCodeHtml = originalCodeRenderer.call(renderer, code, lang, escaped);
    // Ensure code is a string and properly escape it for the data attribute
    const safeCode = String(code || '');
    const escapedCode = safeCode.replace(/'/g, '&#39;').replace(/"/g, '"');
    const copyButtonHtml = `<button class="copy-code-btn" data-code='${escapedCode}'>复制</button>`;
    return `<div class="code-block-wrapper">${copyButtonHtml}${rawCodeHtml}</div>`;
  };

  marked.setOptions({ renderer });
};

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
        const newIndex = Math.max(0, deletedIndex - 1);
        selectSession(sessions.value[newIndex].id);
      } else {
        // If no sessions left, clear the chat window
        activeSessionId.value = null;
        messages.value = [];
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
  setupMarked();
  fetchSessions();

  if (chatHistoryWrapper.value) {
    chatHistoryWrapper.value.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      if (target && target.classList.contains('copy-code-btn')) {
        const code = target.getAttribute('data-code');
        if (code) {
          copyToClipboard(code, target);
        }
      }
    });
  }
});
</script>

<style scoped>
:root {
  --chat-bg: #f7f8fa;
  --sidebar-bg: #ffffff;
  --primary-color: #409eff;
  --user-msg-bg: #e1f0ff;
  --assistant-msg-bg: #f0f2f5;
  --text-primary: #303133;
  --text-secondary: #606266;
  --border-color: #e4e7ed;
}

.ai-chat-layout {
  display: flex;
  height: calc(100vh - 100px); /* Adjust based on your layout's header/footer */
  background-color: var(--chat-bg);
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.chat-sidebar {
  width: 260px;
  flex-shrink: 0;
  border-right: 1px solid var(--border-color);
  padding: 20px 10px;
  display: flex;
  flex-direction: column;
  background-color: var(--sidebar-bg);
  transition: width 0.3s ease;
}

.new-chat-btn {
  width: 100%;
  margin-bottom: 20px;
  font-size: 14px;
}

.session-list {
  flex-grow: 1;
  overflow-y: auto;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  cursor: pointer;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: background-color 0.2s ease, color 0.2s ease;
  position: relative;
}

.session-topic {
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  flex-grow: 1;
  font-size: 14px;
  color: var(--text-secondary);
}

.delete-icon {
  visibility: hidden;
  opacity: 0;
  margin-left: 10px;
  color: #999;
  transition: opacity 0.2s ease;
}

.session-item:hover {
  background-color: #f5f7fa;
}

.session-item:hover .delete-icon {
  visibility: visible;
  opacity: 1;
}

.delete-icon:hover {
  color: #f56c6c;
}

.session-item.active {
  background-color: #ecf5ff;
}

.session-item.active .session-topic {
  color: #409eff;
  font-weight: 600;
}

.session-item.active .delete-icon {
  color: #409eff;
}

.session-item.active .delete-icon:hover {
  color: #f56c6c;
}

.ai-chat-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
  overflow: hidden;
}

.chat-history-wrapper {
  flex-grow: 1;
  overflow-y: auto;
  margin-bottom: 20px;
  padding-right: 10px; /* For scrollbar */
}

.chat-history {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-container {
  display: flex;
  flex-direction: column;
  gap: 4px; /* Adjust gap for vertical layout */
  position: relative; /* Keep relative for positioning children if needed */
}

.message-container.user-container {
  align-items: flex-end;
}

.message-container.assistant-container {
  align-items: flex-start;
}

.message {
  padding: 12px 18px;
  border-radius: 18px;
  max-width: 75%;
  line-height: 1.6;
}

.message p {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

.message.user {
  background-color: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant {
  background-color: #ffffff;
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
  border: 1px solid var(--border-color);
}

/* Markdown styles */
.message.assistant :deep(p) {
  margin-bottom: 1em;
}
.message.assistant :deep(p):last-child {
  margin-bottom: 0;
}
.message.assistant :deep(ul),
.message.assistant :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 1em;
}
.message.assistant :deep(pre) {
  background-color: #282c34;
  color: #abb2bf;
  padding: 1em;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'Fira Code', 'Courier New', monospace;
}
.message.assistant :deep(code) {
  background-color: rgba(0,0,0,0.05);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
}
.message.assistant :deep(pre code) {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

.chat-input-area {
  flex-shrink: 0;
  padding: 10px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.model-selector {
  width: 100%;
  margin-bottom: 10px;
}

.chat-input {
  display: flex;
  gap: 10px;
}

.chat-input .el-input {
  flex-grow: 1;
}

.chat-input .el-button {
  flex-shrink: 0;
}

/* Styles for copy buttons */
.copy-message-btn {
  background: transparent;
  border: none;
  border-radius: 4px;
  width: 28px;
  height: 28px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  visibility: hidden; /* Hide by default */
  opacity: 0;
  transition: opacity 0.2s, visibility 0.2s, background-color 0.2s;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.message-container:hover .copy-message-btn {
  visibility: visible; /* Show on hover */
  opacity: 1;
}

.copy-message-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.copy-message-btn.copied {
  color: #67c23a;
  font-size: 18px;
  font-weight: bold;
}

.message.assistant :deep(.code-block-wrapper) {
  position: relative;
}

.message.assistant :deep(.copy-code-btn) {
  position: absolute;
  top: 1em; /* Match pre padding */
  right: 1em; /* Match pre padding */
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  visibility: hidden; /* Hide by default */
  opacity: 0;
  transition: opacity 0.2s, visibility 0.2s;
  z-index: 10;
}

.message.assistant :deep(.code-block-wrapper:hover .copy-code-btn) {
  visibility: visible; /* Show on hover */
  opacity: 1;
}

.message.assistant :deep(.copy-code-btn:hover) {
  background: rgba(255, 255, 255, 0.2);
}

.message.assistant :deep(.copy-code-btn.copied) {
  background: #67c23a;
  border-color: #67c23a;
  color: white;
}
</style>
