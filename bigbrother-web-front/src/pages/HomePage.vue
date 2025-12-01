<script setup lang="ts">

import NavigatorBar from "@/components/NavigatorBar.vue";
import RaceView from "@/components/sector/race/RaceView.vue";
import {ref} from "vue";
import {RaceItemBean} from "@/components/sector/race/RaceViewBean";

const raceView = ref<InstanceType<typeof RaceView> | null>(null)

function startAction() {
  raceView.value?.receiveRaceBean = {
    name: "test" // 根据实际需求设置值
  }
  console.log("startAction");
}


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