<template>
  <div class="random-question-picker">
    <div class="picker-display">
      <span :class="['student-name', { 'winner': animationFinished }]">
        {{ currentStudentName }}
      </span>
    </div>
    <div v-if="animationFinished" class="congrats-message">
      🎉 恭喜这位同学！ 🎉
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import type { User } from '@/types';

const props = defineProps<{
  students: User[];
  selectedStudent: User | null;
}>();

const emit = defineEmits(['finished']);

const currentStudentName = ref('');
const animationFinished = ref(false);
let pickerInterval: number | undefined;
let finishTimeout: number | undefined;

const startAnimation = () => {
  if (props.students.length === 0) {
    currentStudentName.value = '没有学生';
    animationFinished.value = true;
    setTimeout(() => emit('finished'), 2000);
    return;
  }

  animationFinished.value = false;
  pickerInterval = window.setInterval(() => {
    const randomIndex = Math.floor(Math.random() * props.students.length);
    currentStudentName.value = props.students[randomIndex].username;
  }, 100); // Switch names every 100ms

  finishTimeout = window.setTimeout(() => {
    clearInterval(pickerInterval);
    if (props.selectedStudent) {
      currentStudentName.value = props.selectedStudent.username;
    }
    animationFinished.value = true;
    setTimeout(() => emit('finished'), 2000); // Wait 2 seconds before closing
  }, 5000); // Stop after 5 seconds
};

watch(() => props.selectedStudent, (newVal) => {
  if (newVal) {
    startAnimation();
  }
});

onMounted(() => {
  if (props.selectedStudent) {
    startAnimation();
  }
});

onUnmounted(() => {
  clearInterval(pickerInterval);
  clearTimeout(finishTimeout);
});
</script>

<style scoped>
.random-question-picker {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 250px;
  text-align: center;
}

.picker-display {
  font-size: 48px;
  font-weight: bold;
  color: #333;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.student-name {
  transition: all 0.3s ease-in-out;
}

.student-name.winner {
  color: #f56c6c; /* Highlight color for the winner */
  transform: scale(1.2);
  text-shadow: 0 0 10px rgba(245, 108, 108, 0.5);
}

.congrats-message {
  margin-top: 20px;
  font-size: 20px;
  color: #67c23a;
}
</style>
