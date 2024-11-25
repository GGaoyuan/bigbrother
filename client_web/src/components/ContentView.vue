<script setup>
import {inject, ref} from "vue";
  var page = ref(null)
  const message = inject('vertical_menu_click');
  console.log(message)
  console.log("vertical_menu_click log")
</script>

<template>
  <body class="body_area">
  </body>
</template>

<style scoped>
.body_area{
  background-color: #646c88;
}

</style>