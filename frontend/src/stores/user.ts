import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { getUserProfile } from '@/services/auth';
import type { User } from '@/types';

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null);

  const isAuthenticated = computed(() => !!user.value);
  const isStudent = computed(() => user.value?.role === 'student');
  const isTeacher = computed(() => user.value?.role === 'teacher');
  const isAdmin = computed(() => user.value?.role === 'admin');

  const fetchUser = async () => {
    if (user.value) {
      return;
    }
    try {
      const userData = await getUserProfile();
      user.value = userData;
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      user.value = null;
    }
  };

  const logout = () => {
    // Clear all authentication-related data from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');

    // Force a full page reload to the login page to clear all state
    window.location.href = '/login';
  };

  return {
    user,
    isAuthenticated,
    isStudent,
    isTeacher,
    isAdmin,
    fetchUser,
    logout,
  };
});
