<template>
  <div class="course-list-container">
    <div class="header">
      <h1>我的课程</h1>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索课程"
          clearable
          style="width: 240px; margin-right: 10px;"
        ></el-input>
        <el-button type="primary" @click="goToCreateCourse">创建新课程</el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <p>正在加载课程...</p>
    </div>

    <div v-else-if="filteredCourses.length === 0" class="empty-state">
      <p>没有找到匹配的课程。</p>
    </div>

    <el-row :gutter="20" v-else>
      <el-col :span="8" v-for="course in filteredCourses" :key="course.id">
        <el-card class="course-card">
          <template #header>
            <div class="card-header">
              <span>{{ course.name }}</span>
            </div>
          </template>
          <p class="course-description">{{ course.description }}</p>
          <div class="card-footer">
            <el-button type="primary" link @click="navigateToCourse(course.id)">进入课程</el-button>
            <el-button type="primary" link @click="openEditDialog(course)">编辑课程</el-button>
            <el-button type="danger" link @click="deleteCourse(course.id)">删除</el-button>
            <el-button type="primary" link @click="openStudentManager(course)">管理学生</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑课程对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑课程" width="50%">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="editForm.name"></el-input>
        </el-form-item>
        <el-form-item label="课程描述" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="4"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEditForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 学生管理对话框 -->
    <el-dialog v-model="studentManagerVisible" title="管理学生" width="50%">
      <div v-if="currentCourse">
        <h3>已选学生</h3>
        <el-tag
          v-for="student in enrolledStudentDetails"
          :key="student.id"
          closable
          @close="removeStudent(student.id)"
          style="margin-right: 5px;"
        >
          {{ student.username }}
        </el-tag>
        <el-divider />
        <h3>添加新学生</h3>
        <el-select
          v-model="selectedStudent"
          filterable
          placeholder="搜索并选择学生"
          @change="addStudent"
        >
          <el-option
            v-for="student in availableStudents"
            :key="student.id"
            :label="student.username"
            :value="student.id"
          />
        </el-select>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="studentManagerVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../../services/api';
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus';

const router = useRouter();

interface Student {
  id: number;
  username: string;
}

interface Course {
  id: number;
  name: string;
  description: string;
  students: number[];
}

const courses = ref<Course[]>([]);
const allStudents = ref<Student[]>([]);
const loading = ref(true);
const studentManagerVisible = ref(false);
const editDialogVisible = ref(false);
const currentCourse = ref<Course | null>(null);
const selectedStudent = ref<number | null>(null);
const searchQuery = ref('');

const editFormRef = ref<FormInstance>();
const editForm = reactive({
  id: null as number | null,
  name: '',
  description: '',
});

const editRules = reactive<FormRules>({
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入课程描述', trigger: 'blur' }],
});

const filteredCourses = computed(() => {
  if (!searchQuery.value) {
    return courses.value;
  }
  const query = searchQuery.value.toLowerCase();
  return courses.value.filter(course =>
    course.name.toLowerCase().includes(query) ||
    course.description.toLowerCase().includes(query)
  );
});

const enrolledStudentDetails = computed(() => {
  if (!currentCourse.value) return [];
  const studentMap = new Map(allStudents.value.map(s => [s.id, s]));
  return currentCourse.value.students.map(id => studentMap.get(id)).filter(s => s) as Student[];
});

const availableStudents = computed(() => {
  if (!currentCourse.value) return [];
  const enrolledStudentIds = new Set(currentCourse.value.students);
  return allStudents.value.filter(s => !enrolledStudentIds.has(s.id));
});

const fetchCourses = async () => {
  try {
    const response = await apiClient.get('/courses/');
    courses.value = response.data;
  } catch (error) {
    console.error('获取课程列表失败:', error);
    ElMessage.error('无法加载课程列表，请稍后重试。');
  }
};

const fetchAllStudents = async () => {
  try {
    // 假设有一个 /api/users/students/ 的端点来获取所有学生
    const response = await apiClient.get('/users/?role=student');
    allStudents.value = response.data.results;
  } catch (error) {
    console.error('获取学生列表失败:', error);
    ElMessage.error('无法加载学生列表。');
  }
};

const goToCreateCourse = () => {
  router.push({ name: 'teacher-create-course' });
};

const navigateToCourse = (courseId: number) => {
  router.push({ name: 'course-detail', params: { id: courseId } });
};

const openEditDialog = (course: Course) => {
  editForm.id = course.id;
  editForm.name = course.name;
  editForm.description = course.description;
  editDialogVisible.value = true;
};

const submitEditForm = async () => {
  if (!editFormRef.value) return;
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await apiClient.put(`/courses/${editForm.id}/`, {
          name: editForm.name,
          description: editForm.description,
        });
        ElMessage.success('课程更新成功！');
        editDialogVisible.value = false;
        await fetchCourses(); // 重新获取课程列表
      } catch (error) {
        console.error('更新课程失败:', error);
        ElMessage.error('课程更新失败，请稍后重试。');
      }
    }
  });
};

const openStudentManager = (course: Course) => {
  currentCourse.value = course;
  studentManagerVisible.value = true;
};

const addStudent = async () => {
  if (!currentCourse.value || !selectedStudent.value) return;
  const studentIdToAdd = selectedStudent.value; // 保存ID
  try {
    await apiClient.post(`/courses/${currentCourse.value.id}/add_student/`, {
      student_id: studentIdToAdd,
    });
    ElMessage.success('学生添加成功！');

    // 直接在前端更新数据
    if (currentCourse.value) {
      currentCourse.value.students.push(studentIdToAdd);
    }

    selectedStudent.value = null; // 重置选择
  } catch (error) {
    console.error('添加学生失败:', error);
    ElMessage.error('添加学生失败。');
  }
};

const removeStudent = async (studentId: number) => {
  if (!currentCourse.value) return;
  try {
    await apiClient.post(`/courses/${currentCourse.value.id}/remove_student/`, {
      student_id: studentId,
    });
    ElMessage.success('学生移除成功！');

    // 直接在前端更新数据
    if (currentCourse.value) {
      const index = currentCourse.value.students.indexOf(studentId);
      if (index > -1) {
        currentCourse.value.students.splice(index, 1);
      }
    }
  } catch (error) {
    console.error('移除学生失败:', error);
    ElMessage.error('移除学生失败。');
  }
};

const deleteCourse = async (courseId: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这门课程吗？此操作不可撤销。',
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    await apiClient.delete(`/courses/${courseId}/`);
    ElMessage.success('课程删除成功！');
    await fetchCourses(); // 重新获取课程列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除课程失败:', error);
      ElMessage.error('课程删除失败，请稍后重试。');
    }
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await Promise.all([fetchCourses(), fetchAllStudents()]);
  } catch (error) {
    // 错误已在各自函数中处理
    console.error("加载初始数据失败:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.course-list-container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-actions {
  display: flex;
  align-items: center;
}
.course-card {
  margin-bottom: 20px;
}
.card-header {
  font-weight: bold;
}
.course-description {
  color: #606266;
  font-size: 14px;
  min-height: 60px;
}
.card-footer {
  text-align: right;
  margin-top: 10px;
}
.loading-state, .empty-state {
  text-align: center;
  color: #909399;
  padding: 40px;
}
</style>
