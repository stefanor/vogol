const state = () => ({
  connection: 'disconnected',
  error: null,
  state_last_updated: null,
  ws: null,
});

const mutations = {
  connecting(state, ws) {
    state.connection = 'connecting';
    state.ws = ws;
  },

  connected(state) {
    state.connection = 'connected';
  },

  disconnected(state) {
    state.connection = 'disconnected';
    state.ws = null;
  },

  error(state, error) {
    state.error = error;
  },

  logout(state) {
    state.connection = 'logged_out';
    state.ws = null;
  },

  state_updated(state) {
    state.state_last_updated = new Date();
  },
};

const actions = {
  connect({commit, dispatch, state}) {
    if (state.connection != 'disconnected') {
      return;
    }
    const url = location.href.replace(/^http/, 'ws') + 'ws';
    const ws = new WebSocket(url);
    ws.addEventListener('message', ev => dispatch('ws_message', ev));
    ws.addEventListener('close', ev => dispatch('ws_close', ev));
    ws.addEventListener('error', ev => dispatch('ws_error', ev));
    ws.addEventListener('open', ev => dispatch('connected', ev));
    commit('connecting', ws);
  },

  connected({commit, dispatch}) {
    commit('connected');
    dispatch('start_poller', 'room');
  },

  logout({commit, dispatch}) {
    commit('logout');
    dispatch('stop_polling');
  },

  ws_message({commit, dispatch}, ev) {
    const body = JSON.parse(ev.data);
    switch (body.type) {
      case 'voctomix_state':
        dispatch('voctomix_received_state', body.state);
        break;
      case 'player_state':
        dispatch('playback_received_state', body.state);
        break;
      case 'player_files':
        dispatch('playback_received_files', body.files);
        break;
    }
    commit('state_updated');
  },

  ws_error({commit, dispatch}) {
    commit('error', 'WebSocket Error');
    commit('disconnected');
    // We can't see 403s from WebSockets
    fetch('/ws', {
      credentials: 'same-origin',
    }).then(response => {
      if (response.status == 403) {
        dispatch('logout');
      }
    });
  },

  ws_close({commit, dispatch}) {
    commit('error', 'WebSocket Closed');
    commit('disconnected');
    setTimeout(() => dispatch('connect'), 1000);
  },

  send_action({state}, action) {
    state.ws.send(JSON.stringify(action));
  },
};

export default {
  actions,
  mutations,
  state,
};
