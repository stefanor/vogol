import Vue from 'vue';
import Vuex from 'vuex';

import auth from './modules/auth';
import errors from './modules/errors';
import playback from './modules/playback';
import presets from './modules/presets';
import previews from './modules/previews';
import users from './modules/users';
import voctomix from './modules/voctomix';
import websocket from './modules/websocket';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    auth,
    errors,
    playback,
    presets,
    previews,
    users,
    voctomix,
    websocket,
  },
  strict: process.env.NODE_ENV !== 'production',
});
