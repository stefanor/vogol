const state = () => ({
  audio: [],
  composite_mode: null,
  connected: false,
  last_update: null,
  sources: [],
  stream_status: null,
  video_a: null,
  video_b: null,
});

const mutations = {
  received_state(state, incoming) {
    Object.assign(state, incoming);
    state.last_update = new Date();
  },
};

// Check a state response for sanity
// Restart polling if necessary
// Return JSON
var check_response = function({commit, dispatch, state}, response) {
  if (response.status == 403) {
    dispatch('logout');
  }
  if (!response.ok) {
    commit(
      'error',
      'Failed to retrieve ' + response.url + ' got ' + response.status
    );
  }
  const json = response.json();
  if (json.sources != state.sources) {
    dispatch('stop_polling');
    dispatch('start_polling');
  }
  return json;
};

const actions = {
  send_action(context, action) {
    const {commit} = context;
    fetch('/action', {
      credentials: 'same-origin',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(action),
    })
      .then(response => check_response(context, response))
      .then(response => commit('received_state', response))
      .catch(error => {
        commit('error', 'Failed to perform action. Got ' + error);
      });
  },

  update_state(context) {
    return new Promise(resolve => {
      const {commit} = context;
      fetch('/state', {
        credentials: 'same-origin',
        method: 'GET',
      })
        .then(response => check_response(context, response))
        .then(response => commit('received_state', response))
        .then(() => resolve());
    });
  },
};

export default {
  actions,
  mutations,
  state,
};
