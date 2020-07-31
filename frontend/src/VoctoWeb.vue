<template>
  <div id="app" class="content">
    <b-navbar
      toggleable="lg"
      type="light"
      v-bind:variant="stream_live ? 'success' : 'danger'"
    >
      <b-navbar-brand href="#">
        <img v-bind:src="voctoweb_logo" id="nav-logo" />
        VoctoWeb
      </b-navbar-brand>
    </b-navbar>
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
      <PlaybackControls />
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
import {AlertPlugin, NavbarPlugin, ModalPlugin} from 'bootstrap-vue';
import {mapState} from 'vuex';

import RoomPreview from './components/RoomPreview.vue';
import StreamControls from './components/StreamControls.vue';
import LayoutControls from './components/LayoutControls.vue';
import PlaybackControls from './components/PlaybackControls.vue';
import VoctomixSource from './components/VoctomixSource.vue';
import favicon_svg from './favicon/favicon.svg';

Vue.use(AlertPlugin);
Vue.use(ModalPlugin);
Vue.use(NavbarPlugin);

export default {
  name: 'VoctoWeb',
  components: {
    LayoutControls,
    PlaybackControls,
    RoomPreview,
    StreamControls,
    VoctomixSource,
  },
  data: () => ({
    voctoweb_logo: favicon_svg,
  }),
  computed: mapState({
    error: state => state.websocket.error,
    disconnected: state => !state.voctomix.connected,
    stream_live: state => state.voctomix.stream_status == 'live',
    has_error: state => !!state.websocket.error,
    last_update: state => state.websocket.state_last_updated,
    logged_out: state => state.websocket.connection == 'logged_out',
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

<style>
#nav-logo {
  max-height: 1.5em;
}
</style>
