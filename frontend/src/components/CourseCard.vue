<template>
  <el-card class="course-card" shadow="hover" :body-style="{ padding: '0px' }">
    <div class="card-image">
      <el-image
        :src="course.cover || 'https://images.unsplash.com/photo-1516979187457-637abb4f9353?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=870&q=80'"
        fit="cover"
      />
    </div>
    <div class="card-content">
      <h3 class="course-name">{{ course.name }}</h3>
      <p class="teacher-name">{{ course.teacher?.username || '未知教师' }}</p>
      <div class="card-footer">
        <slot name="actions"></slot>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

// 这里的接口定义需要与父组件传递的数据保持一致
interface Teacher {
  id: number;
  username: string;
  role: string;
}

interface Course {
  id: number;
  name: string;
  description: string;
  teacher: Teacher;
  cover?: string; // 封面图片是可选的
}

defineProps<{
  course: Course;
}>();
</script>

<style scoped>
.course-card {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  margin-bottom: 20px;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.card-image .el-image {
  width: 100%;
  height: 150px;
  display: block;
}

.card-content {
  padding: 16px;
}

.course-name {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #303133;
}

.teacher-name {
  font-size: 14px;
  color: #909399;
  margin: 0 0 16px;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
</style>
