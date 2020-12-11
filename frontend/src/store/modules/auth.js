const state = () => ({
  username: null,
});

const mutations = {
  auth_config(state, config) {
    state.username = config.username;
  },
};

const actions = {};

export default {
  actions,
  mutations,
  state,
};
