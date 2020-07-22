import Vue from 'vue';

export default {
  add_poller(state, poller) {
    state.pollers.push(poller);
  },

  clear_pollers(state) {
    state.pollers = [];
  },

  error(state, error) {
    console.log(error);
    state.error = error;
  },

  logout(state) {
    state.logged_in = false;
  },

  preview_image(state, {source, img}) {
    Vue.set(state.previews, source, img);
    Vue.set(state.preview_is_current, source, true);
  },

  stale_preview(state, source) {
    Vue.set(state.preview_is_current, source, false);
  },

  received_state(state, incoming) {
    Object.assign(state, incoming);
    state.last_update = new Date();
  },
};
