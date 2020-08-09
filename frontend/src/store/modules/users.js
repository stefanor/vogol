const state = () => ({
  connected_users: [],
  username: null,
});

const mutations = {
  users_update(state, users) {
    state.connected_users = users;
  },
  users_logged_in(state, username) {
    state.username = username;
  },
};

const actions = {};

export default {
  actions,
  mutations,
  state,
};
