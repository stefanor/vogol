const state = () => ({
  error: null,
  logged_in: true,
  pollers: [],
  preview_update_interval: 2000,
  state_update_interval: 5000,
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
};

export default {
  actions,
  mutations,
  state,
};
