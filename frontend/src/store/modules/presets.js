import Vue from 'vue';

const state = () => ({
  presets: {},
});

const mutations = {
  presets_config(state, config) {
    Vue.set(state, 'presets', config.presets);
  },
};

export default {
  mutations,
  state,
};
