<script setup lang="ts">
import type { RaceItemBean, RaceViewBean } from "@/components/sector/race/RaceViewBean";
import {onMounted} from "vue";


const props = defineProps({
  foo: String
})




// 定义接收 RaceBean 的方法
const receiveRaceBean = (raceItemBean: RaceItemBean) => {
  console.log('接收到 RaceBean:', raceItemBean)
  // 在这里处理 RaceBean 数据
  // 例如：更新图表数据、开始动画等
}
// 使用 defineExpose 暴露方法给父组件
defineExpose({
  receiveRaceBean
})

onMounted(() => {
  console.log("RaceView onMounted")
})

</script>

<template>
<div>aaaaaaaaaaaaaaaa</div>
</template>

<style scoped>

</style>