<template>
  <div class="vote-detail-container">
    <div v-if="vote">
      <el-page-header @back="goBack" class="page-header">
        <template #content>
          <div class="header-content">
            <span class="title">{{ vote.title }}</span>
            <el-tag :type="vote.is_active ? 'success' : 'info'" size="large" class="status-tag">
              {{ vote.is_active ? '进行中' : '已结束' }}
            </el-tag>
          </div>
        </template>
      </el-page-header>

      <div class="scrollable-content">
        <!-- Student Voting UI -->
        <div v-if="!isTeacher && !userHasVoted && vote.is_active" class="student-voting-section">
          <h3>请选择您的选项：</h3>
        <div class="vote-options-grid">
          <div
            v-for="option in vote.choices"
            :key="option.id"
            class="option-card"
            :class="{ selected: selectedOption === option.id }"
            @click="selectOption(option.id)"
          >
            {{ option.text }}
          </div>
        </div>
        <el-button
          type="primary"
          @click="handleVoteSubmission"
          :disabled="!selectedOption"
          class="submit-vote-btn"
          size="large"
        >
          确认投票
        </el-button>
      </div>

      <!-- Results View (for Teacher, or Student who has voted/vote ended) -->
      <div v-else class="results-section">
        <div v-if="isTeacher" class="teacher-actions">
          <el-button v-if="vote.is_active" type="warning" @click="handleEndVote">结束投票</el-button>
          <el-button type="danger" @click="handleDeleteVote">删除投票</el-button>
        </div>
        <h3>投票结果</h3>
        <div class="results-grid">
          <el-card v-for="option in vote.choices" :key="option.id" class="result-card" shadow="hover">
            <div class="result-card-header">
              <span class="option-text">{{ option.text }}</span>
              <span class="vote-count"
                >{{ option.response_count }} 票 ({{
                  calculatePercentage(option.response_count).toFixed(1)
                }}%)</span
              >
            </div>
            <el-progress
              :percentage="calculatePercentage(option.response_count)"
              :stroke-width="12"
              striped
              striped-flow
              :color="getProgressBarColor(calculatePercentage(option.response_count))"
            />
            <!-- Only show voters list to teacher -->
            <div v-if="isTeacher && option.voters && option.voters.length > 0" class="voters-list">
              <el-collapse>
                <el-collapse-item :title="`查看投票学生 (${option.voters.length}人)`" name="1">
                  <el-tag
                    v-for="voter in option.voters"
                    :key="voter.id"
                    size="small"
                    class="voter-tag"
                  >
                    {{ voter.username }}
                  </el-tag>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-card>
        </div>
        <p class="total-votes">总票数: {{ totalVotes }}</p>
      </div>
      </div>
    </div>
    <div v-else>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getVoteDetail, submitVote, endVote, deleteVote } from '@/services/api';
import { ElMessage, ElMessageBox, ElProgress, ElTag, ElButton, ElCard, ElCollapse, ElCollapseItem, ElPageHeader } from 'element-plus';
import type { Vote } from '@/types';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const isTeacher = computed(() => userStore.isTeacher);

const route = useRoute();
const router = useRouter();
const courseId = ref(Number(route.params.id));
const voteId = ref(Number(route.params.voteId));

const vote = ref<Vote | null>(null);
const userHasVoted = ref(false);
const selectedOption = ref<number | null>(null);

const fetchVoteDetail = async () => {
  try {
    const response = await getVoteDetail(courseId.value, voteId.value);
    vote.value = response.data;
    userHasVoted.value = response.data.user_has_voted;
  } catch (error) {
    ElMessage.error('获取投票详情失败');
    console.error(error);
  }
};

const selectOption = (optionId: number) => {
  selectedOption.value = optionId;
};

const handleVoteSubmission = async () => {
  if (!selectedOption.value) {
    ElMessage.warning('请选择一个选项');
    return;
  }
  try {
    await submitVote(courseId.value, voteId.value, selectedOption.value);
    ElMessage.success('投票成功');
    userHasVoted.value = true;
    fetchVoteDetail();
  } catch (error) {
    ElMessage.error('投票失败');
    console.error(error);
  }
};

const handleEndVote = async () => {
  ElMessageBox.confirm('确定要结束这个投票吗？结束后学生将无法再次投票。', '确认结束', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await endVote(courseId.value, voteId.value);
      ElMessage.success('投票已结束');
      fetchVoteDetail();
    } catch (error) {
      ElMessage.error('操作失败');
      console.error(error);
    }
  });
};

const handleDeleteVote = async () => {
  ElMessageBox.confirm('确定要删除这个投票吗？此操作不可恢复。', '确认删除', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'error',
  }).then(async () => {
    try {
      await deleteVote(courseId.value, voteId.value);
      ElMessage.success('投票已删除');
      router.push({ name: 'course-tasks', params: { id: courseId.value } });
    } catch (error) {
      ElMessage.error('删除失败');
      console.error(error);
    }
  });
};

const totalVotes = computed(() => {
  if (!vote.value) return 0;
  return vote.value.choices.reduce((sum, option) => sum + option.response_count, 0);
});

const calculatePercentage = (count: number) => {
  if (totalVotes.value === 0) return 0;
  return (count / totalVotes.value) * 100;
};

const getProgressBarColor = (percentage: number) => {
  if (percentage > 75) return '#67C23A';
  if (percentage > 50) return '#409EFF';
  if (percentage > 25) return '#E6A23C';
  return '#F56C6C';
};

const goBack = () => {
  router.push({ name: 'course-tasks', params: { id: courseId.value } });
};

onMounted(async () => {
  await userStore.fetchUser();
  fetchVoteDetail();
});
</script>

<style scoped>
.vote-detail-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px); /* Adjust this value based on your layout's header/footer height */
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 20px;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title {
  font-size: 24px;
  font-weight: bold;
}

.status-tag {
  transform: translateY(-2px);
}

.teacher-actions {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  display: flex;
  gap: 12px;
}

.student-voting-section, .results-section {
  background-color: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #303133;
}

.vote-options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.option-card {
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 500;
}

.option-card:hover {
  border-color: #409eff;
  color: #409eff;
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
}

.option-card.selected {
  background-color: #409eff;
  color: #fff;
  border-color: #409eff;
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.2);
}

.submit-vote-btn {
  width: 100%;
}

.results-grid {
  display: grid;
  gap: 20px;
}

.result-card {
  border-left: 5px solid;
  border-left-color: var(--el-color-primary);
}

.result-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.option-text {
  font-weight: bold;
  font-size: 16px;
}

.vote-count {
  font-size: 14px;
  color: #606266;
}

.voters-list {
  margin-top: 16px;
}

.voter-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.total-votes {
  margin-top: 24px;
  font-weight: bold;
  font-size: 16px;
  text-align: right;
  color: #303133;
}

.scrollable-content {
  flex-grow: 1;
  overflow-y: auto;
  padding-right: 10px; /* Add some padding to avoid scrollbar overlapping content */
}
</style>
