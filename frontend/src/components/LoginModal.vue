<template>
  <b-modal
    title="Not Logged In"
    ok-title="Login"
    v-bind:ok-disabled="authenticating"
    v-model="logged_out"
    v-on:ok="loginButton"
    v-on:shown="modalShown"
    centered
    hide-header-close
    no-close-on-esc
    ok-only
    static
  >
    <p>You need to login to use Vogol.</p>
    <p v-if="type == 'gitlab'">
      Authentication is done via SSO through
      <a v-bind:href="url">{{ name }}</a
      >.
    </p>
    <form ref="loginForm" v-if="type == 'password'">
      <div class="alert alert-danger" v-if="error_message">
        <b>Login Failed:</b> {{ error_message }}
      </div>
      <div class="form-group">
        <input
          type="text"
          class="form-control"
          name="username"
          placeholder="Username"
        />
      </div>
      <div class="form-group">
        <input
          type="password"
          class="form-control"
          name="password"
          placeholder="Password"
        />
      </div>
    </form>
    <template #modal-ok>
      <span
        class="spinner-border spinner-border-sm"
        role="status"
        aria-hidden="true"
        v-if="authenticating"
      ></span>
      <span v-if="authenticating">Logging in...</span>
      <span v-else>Login</span>
    </template>
  </b-modal>
</template>

<script>
import Vue from 'vue';
import {ModalPlugin} from 'bootstrap-vue';
import {mapState} from 'vuex';

Vue.use(ModalPlugin);

export default {
  computed: mapState({
    error_message: state => state.auth.error_message,
    logged_out: state => state.websocket.connection == 'logged_out',
    authenticating: state => state.auth.authenticating,
    name: state => state.auth.name,
    type: state => state.auth.type,
    url: state => state.auth.url,
  }),
  methods: {
    loginButton(event) {
      if (this.type == 'gitlab') {
        event.preventDefault();
        window.location = '/login';
      } else if (this.type == 'password') {
        event.preventDefault();
        this.passwordLogin();
      }
    },
    inputKeyDown(event) {
      if (event.key == 'Enter' && this.type == 'password') {
        event.preventDefault();
        this.passwordLogin();
      }
    },
    modalShown() {
      if (this.type == 'password') {
        const form = this.$refs.loginForm;
        for (const input of form.querySelectorAll('input')) {
          input.addEventListener('keydown', this.inputKeyDown);
        }
      }
    },
    passwordLogin() {
      if (this.authenticating) {
        return;
      }
      const data = new FormData(this.$refs.loginForm);
      this.$store.dispatch('auth_password_login', data);
    },
  },
};
</script>
