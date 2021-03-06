import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import Vue from 'vue';

import Vogol from './Vogol.vue';
import store from './store';

Vue.config.productionTip = false;

new Vue({
  store,
  render: h => h(Vogol),
}).$mount('#app');
