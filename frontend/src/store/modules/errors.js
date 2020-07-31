const state = () => ({
  error: null,
});

const mutations = {
  error(state, error) {
    state.error = error;
  },
};

export default {
  mutations,
  state,
};
