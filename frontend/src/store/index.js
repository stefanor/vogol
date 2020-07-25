import Vue from 'vue';
import Vuex from 'vuex';

import actions from './actions.js';
import mutations from './mutations.js';

Vue.use(Vuex);

const state = () => ({
  // From Backend
  audio: [],
  composite_mode: null,
  connected: false,
  stream_status: null,
  sources: [],
  video_a: null,
  video_b: null,

  // FE-only
  error: null,
  last_update: null,
  logged_in: true,
  pollers: [],
  previews: {},
  preview_is_current: {},
  preview_update_interval: 2000,
  state_update_interval: 5000,
  /*
  audio: {grabber: 0.15, jitsi: 0.8},
  composite_mode: 'fullscreen',
  error: null,
  logged_in: true,
  last_update: new Date(),
  pollers: [],
  previews: [],
  preview_update_interval: 2000,
  state_update_interval: 5000,
  stream_status: 'blank',
  sources: ['grabber', 'jitsi'],
  video_a: 'grabber',
  video_b: 'jitsi',
  */
});

export default new Vuex.Store({
  state,
  mutations,
  actions,
  strict: process.env.NODE_ENV !== 'production',
});
