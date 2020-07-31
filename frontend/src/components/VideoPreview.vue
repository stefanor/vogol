<template>
  <img
    class="preview"
    v-bind:class="{stale: isStale, room: isRoom, source: isSource}"
    v-bind:src="preview"
  />
</template>

<script>
import {mapState} from 'vuex';

export default {
  props: ['room'],
  data: () => ({
    last_object_url: null,
  }),
  computed: mapState({
    isRoom() {
      return this.room == 'room';
    },
    isSource() {
      return this.room != 'room';
    },
    preview(state) {
      const preview = state.previews.previews[this.room];
      if (preview) {
        if (this.last_object_url) {
          URL.revokeObjectURL(this.last_object_url);
        }
        const url = URL.createObjectURL(preview);
        this.last_object_url = url;
        return url;
      }
    },
    isStale(state) {
      return !state.previews.preview_is_current[this.room];
    },
  }),
  created() {
    this.$store.dispatch('start_poller', this.room);
  },
  beforeDestroy() {
    this.$store.dispatch('stop_poller', this.room);
  },
};
</script>

<style>
img.preview {
  display: block;
  border: 0.2rem solid #000000ff;
  background: black;
  margin: 0.5rem;
}

img.room {
  width: 320px;
  height: 180px;
}

img.source {
  width: 240px;
  height: 135px;
}

img.stale {
  opacity: 0.5;
  background: red;
  border-color: red;
}
</style>
