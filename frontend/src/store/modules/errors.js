const state = () => ({
  errors: [],
});

const mutations = {
  add_error(state, {key, message, priority}) {
    state.errors = state.errors.filter(error => error.key != key);
    const timestamp = new Date();
    state.errors.push({
      key,
      message,
      priority,
      timestamp,
    });
    state.errors.sort((a, b) => {
      if (a.priority != b.priority) {
        return b.priority - a.priority;
      }
      return a.timestamp - b.timestamp;
    });
  },

  remove_error(state, key) {
    state.errors = state.errors.filter(error => error.key != key);
  },
};

export default {
  mutations,
  state,
};
