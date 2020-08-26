const state = () => ({
  audio: [],
  composite_mode: null,
  connected: false,
  sources: [],
  stream_status: null,
  video_a: null,
  video_b: null,
  video_only_sources: [],
});

const mutations = {
  voctomix_state_update(state, incoming) {
    Object.assign(state, incoming);
  },
  voctomix_config(state, config) {
    state.video_only_sources = config.video_only_sources;
  },
};

const actions = {
  voctomix_action({dispatch}, action) {
    dispatch('send_action', {type: 'voctomix', action});
  },
};

export default {
  actions,
  mutations,
  state,
};
