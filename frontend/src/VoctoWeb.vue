<template>
  <div id="app" class="content">
    <h1>VoctoWeb</h1>
    <b-alert variant="danger" v-model="disconnected">
      <strong>Disconnected from core</strong>
    </b-alert>
    <b-alert variant="danger" v-model="has_error">
      <strong>Error:</strong> {{ error }}
    </b-alert>
    <div class="row">
      <RoomPreview />
      <StreamControls />
      <LayoutControls />
    </div>
    <div class="row">
      <VoctomixSource
        v-for="source in sources"
        v-bind:source="source"
        v-bind:key="source"
      />
    </div>
    <div>Last updated: {{ last_update }}</div>
    <div>
      Source:
      <a href="https://salsa.debian.org/debconf-video-team/voctoweb"
        >on Salsa</a
      >
    </div>
    <b-modal
      title="Not Logged In"
      ok-title="Login"
      v-model="logged_out"
      v-on:ok="loginButton"
      centered
      hide-header-close
      no-close-on-esc
      ok-only
    >
      <p>You need to login to use VoctWeb.</p>
      <p>Login is managed through Salsa.</p>
    </b-modal>
  </div>
</template>

<script>
import Vue from 'vue';
import {AlertPlugin, ModalPlugin} from 'bootstrap-vue';
import {mapState} from 'vuex';

import RoomPreview from './components/RoomPreview.vue';
import StreamControls from './components/StreamControls.vue';
import LayoutControls from './components/LayoutControls.vue';
import VoctomixSource from './components/VoctomixSource.vue';

Vue.use(AlertPlugin);
Vue.use(ModalPlugin);

export default {
  name: 'VoctoWeb',
  components: {
    LayoutControls,
    RoomPreview,
    StreamControls,
    VoctomixSource,
  },
  computed: mapState({
    error: state => state.ui.error,
    disconnected: state => !state.voctomix.connected,
    has_error: state => !!state.ui.error,
    last_update: state => state.ui.state_last_updated,
    logged_out: state => !state.ui.logged_in,
    sources: state => state.voctomix.sources,
  }),
  methods: {
    loginButton(event) {
      event.preventDefault();
      window.location = '/login';
    },
  },

  created() {
    this.$store.dispatch('connect');
  },
  beforeDestroy() {
    this.$store.dispatch('stop_polling');
  },
};
</script>
