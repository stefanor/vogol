<template>
  <div id="app">
    <b-navbar
      toggleable="lg"
      type="light"
      v-bind:variant="all_good ? 'success' : 'danger'"
    >
      <b-navbar-brand href="#">
        <img v-bind:src="voctoweb_logo" id="nav-logo" />
        VoctoWeb
      </b-navbar-brand>
      <NavBarControls />
    </b-navbar>
    <main class="container-fluid">
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
        <PlaybackControls />
      </div>
      <div class="row">
        <VoctomixSource
          v-for="(source, source_index) in sources"
          v-bind:source="source"
          v-bind:index="source_index"
          v-bind:key="source"
        />
      </div>
    </main>
    <footer class="footer mt-auto py-3 bg-light">
      <div class="container-fluid">
        <span class="text-muted">
          Source:
          <a href="https://salsa.debian.org/debconf-video-team/voctoweb"
            >on Salsa</a
          >
        </span>
      </div>
    </footer>
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

import NavBarControls from './components/NavBarControls.vue';
import PlaybackControls from './components/PlaybackControls.vue';
import RoomPreview from './components/RoomPreview.vue';
import VoctomixSource from './components/VoctomixSource.vue';
import favicon_svg from './favicon/favicon.svg';

Vue.use(AlertPlugin);
Vue.use(ModalPlugin);
Vue.use(NavbarPlugin);

export default {
  name: 'VoctoWeb',
  components: {
    NavBarControls,
    PlaybackControls,
    RoomPreview,
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

/* Sticky footer: */
html {
  position: relative;
  min-height: 100%;
}
body {
  margin-bottom: 3rem;
}
.footer {
  position: absolute;
  bottom: 0;
  width: 100%;
  height: 3rem;
  padding-left: 1rem;
}
</style>
