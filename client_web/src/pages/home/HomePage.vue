<script setup>
import {reactive, ref, watch, h, provide, inject} from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { MailOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons-vue';
const selectedKeys = ref(['1']);
const openKeys = ref(['sub1']);

function getItem(label, key, icon, children, type) {
  return {
    key,
    icon,
    children,
    label,
    type,
  };
}
const items = reactive([
  getItem('Navigation Oneaaaaaa', 'sub1', () => h(MailOutlined), [
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
  },
  getItem('Navigation Three', 'sub4', () => h(SettingOutlined), [
    getItem('Option 9', '9'),
    getItem('Option 10', '10'),
    getItem('Option 11', '11'),
    getItem('Option 12', '12'),
  ]),
  getItem('Navigation Three', 'sub4', () => h(SettingOutlined), [
    getItem('Option 9', '9'),
    getItem('Option 10', '10'),
    getItem('Option 11', '11'),
    getItem('Option 12', '12'),
  ]),
  getItem('Navigation Three', 'sub4', () => h(SettingOutlined), [
    getItem('Option 9', '9'),
    getItem('Option 10', '10'),
    getItem('Option 11', '11'),
    getItem('Option 12', '12'),
  ]),
  getItem('Navigation Three', 'sub4', () => h(SettingOutlined), [
    getItem('Option 9', '9'),
    getItem('Option 10', '10'),
    getItem('Option 11', '11'),
    getItem('Option 12', '12'),
  ]),
  getItem('Group', 'grp', null, [getItem('Option 13', '13'), getItem('Option 14', '14')], 'group'),
]);
const router = useRouter();
const route = useRoute();
const handleClick = e => {
  router.push({ path: '/heatmap' });
  console.log('click', e);
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
  /*overflow-y: auto;  如果内容超出，显示滚动条 */
}

</style>