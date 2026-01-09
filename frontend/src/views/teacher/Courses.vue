<template>
  <div class="course-list-container">
    <div class="header">
      <h1>课程列表</h1>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索课程"
          clearable
          style="width: 240px; margin-right: 10px;"
        ></el-input>
        <el-button type="primary" @click="openCreateDialog">创建新课程</el-button>
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
        <course-card :course="course" @click="navigateToCourse(course.id)">
          <template #actions>
            <el-button type="primary" link @click.stop="openEditDialog(course)">编辑</el-button>
            <el-button type="danger" link @click.stop="deleteCourse(course.id)">删除</el-button>
            <el-button type="primary" link @click.stop="openStudentManager(course)">学生</el-button>
          </template>
        </course-card>
      </el-col>
    </el-row>

    <!-- 编辑课程对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑课程" width="50%">
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="editForm.name"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEditForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 创建课程对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建新课程" width="50%">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入课程名称"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCreateForm">创建</el-button>
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
import CourseCard from '../../components/CourseCard.vue';

const router = useRouter();

interface Student {
  id: number;
  username: string;
}

interface Teacher {
  id: number;
  username: string;
  role: string;
}

interface Course {
  id: number;
  name: string;
  teacher: Teacher;
  students: number[];
  cover?: string;
}

const courses = ref<Course[]>([]);
const allStudents = ref<Student[]>([]);
const loading = ref(true);
const studentManagerVisible = ref(false);
const editDialogVisible = ref(false);
const createDialogVisible = ref(false);
const currentCourse = ref<Course | null>(null);
const selectedStudent = ref<number | null>(null);
const searchQuery = ref('');

const editFormRef = ref<FormInstance>();
const editForm = reactive({
  id: null as number | null,
  name: '',
});

const editRules = reactive<FormRules>({
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
});

const createFormRef = ref<FormInstance>();
const createForm = reactive({
  name: '',
});

const createRules = reactive<FormRules>({
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
});

const filteredCourses = computed(() => {
  if (!searchQuery.value) {
    return courses.value;
  }
  const query = searchQuery.value.toLowerCase();
  return courses.value.filter(course =>
    course.name.toLowerCase().includes(query)
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

const openCreateDialog = () => {
  createDialogVisible.value = true;
};

const submitCreateForm = async () => {
  if (!createFormRef.value) return;
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await apiClient.post('/courses/', createForm);
        ElMessage.success('课程创建成功！');
        createDialogVisible.value = false;
        createFormRef.value?.resetFields();
        await fetchCourses(); // 重新获取课程列表
      } catch (error) {
        console.error('创建课程失败:', error);
        ElMessage.error('课程创建失败，请稍后重试。');
      }
    }
  });
};

const navigateToCourse = (courseId: number) => {
  router.push({ name: 'course-detail', params: { id: courseId } });
};

const openEditDialog = (course: Course) => {
  editForm.id = course.id;
  editForm.name = course.name;
  editDialogVisible.value = true;
};

const submitEditForm = async () => {
  if (!editFormRef.value) return;
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await apiClient.put(`/courses/${editForm.id}/`, {
          name: editForm.name,
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
.loading-state, .empty-state {
  text-align: center;
  color: #909399;
  padding: 40px;
}
</style>
