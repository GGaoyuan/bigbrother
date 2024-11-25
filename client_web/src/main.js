// import { createApp } from 'vue'
// import './style.css'
// import App from './App.vue'
//
// createApp(App).mount('#app')



import { createApp } from 'vue';
import Antd from 'ant-design-vue';
import './style.css'
import App from './App.vue'

const app = createApp(App);

app.use(Antd).mount('#app');
