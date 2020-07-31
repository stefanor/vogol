import Vue from 'vue';
import Vuex from 'vuex';

import playback from './modules/playback';
import previews from './modules/previews';
import voctomix from './modules/voctomix';
import websocket from './modules/websocket';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    playback,
    previews,
    voctomix,
    websocket,
  },
  strict: process.env.NODE_ENV !== 'production',
});
