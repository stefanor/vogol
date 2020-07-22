<template>
  <div class="card">
    <div class="card-header">Stream</div>
    <div class="card-body">
      <button
        class="btn btn-success"
        v-bind:disabled="stream_status == 'live'"
        v-on:click="send_action('stream_live')"
      >
        Go Live
      </button>
      <br />
      <button
        class="btn btn-danger"
        v-bind:disabled="stream_status == 'blank loop'"
        v-on:click="send_action('stream_loop')"
      >
        Loop
      </button>
      <button
        class="btn btn-danger"
        v-bind:disabled="stream_status == 'blank nostream'"
        v-on:click="send_action('stream_blank')"
      >
        Blank
      </button>
      <br />
      <button class="btn btn-secondary" v-on:click="send_action('cut')">
        Cut
      </button>
      <div>Stream Status: {{ stream_status }}</div>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex';

export default {
  computed: mapState({
    stream_status: 'stream_status',
  }),
  methods: {
    send_action(action) {
      this.$store.dispatch('send_action', {action});
    },
  },
};
</script>
