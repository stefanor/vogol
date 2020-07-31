const state = () => ({
  connection: 'disconnected',
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

  connected({commit}) {
    commit('connected');
    commit('remove_error', 'ws');
  },

  logout({commit}) {
    commit('logout');
  },

  ws_message({commit}, ev) {
    const body = JSON.parse(ev.data);
    switch (body.type) {
      case 'voctomix_state':
        commit('voctomix_state_update', body.state);
        break;
      case 'player_state':
        commit('playback_state_update', body.state);
        break;
      case 'player_files':
        commit('playback_files_update', body.files);
        break;
    }
    commit('state_updated');
  },

  ws_error({commit, dispatch}) {
    commit('add_error', {
      key: 'ws',
      message: 'WebSocket Error',
      priority: 100,
    });
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
    commit('add_error', {
      key: 'ws',
      message: 'WebSocket Closed',
      priority: 100,
    });
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
