import Vue from 'vue';
import Vuex from 'vuex';

import previews from './modules/previews';
import ui from './modules/ui';
import voctomix from './modules/voctomix';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    previews,
    ui,
    voctomix,
  },
  strict: process.env.NODE_ENV !== 'production',
});
