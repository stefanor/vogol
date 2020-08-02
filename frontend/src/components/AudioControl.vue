<template>
  <div class="audio-control">
    <div class="volume">
      <b-popover
        v-bind:target="'volume-badge-' + source"
        triggers="hover"
        placement="top"
        title="Fader (dB)"
      >
        <b-form-input
          type="range"
          v-model="volume_db"
          step="0.5"
          min="-20"
          max="10"
        ></b-form-input>
      </b-popover>
      <div
        class="badge badge-info"
        v-bind:id="'volume-badge-' + source"
        v-bind:class="[muted ? 'badge-danger' : 'badge-success']"
      >
        <b-icon-volume-mute-fill scale="1.5" v-if="muted" />
        <b-icon-volume-up-fill scale="1.5" v-else />
        {{ volume_db }} dB ({{ volume_percent }} %)
      </div>
    </div>
    <button
      class="btn btn-danger"
      v-bind:disabled="muted"
      v-on:click="send('mute')"
    >
      Mute
    </button>
    <button
      class="btn btn-success"
      v-bind:disabled="unity"
      v-on:click="send('unmute')"
    >
      0 db
    </button>
  </div>
</template>

<script>
import {
  BFormInput,
  BIconVolumeUpFill,
  BIconVolumeMuteFill,
  BPopover,
} from 'bootstrap-vue';

export default {
  props: ['source'],
  components: {
    BFormInput,
    BIconVolumeUpFill,
    BIconVolumeMuteFill,
    BPopover,
  },
  computed: {
    muted() {
      return this.volume < 0.2;
    },
    unity() {
      return this.volume == 1;
    },
    volume() {
      return this.$store.state.voctomix.audio[this.source];
    },
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
    volume_percent() {
      const volume_percent = Math.trunc(this.volume * 100);
      return volume_percent;
    },
  },
  methods: {
    send(action) {
      const source = this.source;
      this.$store.dispatch('voctomix_action', {action, source});
    },
  },
};
</script>

<style>
.audio-control {
  padding-top: 1em;
}

.audio-control .volume {
  padding-top: 1rem;
  padding-bottom: 1rem;
}

.audio-control .badge {
  font-size: 1.2rem;
}
</style>
