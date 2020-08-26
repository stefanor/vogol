<template>
  <button class="btn btn-primary" v-on:click="apply" v-bind:disabled="active">
    {{ preset.name }}
  </button>
</template>

<script>
import {mapState} from 'vuex';

export default {
  props: ['preset_id'],
  computed: mapState({
    active(state) {
      if (state.voctomix.video_a !== this.preset.video_a) {
        return false;
      }
      if (
        this.preset.video_b &&
        state.voctomix.video_b !== this.preset.video_b
      ) {
        return false;
      }
      if (state.voctomix.composite_mode !== this.preset.composite_mode) {
        return false;
      }
      for (const [source, level] of Object.entries(state.voctomix.audio)) {
        if (this.preset.audio_solo.indexOf(source) !== -1) {
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
    },
    preset(state) {
      return state.presets.presets[this.preset_id];
    },
  }),
  methods: {
    apply() {
      this.$store.dispatch('voctomix_action', {
        action: 'preset',
        preset: this.preset_id,
      });
    },
  },
};
</script>
