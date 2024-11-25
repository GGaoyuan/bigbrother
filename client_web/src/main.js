// import { createApp } from 'vue'
// import App from './App.vue'
//
// createApp(App).mount('#app')



import { createApp } from 'vue';
import Antd from 'ant-design-vue';
import App from './App.vue'
import './style.css'
import router from './router'

const app = createApp(App);

app.use(Antd).use(router).mount('#app');
