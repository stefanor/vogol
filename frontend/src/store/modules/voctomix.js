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

  voctomix_received_state({dispatch, commit, state}, updated_state) {
    const new_sources = updated_state.sources.filter(
      x => !state.sources.includes(x)
    );
    for (const new_source of new_sources) {
      dispatch('start_poller', new_source);
    }
    const old_sources = state.sources.filter(
      x => !updated_state.sources.includes(x)
    );
    for (const old_source of old_sources) {
      dispatch('stop_poller', old_source);
    }
    commit('voctomix_state_update', updated_state);
  },
};

export default {
  actions,
  mutations,
  state,
};
