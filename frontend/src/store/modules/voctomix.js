const state = () => ({
  audio: [],
  composite_mode: null,
  connected: false,
  sources: [],
  stream_status: null,
  video_a: null,
  video_b: null,
});

const mutations = {
  voctomix_state_update(state, incoming) {
    Object.assign(state, incoming);
  },
};

const actions = {
  voctomix_action({dispatch}, action) {
    dispatch('send_action', {voctomix: action});
  },

  voctomix_received_state({dispatch, commit, state}, updated_state) {
    if (updated_state.sources != state.sources) {
      dispatch('stop_polling');
      dispatch('start_polling');
    }
    commit('voctomix_state_update', updated_state);
  },
};

export default {
  actions,
  mutations,
  state,
};
