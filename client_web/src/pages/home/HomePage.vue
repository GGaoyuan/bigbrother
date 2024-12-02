<script setup>
import {reactive, ref, watch, h, provide, inject} from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { MailOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons-vue';
const selectedKeys = ref(['9']);
const openKeys = ref(['sub4']);

function getItem(label, key, icon, children, type, url) {
  return {
    key,
    icon,
    children,
    label,
    type,
    url,
  };
}
const items = reactive([
  getItem('Navigation One', 'sub1', () => h(MailOutlined), [
    getItem('Item 1', 'g1', null, [getItem('Option 1', '1'), getItem('Option 2', '2')], 'group'),
    getItem('Item 2', 'g2', null, [getItem('Option 3', '3'), getItem('Option 4', '4')], 'group'),
  ]),
  getItem('Navigation Two', 'sub2', () => h(AppstoreOutlined), [
    getItem('Option 5', '5'),
    getItem('Option 6', '6'),
    getItem('Submenu', 'sub3', null, [getItem('Option 7', '7'), getItem('Option 8', '8')]),
  ]),
  {
    type: 'divider',
  }
]);
const router = useRouter();
router.push({ path: '/heatmap' });

const route = useRoute();
const handleClick = e => {

  console.log('click', e);
  if (e.key === '1') {
    router.push({ path: '/heatmap' });
  } else {

    router.push({ path: '/candle' });
  }
};
watch(openKeys, val => {
  console.log('openKeys', val);
});
</script>


<template>
  <div class="container">
    <div class="menu">
      <a-menu
          id="dddddd"
          v-model:openKeys="openKeys"
          v-model:selectedKeys="selectedKeys"
          mode="inline"
          :items="items"
          @click="handleClick"
      ></a-menu>
    </div>


    <div class="content">
      <RouterView></RouterView>
    </div>
  </div>
</template>


<style scoped>
.container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.content {
  flex-grow: 1;
  background-color: #99FF22;
  overflow-y: auto;
}

</style>