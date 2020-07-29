import {check_response} from '../lib/helpers';

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

  files_refreshed(state, files) {
    state.files = files;
  },
};

const actions = {
  playback_action({dispatch}, action) {
    var actions = {playback: action};
    if (action.action == 'play') {
      actions.voctomix = {
        action: 'fullscreen',
        source: 'recording',
      };
    }

    dispatch('send_action', actions);
  },

  playback_received_state({commit}, updated_state) {
    commit('playback_state_update', updated_state);
  },

  refresh_files(context) {
    const {commit} = context;
    fetch('/playback/files', {
      credentials: 'same-origin',
      method: 'GET',
    })
      .then(response => check_response(context, response))
      .then(response => response.json())
      .then(response => {
        commit('files_refreshed', response);
        return response;
      })
      .catch(error => {
        commit('error', 'Failed to refresh files. Got ' + error);
      });
  },
};

export default {
  actions,
  mutations,
  state,
};
