<script setup lang="ts">
import type { RaceItemBean, RaceViewBean } from "@/components/sector/race/RaceViewBean";
import {onMounted} from "vue";


function addPairs(raceItemBean: RaceItemBean) {
  console.log("addPairs 方法被调用", raceItemBean);
  // 在这里实现 addPairs 的逻辑
}

// 使用 defineExpose 暴露方法给父组件
defineExpose({
  addPairs
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