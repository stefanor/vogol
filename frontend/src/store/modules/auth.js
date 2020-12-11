const state = () => ({
  name: null,
  type: null,
  url: null,
  username: null,
});

const mutations = {
  auth_config(state, config) {
    state.username = config.username;
  },
  auth_display(state, config) {
    state.type = config.type;
    if (config.type == 'gitlab') {
      state.name = config.name;
      state.url = config.url;
    }
  },
};

const actions = {};

export default {
  actions,
  mutations,
  state,
};
