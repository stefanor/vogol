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
    dispatch('send_action', {type: 'voctomix', action});
  },

  voctomix_received_state({commit}, updated_state) {
    commit('voctomix_state_update', updated_state);
  },
};

export default {
  actions,
  mutations,
  state,
};
