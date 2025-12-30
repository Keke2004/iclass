<template>
  <div class="courses-container">
    <div class="toolbar">
      <el-input v-model="searchQuery" placeholder="搜索课程" class="search-input" clearable @clear="fetchCourses" @keyup.enter="fetchCourses" />
      <el-button type="primary" @click="openCreateDialog">创建新课程</el-button>
    </div>

    <div v-if="loading" class="loading-state">
      <p>正在加载课程...</p>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>

    <el-row :gutter="20" v-else-if="courses.length > 0">
      <el-col :span="8" v-for="course in courses" :key="course.id">
        <CourseCard :course="course" @click="navigateToCourseDetail(course.id)">
          <template #actions>
            <el-button type="primary" link @click.stop="openEditDialog(course)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这门课程吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm.stop="deleteCourse(course.id)"
            >
              <template #reference>
                <el-button type="danger" link @click.stop>删除</el-button>
              </template>
            </el-popconfirm>
            <el-button type="info" link @click.stop="navigateToCourseDetail(course.id)">学生</el-button>
          </template>
        </CourseCard>
      </el-col>
    </el-row>
    <div v-else class="empty-state">
      <p>暂无课程，快去创建一门吧！</p>
    </div>

    <!-- 创建/编辑课程弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEditMode ? '编辑课程' : '创建新课程'" width="500px" @closed="handleDialogClosed">
      <CourseForm ref="courseFormRef" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleFormSubmit" :loading="formSubmitting">
            {{ isEditMode ? '保存' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../services/api';
import CourseCard from '../../components/CourseCard.vue';
import CourseForm from '../../components/CourseForm.vue';
import { ElMessage, ElPopconfirm } from 'element-plus';

interface Teacher {
  id: number;
  username: string;
  role: string;
}

interface Course {
  id: number;
  name: string;
  teacher: Teacher;
  cover?: string;
}

const router = useRouter();
const courses = ref<Course[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const searchQuery = ref('');

const dialogVisible = ref(false);
const isEditMode = ref(false);
const formSubmitting = ref(false);
const courseFormRef = ref<InstanceType<typeof CourseForm> | null>(null);
const editingCourse = ref<Course | null>(null);

const fetchCourses = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/courses/', {
      params: { search: searchQuery.value },
    });
    courses.value = response.data;
  } catch (err) {
    error.value = '无法加载课程列表，请稍后重试。';
  } finally {
    loading.value = false;
  }
};

const openCreateDialog = () => {
  isEditMode.value = false;
  editingCourse.value = null;
  dialogVisible.value = true;
};

const openEditDialog = (course: Course) => {
  isEditMode.value = true;
  editingCourse.value = course;
  dialogVisible.value = true;
  // nextTick is needed to ensure the form is rendered
  nextTick(() => {
    if (courseFormRef.value) {
      // Manually set form data for editing
      courseFormRef.value.form.name = course.name;
    }
  });
};

const handleDialogClosed = () => {
  if (courseFormRef.value) {
    courseFormRef.value.reset();
  }
};

const handleFormSubmit = async () => {
  if (!courseFormRef.value) return;

  formSubmitting.value = true;
  try {
    if (isEditMode.value && editingCourse.value) {
      // Update existing course
      await apiClient.patch(`/courses/${editingCourse.value.id}/`, courseFormRef.value.form);
      ElMessage.success('课程更新成功！');
    } else {
      // Create new course
      await courseFormRef.value.submit();
      ElMessage.success('课程创建成功！');
    }
    dialogVisible.value = false;
    fetchCourses(); // Refresh the course list
  } catch (err) {
    ElMessage.error(isEditMode.value ? '更新失败，请重试' : '创建失败，请重试');
  } finally {
    formSubmitting.value = false;
  }
};

const deleteCourse = async (courseId: number) => {
  try {
    await apiClient.delete(`/courses/${courseId}/`);
    ElMessage.success('课程删除成功');
    fetchCourses(); // Refresh list after deletion
  } catch (err) {
    ElMessage.error('删除失败，请稍后重试。');
  }
};

const navigateToCourseDetail = (courseId: number) => {
  router.push({ name: 'course-detail', params: { id: courseId } });
};

onMounted(fetchCourses);
</script>

<style scoped>
.courses-container {
  padding: 20px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}
.search-input {
  max-width: 300px;
}
.loading-state, .error-state, .empty-state {
  text-align: center;
  color: #909399;
  padding: 40px;
}
</style>
