<template>
  <div class="chapter-navigator">
    <h4 class="navigator-title">课程大纲</h4>
    <el-tree
      v-if="chapters.length > 0"
      :data="chapters"
      :props="treeProps"
      node-key="id"
      default-expand-all
      :expand-on-click-node="false"
      class="chapter-tree"
    >
      <template #default="{ node, data }">
        <span 
          class="custom-tree-node" 
          :class="{ 'is-active': data.id === activeSectionId }"
          @click="handleNodeClick(node, data)"
        >
          <span>{{ node.label }}</span>
        </span>
      </template>
    </el-tree>
    <el-empty v-else description="暂无章节"></el-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { ElTree, ElEmpty } from 'element-plus';

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

const treeProps = {
  children: 'children',
  label: 'title',
};

const fetchChapters = async () => {
  try {
    const response = await apiClient.get(`/courses/${props.courseId}/chapters/`);
    chapters.value = response.data;
  } catch (error) {
    console.error('获取章节列表失败:', error);
  }
};

const handleNodeClick = (node: any, data: Chapter) => {
  if (data.parent) { // 只有节可以点击
    router.push({ name: 'section-detail', params: { id: props.courseId, sectionId: data.id } });
  }
};

onMounted(() => {
  fetchChapters();
});
</script>

<style scoped>
.chapter-navigator {
  padding: 16px;
}
.navigator-title {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 1.1em;
  color: #333;
}
.chapter-tree {
  background-color: transparent;
}
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
}
.custom-tree-node:hover {
  background-color: #f5f7fa;
}
.custom-tree-node.is-active {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: bold;
}
</style>
