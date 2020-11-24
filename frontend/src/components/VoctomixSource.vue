<template>
  <div class="card">
    <div
      class="card-header source-header"
      v-bind:class="[is_muted ? '' : 'bg-success']"
    >
      <div class="source-name">
        {{ title }}
      </div>
      <div class="badge volume-badge">
        <b-icon-volume-mute-fill scale="1.5" v-if="is_muted" />
        <b-icon-volume-up-fill scale="1.5" v-else />
      </div>
      <button
        class="btn source-a"
        v-bind:disabled="is_fullscreen_solo"
        v-on:click="fullscreen_solo"
        v-if="!is_video_only"
      >
        Select
      </button>
      <button
        class="btn source-a"
        v-bind:disabled="is_fullscreen"
        v-on:click="fullscreen"
        v-if="is_video_only"
      >
        Select Video
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
        <div>
          Audio:
          <button
            class="btn btn-danger"
            v-bind:disabled="is_muted"
            v-on:click="send('mute')"
          >
            Mute
          </button>
          <button
            class="btn btn-success"
            v-bind:disabled="is_unity"
            v-on:click="send('unmute')"
          >
            0 db
          </button>
        </div>
        <div class="volume">
          Level:
          {{ volume_percent }}% ({{ volume_db }} dB)
          <b-form-input
            type="range"
            v-model="volume_db"
            step="0.5"
            min="-20"
            max="10"
          ></b-form-input>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import {
  BFormInput,
  BIconVolumeUpFill,
  BIconVolumeMuteFill,
} from 'bootstrap-vue';
import startCase from 'lodash/startCase';
import {mapState} from 'vuex';

import VideoPreview from './VideoPreview.vue';

export default {
  props: ['source', 'index'],
  components: {
    BFormInput,
    BIconVolumeUpFill,
    BIconVolumeMuteFill,
    VideoPreview,
  },
  computed: Object.assign(
    mapState({
      is_fullscreen(state) {
        return state.voctomix.composite_mode == 'fullscreen' && this.source_a;
      },
      is_fullscreen_solo(state) {
        return (
          state.voctomix.composite_mode == 'fullscreen' &&
          this.source_a &&
          this.is_unity
        );
      },
      is_muted() {
        return this.volume < 0.2;
      },
      is_unity() {
        return this.volume == 1;
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
      volume(state) {
        return state.voctomix.audio[this.source];
      },
      volume_percent() {
        const volume_percent = Math.trunc(this.volume * 100);
        return volume_percent;
      },
    }),
    {
      volume_db: {
        get() {
          const db = this.volume > 0 ? 20.0 * Math.log10(this.volume) : -20;
          return Number.parseFloat(db).toFixed(1);
        },
        set(value) {
          const volume = value > -20.0 ? 10 ** (value / 20) : 0;
          this.$store.dispatch('voctomix_action', {
            action: 'set_audio_volume',
            source: this.source,
            volume: volume,
          });
        },
      },
    }
  ),
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
.volume {
  padding-top: 1rem;
}
.volume-badge {
  font-size: 1.2rem;
}
</style>
