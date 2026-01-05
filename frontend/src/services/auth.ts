import apiClient from './api';
import type { LoginCredentials, User } from '../types';

export const login = async (credentials: LoginCredentials): Promise<{ access: string; refresh: string }> => {
  const response = await apiClient.post('/users/token/', credentials);
  return response.data;
};

export const register = async (userData: User) => {
  const response = await apiClient.post('/users/register/', userData);
  return response.data;
};

export const getUserProfile = async (): Promise<User> => {
  const response = await apiClient.get('/users/profile/'); // 假设这是获取用户信息的端点
  return response.data;
};

import type { DirectPasswordResetPayload } from '../types';

export const directPasswordReset = async (payload: DirectPasswordResetPayload) => {
  const response = await apiClient.post('/auth/password/reset/direct/', payload);
  return response.data;
};
