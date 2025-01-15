// import { createApp } from 'vue'
// import App from './App.vue'
//
// createApp(App).mount('#app')



import { createApp } from 'vue';
import Antd from 'ant-design-vue';
// import VueGoodTablePlugin from 'vue-good-table';
// import 'vue-good-table/dist/vue-good-table.css';
// Vue.use(VueGoodTablePlugin);

import App from './App.vue'
import './style.css'
import router from './router'

const app = createApp(App);

app.use(Antd).use(router).mount('#app');
