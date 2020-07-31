import Vue from 'vue';

const state = () => ({
  preview_is_current: {},
  previews: {},
  update_interval: 2000,
});

const mutations = {
  preview_image(state, {source, img}) {
    Vue.set(state.previews, source, img);
    Vue.set(state.preview_is_current, source, true);
  },

  stale_preview(state, source) {
    Vue.set(state.preview_is_current, source, false);
  },
};

const actions = {
  update_preview({commit, dispatch, rootState}, source) {
    if (rootState.websocket.connection != 'connected') {
      commit('stale_preview', source);
      return;
    }
    fetch('/preview/' + source, {
      credentials: 'same-origin',
    })
      .then(response => {
        if (response.status == 403) {
          dispatch('logout');
        } else if (response.ok) {
          return response.blob();
        } else {
          commit('stale_preview', source);
        }
      })
      .then(img => {
        if (img) {
          commit('preview_image', {source, img});
        }
      })
      .catch(error => {
        commit(
          'error',
          'Failed to update preview for ' + source + ' got ' + error
        );
      });
  },
};

export default {
  actions,
  mutations,
  state,
};
