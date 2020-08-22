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
  fullscreen_solo({dispatch, state}, source) {
    dispatch('send_action', {
      type: 'voctomix',
      action: {
        action: 'fullscreen',
        source,
      },
    });
    for (const [other_source, level] of Object.entries(state.audio)) {
      if (source == other_source) {
        if (level < 0.2) {
          dispatch('send_action', {
            type: 'voctomix',
            action: {
              action: 'unmute',
              source: source,
            },
          });
        }
      } else {
        if (level > 0.2) {
          dispatch('send_action', {
            type: 'voctomix',
            action: {
              action: 'mute',
              source: other_source,
            },
          });
        }
      }
    }
  },
  voctomix_action({dispatch}, action) {
    dispatch('send_action', {type: 'voctomix', action});
  },
};

export default {
  actions,
  mutations,
  state,
};
