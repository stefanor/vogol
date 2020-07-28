<template>
  <div class="card">
    <div class="card-header">
      Stream
      <div class="stream-status badge badge-success" v-if="live">Live</div>
      <div class="stream-status badge badge-danger" v-if="loop">Loop</div>
      <div class="stream-status badge badge-danger" v-if="blank">Blank</div>
    </div>
    <div class="card-body">
      <button
        class="btn btn-success"
        v-bind:disabled="live"
        v-on:click="send('stream_live')"
      >
        Go Live
      </button>
      <br />
      <button
        class="btn btn-danger"
        v-bind:disabled="loop"
        v-on:click="send('stream_loop')"
      >
        Loop
      </button>
      <button
        class="btn btn-danger"
        v-bind:disabled="blank"
        v-on:click="send('stream_blank')"
      >
        Blank
      </button>
      <br />
      <button class="btn btn-secondary" v-on:click="send('cut')">
        Cut
      </button>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex';

export default {
  computed: mapState({
    stream_status: state => state.voctomix.stream_status,
    live() {
      return this.stream_status == 'live';
    },
    loop() {
      return this.stream_status == 'blank loop';
    },
    blank() {
      return this.stream_status == 'blank nostream';
    },
  }),
  methods: {
    send(action) {
      this.$store.dispatch('voctomix_action', {action});
    },
  },
};
</script>

<style>
div.stream-status {
  float: right;
  padding: 0.4em;
  margin: 0.1em;
}
</style>
