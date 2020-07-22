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
  computed: mapState({
    isRoom() {
      return this.room == 'room';
    },
    isSource() {
      return this.room != 'room';
    },
    preview(state) {
      const preview = state.previews[this.room];
      if (preview) {
        return URL.createObjectURL(preview);
      }
    },
    isStale(state) {
      return !state.preview_is_current[this.room];
    },
  }),
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
