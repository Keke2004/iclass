<template>
  <div v-if="show" class="dialog-overlay" @click.self="handleCancel">
    <div class="dialog-box">
      <h3 class="dialog-title">{{ title }}</h3>
      <p class="dialog-message">{{ message }}</p>
      <div class="dialog-actions">
        <button @click="handleCancel" class="btn btn-cancel">取消</button>
        <button @click="handleConfirm" class="btn btn-confirm">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean;
  title: string;
  message: string;
}>();

const emit = defineEmits(['confirm', 'cancel']);

const handleConfirm = () => {
  emit('confirm');
};

const handleCancel = () => {
  emit('cancel');
};
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-box {
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 400px;
  text-align: center;
}

.dialog-title {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  color: #333;
}

.dialog-message {
  margin-bottom: 2rem;
  font-size: 1.1rem;
  color: #555;
}

.dialog-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.btn {
  border: none;
  padding: 0.7rem 1.5rem;
  font-size: 1rem;
  font-weight: bold;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn-confirm {
  background-color: #1976d2;
  color: white;
}

.btn-confirm:hover {
  background-color: #1565c0;
}

.btn-cancel {
  background-color: #f0f0f0;
  color: #555;
  border: 1px solid #ccc;
}

.btn-cancel:hover {
  background-color: #e0e0e0;
}
</style>
