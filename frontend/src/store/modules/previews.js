import Vue from 'vue';

const state = () => ({
  preview_is_current: {},
  previews: {},
  pollers: {},
  preview_update_interval: 2000,
});

const mutations = {
  add_poller(state, {source, poller}) {
    Vue.set(state.pollers, source, poller);
  },

  remove_poller(state, source) {
    Vue.delete(state.pollers, source);
  },

  preview_image(state, {source, img}) {
    Vue.set(state.previews, source, img);
    Vue.set(state.preview_is_current, source, true);
  },

  stale_preview(state, source) {
    Vue.set(state.preview_is_current, source, false);
  },
};

const actions = {
  start_poller({commit, dispatch, state}, source) {
    if (source in state.pollers) {
      return;
    }
    const poller = window.setInterval(
      () => dispatch('update_preview', source),
      state.preview_update_interval
    );
    commit('add_poller', {source, poller});
  },

  stop_poller({commit, state}, source) {
    const poller = state.pollers[source];
    clearInterval(poller);
    commit('remove_poller', source);
  },

  stop_polling({dispatch, state}) {
    for (const source of Object.keys(state.pollers)) {
      dispatch('stop_poller', source);
    }
  },

  update_preview({commit, dispatch}, source) {
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
