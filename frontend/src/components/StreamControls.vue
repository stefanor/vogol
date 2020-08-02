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
        v-on:click="stream_live"
      >
        Go Live
      </button>
      <br />
      <button
        class="btn btn-danger"
        v-bind:disabled="loop"
        v-on:click="stream_loop"
      >
        Loop
      </button>
      <button
        class="btn btn-danger"
        v-bind:disabled="blank"
        v-on:click="stream_blank"
      >
        Blank
      </button>
      <br />
      <button class="btn btn-secondary" v-on:click="cut">
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
    cut() {
      this.send('cut');
    },
    on_key_down(ev) {
      if (ev.key == 'F11') {
        ev.preventDefault();
        this.stream_loop();
      } else if (ev.key == 'F12') {
        ev.preventDefault();
        this.stream_live();
      } else if (ev.key == 't') {
        ev.preventDefault();
        this.cut();
      }
    },
    send(action) {
      this.$store.dispatch('voctomix_action', {action});
    },
    stream_blank() {
      this.send('stream_blank');
    },
    stream_live() {
      this.send('stream_live');
    },
    stream_loop() {
      this.send('stream_loop');
    },
  },
  mounted() {
    window.addEventListener('keydown', this.on_key_down);
  },
  beforeDestroy() {
    window.removeEventListener('keydown', this.on_key_down);
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
