<template>
  <div class="statistics-container">
    <h1>数据统计</h1>
    <div class="content-wrapper">
      <div class="chart-container">
        <div ref="userChart" style="width: 100%; height: 400px;"></div>
      </div>
      <div class="chart-container">
        <div ref="logChart" style="width: 100%; height: 400px;"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import api from '@/services/api';

const userChart = ref<HTMLElement | null>(null);
const logChart = ref<HTMLElement | null>(null);

onMounted(async () => {
  // 初始化用户角色分布图
  if (userChart.value) {
    const myUserChart = echarts.init(userChart.value);
    try {
      const response = await api.get('/users/statistics/');
      const data = response.data;
      
      const userChartData = Object.keys(data).map(key => ({
        name: key,
        value: data[key]
      }));

      const userOption = {
        title: {
          text: '用户角色分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            name: '角色',
            type: 'pie',
            radius: '50%',
            data: userChartData,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
      myUserChart.setOption(userOption);
    } catch (error) {
      console.error('Failed to fetch user statistics:', error);
    }
  }

  // 初始化日志级别分布图
  if (logChart.value) {
    const myLogChart = echarts.init(logChart.value);
    try {
      const response = await api.get('/logs/statistics/');
      const data = response.data;
      
      const logChartData = Object.keys(data).map(key => ({
        name: key,
        value: data[key]
      }));

      const logOption = {
        color: ['#67C23A', '#E6A23C', '#F56C6C'],
        title: {
          text: '日志级别分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            name: '级别',
            type: 'pie',
            radius: '50%',
            data: logChartData,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
      myLogChart.setOption(logOption);
    } catch (error) {
      console.error('Failed to fetch log statistics:', error);
    }
  }
});
</script>

<style scoped>
.statistics-container {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  height: calc(100vh - 120px);
  max-width: 1400px;
  margin: 0 auto;
  width: 95%;
}

h1 {
  margin-bottom: 20px;
  flex-shrink: 0;
}

.content-wrapper {
  flex-grow: 1;
  overflow-y: auto;
}

.chart-container {
  margin-bottom: 30px;
  height: 400px; /* Ensure the container has a fixed height */
}
</style>
