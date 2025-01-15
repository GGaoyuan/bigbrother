<script setup lang="ts">
import { ref } from 'vue';
import 'vue-good-table/dist/vue-good-table.css'



// 定义表格的列配置
const columns = ref([
  {
    label: 'Name',
    field: 'name',
  },
  {
    label: 'Age',
    field: 'age',
    type: 'number',
  },
  {
    label: 'Created On',
    field: 'createdAt',
    type: 'date',
    dateInputFormat: 'yyyy-MM-dd',
    dateOutputFormat: 'MMM do yy',
  },
  {
    label: 'Percent',
    field: 'score',
    type: 'percentage',
  },
]);

// 定义表格的数据
const rows = ref([
  { id: 1, name: 'John', age: 20, createdAt: '', score: 0.03343 },
  { id: 2, name: 'Jane', age: 24, createdAt: '2011-10-31', score: 0.03343 },
  { id: 3, name: 'Susan', age: 16, createdAt: '2011-10-30', score: 0.03343 },
  { id: 4, name: 'Chris', age: 55, createdAt: '2011-10-11', score: 0.03343 },
  { id: 5, name: 'Dan', age: 40, createdAt: '2011-10-21', score: 0.03343 },
  { id: 6, name: 'John', age: 20, createdAt: '2011-10-31', score: 0.03343 },
]);
</script>

<template>
  <!-- 三个可滚动的 div -->
  <vue-good-table class="box"
      :columns="columns"
      :rows="rows">
  </vue-good-table>
<!--  <div class="box box1">Div 1 (600px)</div>-->
<!--  <div class="box box2">Div 2 (500px)</div>-->
<!--  <div class="box box3">Div 3 (400px)</div>-->
</template>

<style scoped>

/* 确保页面的 body 允许滚动 */
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow-y: auto;
}
/* 给每个 div 设置高度并添加样式 */
.box {
  width: 100%; /* 全屏宽度 */
}
.box1 {
  height: 600px;
  background-color: lightblue;
}
.box2 {
  height: 500px;
  background-color: lightgreen;
}
.box3 {
  height: 400px;
  background-color: lightcoral;
}
</style>