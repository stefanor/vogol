import {BootstrapVue, BootstrapVueIcons} from 'bootstrap-vue';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import Vue from 'vue';

import VoctoWeb from './VoctoWeb.vue';
import store from './store';

Vue.config.productionTip = false;

Vue.use(BootstrapVue);
Vue.use(BootstrapVueIcons);

new Vue({
  store,
  render: h => h(VoctoWeb),
}).$mount('#app');
