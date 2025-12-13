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
    // 检查是否是401错误且不是因为刷新token本身失败
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // 标记为已重试
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

export default apiClient;
