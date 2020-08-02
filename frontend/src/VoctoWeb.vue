<template>
  <div id="app" class="content">
    <b-navbar
      toggleable="lg"
      type="light"
      v-bind:variant="all_good ? 'success' : 'danger'"
    >
      <b-navbar-brand href="#">
        <img v-bind:src="voctoweb_logo" id="nav-logo" />
        VoctoWeb
      </b-navbar-brand>
    </b-navbar>
    <b-alert variant="danger" v-model="disconnected">
      <strong>Disconnected from core</strong>
    </b-alert>
    <b-alert
      variant="danger"
      v-for="error in errors"
      v-bind:key="error.key"
      v-on:dismissed="dismiss_error(error)"
      show
      dismissible
    >
      <strong>Error:</strong> {{ error.message }}
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
    all_good: state =>
      state.voctomix.stream_status == 'live' && state.voctomix.connected,
    errors: state => state.errors.errors,
    disconnected: state => !state.voctomix.connected,
    last_update: state => state.websocket.state_last_updated,
    logged_out: state => state.websocket.connection == 'logged_out',
    sources: state => state.voctomix.sources,
  }),
  methods: {
    dismiss_error(error) {
      this.$store.commit('remove_error', error.key);
    },
    loginButton(event) {
      event.preventDefault();
      window.location = '/login';
    },
  },
  created() {
    this.$store.dispatch('connect');
  },
};
</script>

<style>
#nav-logo {
  max-height: 1.5em;
}
</style>
