<script setup lang="ts">

import NavigatorBar from "@/components/NavigatorBar.vue";
import RaceView from "@/components/sector/race/RaceView.vue";
import {onMounted, ref} from "vue";
import {RaceItemBean} from "@/components/sector/race/RaceViewBean";

const sectorRaceView = ref<InstanceType<typeof RaceView> | null>(null)

function startAction() {
  console.log("startAction");
  // 创建 RaceItemBean 对象
  const raceItemBean: RaceItemBean = {
    name: "示例名称" // 根据实际需求设置值
  };
  // 调用 RaceView 组件的 addPairs 方法，传入 RaceItemBean
  sectorRaceView.value?.addPairs(raceItemBean);
}

function prepareRaceViewSeries() {
  // 获取x个板块，获取策略TODO，必须要有银行，券商作为锚定，或者以上证指数，xx指数作为锚定

}

onMounted(() => {

})


function resetAction() {
  console.log("resetAction");
}

</script>

<template>
  <navigator-bar></navigator-bar>
  <RaceView ref="sectorRaceView"></RaceView>
  <div>
    <a-button type="primary" @click="startAction">开始</a-button>
    <a-button @click="resetAction">重置</a-button>
  </div>
</template>

<style scoped>

</style>