<template>
  <div class="audio-control">
    <div class="volume">
      <div
        class="badge badge-info"
        v-bind:class="[muted ? 'badge-danger' : 'badge-success']"
      >
        <b-icon-volume-mute-fill scale="1.5" v-if="muted" />
        <b-icon-volume-up-fill scale="1.5" v-else />
        {{ volume }} %
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
      v-bind:disabled="!muted"
      v-on:click="send('unmute')"
    >
      Un-Mute
    </button>
  </div>
</template>

<script>
import {BIconVolumeUpFill, BIconVolumeMuteFill} from 'bootstrap-vue';
import {mapState} from 'vuex';

export default {
  props: ['source'],
  components: {
    BIconVolumeUpFill,
    BIconVolumeMuteFill,
  },
  computed: mapState({
    muted() {
      return this.volume < 20;
    },
    volume(state) {
      const volume_fraction = state.voctomix.audio[this.source];
      const volume_percent = Math.trunc(volume_fraction * 100);
      return volume_percent;
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
