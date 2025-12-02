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

// 获取当前用户信息
export const getProfile = () => {
  return apiClient.get('/users/profile/');
};

// 更新当前用户信息
export const updateProfile = (data: any) => {
  return apiClient.put('/users/profile/', data);
};

export default apiClient;
