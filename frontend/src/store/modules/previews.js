import Vue from 'vue';

const state = () => ({
  audio_levels: {},
  preview_is_current: {},
  previews: {},
  update_interval: 2000,
});

const mutations = {
  preview_audio_level(state, {source, rms, peak, decay}) {
    Vue.set(state.audio_levels, source, {rms, peak, decay});
  },

  preview_image(state, {source, img}) {
    Vue.set(state.previews, source, img);
    Vue.set(state.preview_is_current, source, true);
  },

  stale_preview(state, source) {
    Vue.set(state.preview_is_current, source, false);
  },
};

export default {
  mutations,
  state,
};
