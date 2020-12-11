<template>
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
    <p>You need to login to use Vogol.</p>
    <p>Login is managed through Salsa.</p>
  </b-modal>
</template>

<script>
import Vue from 'vue';
import {ModalPlugin} from 'bootstrap-vue';
import {mapState} from 'vuex';

Vue.use(ModalPlugin);

export default {
  computed: mapState({
    logged_out: state => state.websocket.connection == 'logged_out',
  }),
  methods: {
    loginButton(event) {
      event.preventDefault();
      window.location = '/login';
    },
  },
};
</script>
