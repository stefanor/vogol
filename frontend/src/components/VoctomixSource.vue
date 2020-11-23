<template>
  <div class="card">
    <div class="card-header source-header">
      <div class="source-name">
        {{ title }}
      </div>
      <button
        class="btn source-a"
        v-bind:disabled="is_fullscreen_solo"
        v-on:click="fullscreen_solo"
        v-if="!is_video_only"
      >
        Fullscreen Solo
      </button>
      <button
        class="btn source-a"
        v-bind:disabled="is_fullscreen"
        v-on:click="fullscreen"
        v-if="is_video_only"
      >
        Fullscreen
      </button>
    </div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item">
        <VideoPreview v-bind:room="source" />
      </li>
      <li class="list-group-item">
        Video:
        <button
          class="btn source"
          v-bind:class="{'source-a': source_a, 'btn-light': !source_a}"
          v-bind:disabled="source_a"
          v-on:click="set_a"
        >
          A
        </button>
        <button
          class="btn source"
          v-bind:class="{'source-b': source_b, 'btn-light': !source_b}"
          v-bind:disabled="source_b"
          v-on:click="set_b"
        >
          B
        </button>
      </li>
      <li class="list-group-item" v-if="!is_video_only">
        <AudioControl v-bind:source="source" />
      </li>
    </ul>
  </div>
</template>

<script>
import startCase from 'lodash/startCase';
import {mapState} from 'vuex';

import AudioControl from './AudioControl.vue';
import VideoPreview from './VideoPreview.vue';

export default {
  props: ['source', 'index'],
  components: {
    AudioControl,
    VideoPreview,
  },
  computed: mapState({
    is_fullscreen(state) {
      return state.voctomix.composite_mode == 'fullscreen' && this.source_a;
    },
    is_fullscreen_solo(state) {
      if (state.voctomix.composite_mode == 'fullscreen' && this.source_a) {
        for (const [source, level] of Object.entries(state.voctomix.audio)) {
          if (this.source == source) {
            if (level < 0.2) {
              return false;
            }
          } else {
            if (level > 0.2) {
              return false;
            }
          }
        }
        return true;
      } else {
        return false;
      }
    },
    is_video_only(state) {
      return state.voctomix.video_only_sources.indexOf(this.source) !== -1;
    },
    title() {
      return startCase(this.source);
    },
    source_a(state) {
      return state.voctomix.video_a == this.source;
    },
    source_b(state) {
      return state.voctomix.video_b == this.source;
    },
  }),
  methods: {
    fullscreen() {
      this.send('fullscreen');
    },
    fullscreen_solo() {
      this.send('fullscreen_solo');
    },
    on_key_down(ev) {
      const source_number = this.index + 1;
      if (ev.key == source_number && !ev.shiftKey && !ev.altKey) {
        if (!ev.ctrlKey) {
          ev.preventDefault();
          if (this.is_video_only) {
            this.fullscreen();
          } else {
            this.fullscreen_solo();
          }
        } else {
          ev.preventDefault();
          this.set_b();
        }
      }
    },
    set_a() {
      this.send('set_a');
    },
    set_b() {
      this.send('set_b');
    },
    send(action) {
      const source = this.source;
      this.$store.dispatch('voctomix_action', {action, source});
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
