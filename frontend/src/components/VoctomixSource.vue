<template>
  <div class="card">
    <div class="card-header">
      {{ title }}
      <div class="selected-source badge badge-warning" v-if="source_a">A</div>
      <div class="selected-source badge badge-info" v-if="source_b">B</div>
    </div>
    <div class="card-body">
      <VideoPreview v-bind:room="source" />
      <button
        class="btn btn-primary"
        v-bind:disabled="is_fullscreen"
        v-on:click="send('fullscreen')"
      >
        Fullscreen
      </button>
      <button
        class="btn btn-warning"
        v-bind:disabled="source_a"
        v-on:click="send('set_a')"
      >
        A
      </button>
      <button
        class="btn btn-info"
        v-bind:disabled="source_b"
        v-on:click="send('set_b')"
      >
        B
      </button>
      <br />
      <AudioControl v-bind:source="source" />
    </div>
  </div>
</template>

<script>
import startCase from 'lodash/startCase';
import {mapState} from 'vuex';

import AudioControl from './AudioControl.vue';
import VideoPreview from './VideoPreview.vue';

export default {
  props: ['source'],
  components: {
    AudioControl,
    VideoPreview,
  },
  computed: mapState({
    is_fullscreen(state) {
      return state.composite_mode == 'fullscreen' && this.source_a;
    },
    title() {
      return startCase(this.source);
    },
    source_a(state) {
      return state.video_a == this.source;
    },
    source_b(state) {
      return state.video_b == this.source;
    },
  }),
  methods: {
    send(action) {
      const source = this.source;
      this.$store.dispatch('send_action', {action, source});
    },
  },
};
</script>

<style>
div.selected-source {
  float: right;
  padding: 0.4em;
  margin: 0.1em;
}
</style>
