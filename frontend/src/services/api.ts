import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api', // 使用 Vite 代理
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // 检查是否是401错误、不是重试请求，并且请求的URL不是登录URL
    if (error.response.status === 401 && !originalRequest._retry && originalRequest.url !== '/token/') {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/users/token/refresh/', {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', data.access);
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${data.access}`;
          originalRequest.headers['Authorization'] = `Bearer ${data.access}`;
          return apiClient(originalRequest); // 重新发送原始请求
        } catch (refreshError) {
          // 刷新token失败，清除本地存储并重定向到登录页
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user_role');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // 没有refresh token，直接重定向到登录
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// 获取当前用户信息
export const getProfile = () => {
  return apiClient.get('/users/profile/');
};

// 更新当前用户信息
export const updateProfile = (data: any) => {
  return apiClient.put('/users/profile/', data);
};

// 作业相关 API
export const getAssignment = (id: number) => apiClient.get(`/assignments/${id}/`);
export const createAssignment = (data: any) => apiClient.post('/assignments/', data);
export const updateAssignment = (id: number, data: any) => apiClient.put(`/assignments/${id}/`, data);
export const deleteAssignment = (id: number) => apiClient.delete(`/assignments/${id}/`);
export const getSubmissions = (assignmentId: number) => apiClient.get(`/submissions/?assignment=${assignmentId}`);
export const createSubmission = (data: any) => apiClient.post('/submissions/', data);
export const getSubmission = (id: number) => apiClient.get(`/submissions/${id}/`);
export const gradeSubmission = (id: number, data: any) => apiClient.post(`/submissions/${id}/grade/`, data);

// 考试相关 API
export const getExams = (courseId: number) => apiClient.get(`/exams/?course=${courseId}`);
export const getExam = (id: number) => apiClient.get(`/exams/${id}/`);
export const createExam = (data: any) => apiClient.post('/exams/', data);
export const updateExam = (id: number, data: any) => apiClient.put(`/exams/${id}/`, data);
export const deleteExam = (id: number) => apiClient.delete(`/exams/${id}/`);
export const startExam = (id: number) => apiClient.post(`/exams/${id}/start/`);
export const getExamSubmission = (id: number) => apiClient.get(`/exam-submissions/${id}/`);
export const getSubmissionsForExam = (examId: number) => apiClient.get(`/exams/${examId}/submissions/`);
export const submitExam = (id: number, data: any) => apiClient.post(`/exam-submissions/${id}/submit/`, data);
export const gradeExamSubmission = (id: number, data: any) => apiClient.post(`/exam-submissions/${id}/grade/`, data);

// 课程成员
export const getCourseMembers = (courseId: number) => apiClient.get(`/courses/${courseId}/members/`);

// 签到相关 API
export const getCheckins = (courseId: number) => apiClient.get(`/courses/${courseId}/checkins/`);
export const createCheckin = (courseId: number, data: { title: string }) => apiClient.post(`/courses/${courseId}/checkins/`, data);
export const getCheckinDetail = (courseId: number, checkinId: number) => apiClient.get(`/courses/${courseId}/checkins/${checkinId}/`);
export const endCheckin = (courseId: number, checkinId: number) => apiClient.post(`/courses/${courseId}/checkins/${checkinId}/end_checkin/`);
export const studentCheckin = (courseId: number, checkinId: number) => apiClient.post(`/courses/${courseId}/checkins/${checkinId}/student_checkin/`);
export const proxyCheckin = (courseId: number, checkinId: number, studentId: number) => apiClient.post(`/courses/${courseId}/checkins/${checkinId}/proxy_checkin/`, { student_id: studentId });


export default apiClient;
