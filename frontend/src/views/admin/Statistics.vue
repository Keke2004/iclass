<template>
  <div>
    <h1>用户数据统计</h1>
    <div ref="chart" style="width: 600px; height: 400px;"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import api from '@/services/api';

const chart = ref<HTMLElement | null>(null);

onMounted(async () => {
  if (chart.value) {
    const myChart = echarts.init(chart.value);
    try {
      const response = await api.get('/users/statistics/');
      const data = response.data;
      
      const chartData = Object.keys(data).map(key => ({
        name: key,
        value: data[key]
      }));

      const option = {
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
            data: chartData,
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
      myChart.setOption(option);
    } catch (error) {
      console.error('Failed to fetch user statistics:', error);
    }
  }
});
</script>

<style scoped>
h1 {
  margin-bottom: 20px;
}
</style>
