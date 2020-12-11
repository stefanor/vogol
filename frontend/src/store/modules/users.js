const state = () => ({
  connected_users: [],
  recent_actions: [],
});

const mutations = {
  users_update(state, users) {
    state.connected_users = users;
  },
  user_action(state, user_action) {
    const {username, action, type} = user_action;
    const timestamp = new Date();
    if (state.recent_actions.length > 0) {
      const last_action = state.recent_actions.slice(-1)[0];
      if (
        username == last_action.username &&
        timestamp - last_action.timestamp < 1000
      ) {
        last_action.actions.push({action, type});
        return;
      }
    }
    state.recent_actions.push({
      username,
      actions: [{action, type}],
      timestamp,
    });
    if (state.recent_actions.length >= 5) {
      state.recent_actions.shift();
    }
  },
};

const actions = {};

export default {
  actions,
  mutations,
  state,
};
