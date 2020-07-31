const state = () => ({
  duration: self.duration,
  file: null,
  files: [],
  playback: self.playback,
  position: self.position,
});

const mutations = {
  playback_state_update(state, incoming) {
    Object.assign(state, incoming);
  },

  playback_files_update(state, files) {
    state.files = files;
  },
};

const actions = {
  playback_action({dispatch, rootState}, action) {
    if (action.action == 'play') {
      const voctomix = rootState.voctomix;
      if (voctomix.sources.indexOf('recording') == -1) {
        console.log("No recording source, can't control it");
      } else {
        if (
          voctomix.composite_mode != 'fullscreen' ||
          voctomix.video_a != 'recording'
        ) {
          dispatch('send_action', {
            type: 'voctomix',
            action: {
              action: 'fullscreen',
              source: 'recording',
            },
          });
        }
        if (rootState.voctomix.audio.recording < 0.2) {
          dispatch('send_action', {
            type: 'voctomix',
            action: {
              action: 'unmute',
              source: 'recording',
            },
          });
        }
      }
    }
    dispatch('send_action', {type: 'player', action});
  },

  refresh_files({dispatch}) {
    dispatch('send_action', {
      type: 'player',
      action: {action: 'refresh_files'},
    });
  },
};

export default {
  actions,
  mutations,
  state,
};
