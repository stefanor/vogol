// Check a state response for sanity
export var check_response = function({commit, dispatch}, response) {
  if (response.status == 403) {
    dispatch('logout');
    throw new Error('logged out');
  }
  if (!response.ok) {
    commit(
      'error',
      'Failed to retrieve ' + response.url + ' got ' + response.status
    );
  }
  return response;
};
