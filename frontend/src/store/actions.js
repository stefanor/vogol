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

export default {
  connect({dispatch}) {
    dispatch('update_state').then(() => dispatch('start_polling'));
  },

  logout({commit, dispatch}) {
    commit('logout');
    dispatch('stop_polling');
  },

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

  start_polling({commit, dispatch, state}) {
    const sources = ['room'].concat(state.sources);
    for (const source of sources) {
      commit(
        'add_poller',
        setInterval(
          () => dispatch('update_preview', source),
          state.preview_update_interval
        )
      );
    }
    commit(
      'add_poller',
      setInterval(() => dispatch('update_state'), state.state_update_interval)
    );
  },

  stop_polling({commit, state}) {
    for (const poller of state.pollers) {
      clearInterval(poller);
    }
    commit('clear_pollers');
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
