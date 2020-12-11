import {deserialize} from 'bson';

const state = () => ({
  connection: 'disconnected',
  room_name: null,
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

  websocket_config(state, config) {
    state.room_name = config.room_name;
  },
};

const actions = {
  connect({commit, dispatch, state}) {
    if (state.connection != 'disconnected') {
      return;
    }
    const url = location.href.replace(/^http/, 'ws') + 'ws';
    const ws = new WebSocket(url);
    ws.binaryType = 'arraybuffer';
    ws.addEventListener('message', ev => dispatch('ws_message_raw', ev));
    ws.addEventListener('close', ev => dispatch('ws_close', ev));
    ws.addEventListener('error', ev => dispatch('ws_error', ev));
    ws.addEventListener('open', ev => dispatch('connected', ev));
    commit('connecting', ws);
  },

  connected({commit}) {
    commit('connected');
    commit('remove_error', 'ws');
  },

  logout({commit}, config) {
    commit('logout');
    commit('auth_display', config);
  },

  ws_message_raw({dispatch}, ev) {
    if (typeof ev.data == 'string') {
      const body = JSON.parse(ev.data);
      dispatch('ws_message_deserialized', body);
    } else if (ev.data instanceof ArrayBuffer) {
      const body = deserialize(new Uint8Array(ev.data));
      dispatch('ws_message_deserialized', body);
    }
  },

  ws_message_deserialized({commit}, body) {
    switch (body.type) {
      case 'config':
        commit('auth_config', body.config);
        commit('presets_config', body.config);
        commit('voctomix_config', body.config);
        commit('websocket_config', body.config);
        break;
      case 'connected_users':
        commit('users_update', body.users);
        break;
      case 'player_files':
        commit('playback_files_update', body.files);
        break;
      case 'player_state':
        commit('playback_state_update', body.state);
        break;
      case 'preview':
        commit('preview_image', {
          source: body.source,
          img: new Blob([body.jpeg.buffer], {type: 'image/jpeg'}),
        });
        break;
      case 'preview_audio_level':
        commit('preview_audio_level', {
          source: body.source,
          rms: body.rms,
          peak: body.peak,
          decay: body.decay,
        });
        break;
      case 'voctomix_state':
        commit('voctomix_state_update', body.state);
        break;
      case 'user_action':
        commit('user_action', body.user_action);
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
        response.json().then(body => {
          dispatch('logout', body);
        });
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
