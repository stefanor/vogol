const state = () => ({
  authenticating: false,
  error_message: null,
  name: null,
  type: null,
  url: null,
  username: null,
});

const mutations = {
  auth_config(state, config) {
    state.authenticating = false;
    state.error_message = null;
    state.username = config.username;
  },
  auth_display(state, config) {
    state.authenticating = false;
    state.error_message = null;
    state.type = config.type;
    if (config.type == 'gitlab') {
      state.name = config.name;
      state.url = config.url;
    }
  },
  auth_error(state, error) {
    state.authenticating = false;
    state.error_message = error;
  },
  auth_submit(state) {
    state.authenticating = true;
  },
};

const actions = {
  auth_password_login({commit, dispatch}, form_data) {
    commit('auth_submit');
    fetch('/login', {
      body: form_data,
      credentials: 'same-origin',
      method: 'POST',
    }).then(response => {
      if (response.status >= 400) {
        commit('auth_error', response.statusText);
      } else {
        // Reset the state so we will be allowed to connect
        commit('disconnected');
        dispatch('connect');
      }
    });
  },
};

export default {
  actions,
  mutations,
  state,
};
