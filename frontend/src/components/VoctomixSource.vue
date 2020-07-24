<template>
  <div class="card">
    <div class="card-header source-header">
      <div class="source-name">
        {{ title }}
      </div>
      <div>
        <button
          class="btn source"
          v-bind:class="{'source-a': source_a, 'btn-light': !source_a}"
          v-bind:disabled="source_a"
          v-on:click="send('set_a')"
        >
          A
        </button>
        <button
          class="btn source"
          v-bind:class="{'source-b': source_b, 'btn-light': !source_b}"
          v-bind:disabled="source_b"
          v-on:click="send('set_b')"
        >
          B
        </button>
      </div>
    </div>
    <div class="card-body">
      <VideoPreview v-bind:room="source" />
      <button
        class="btn source-a"
        v-bind:disabled="is_fullscreen"
        v-on:click="send('fullscreen')"
      >
        Fullscreen
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
.source-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.source-a {
  background: #2222ff;
  color: white;
}
.source-b {
  background: #ff2222;
  color: white;
}
</style>
