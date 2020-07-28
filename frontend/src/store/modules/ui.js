const state = () => ({
  error: null,
  logged_in: true,
  pollers: [],
  preview_update_interval: 2000,
  state_update_interval: 5000,
  state_last_updated: null,
});

const mutations = {
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

  state_updated(state) {
    state.state_last_updated = new Date();
  }
};

// Check a state response for sanity
var check_response = function({commit, dispatch}, response) {
  if (response.status == 403) {
    dispatch('logout');
  }
  if (!response.ok) {
    commit(
      'error',
      'Failed to retrieve ' + response.url + ' got ' + response.status
    );
  }
  return response;
};


const actions = {
  connect({dispatch}) {
    dispatch('update_state').then(() => dispatch('start_polling'));
  },

  logout({commit, dispatch}) {
    commit('logout');
    dispatch('stop_polling');
  },

  start_polling({commit, dispatch, state, rootState}) {
    const sources = ['room'].concat(rootState.voctomix.sources);
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

  update_state(context) {
    return new Promise(resolve => {
      const {commit, dispatch} = context;
      fetch('/state', {
        credentials: 'same-origin',
        method: 'GET',
      })
        .then(response => check_response(context, response))
        .then(response => response.json())
        .then(response => {
          dispatch('voctomix_received_state', response.voctomix);
          commit('state_updated');
          return response;
        })
        .then(() => resolve());
    });
  },

  send_action(context, action) {
    const {commit, dispatch} = context;
    fetch('/action', {
      credentials: 'same-origin',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(action),
    })
      .then(response => check_response(context, response))
      .then(response => response.json())
      .then(response => {
        dispatch('voctomix_received_state', response.voctomix);
        commit('state_updated');
        return response;
      })
      .catch(error => {
        commit('error', 'Failed to perform action. Got ' + error);
      });
  },
};

export default {
  actions,
  mutations,
  state,
};
