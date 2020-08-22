<template>
  <div class="preview">
    <img
      v-bind:class="{stale: isStale, room: isRoom, source: isSource}"
      v-bind:src="preview"
    />
    <div class="audio-level-bg" v-bind:class="{room: isRoom, source: isSource}">
      <div class="vu-wrapper" v-bind:class="{room: isRoom, source: isSource}">
        <div class="vu-rms" v-bind:style="{height: audio_rms + '%'}"></div>
        <div class="vu-peak" v-bind:style="{top: audio_peak + '%'}"></div>
      </div>
    </div>
  </div>
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
    audio_peak(state) {
      const level = state.previews.audio_levels[this.room];
      if (level) {
        const db = level.peak;
        return 100 - 10 ** (db / 20) * 80;
      }
    },
    audio_rms(state) {
      const level = state.previews.audio_levels[this.room];
      if (level) {
        const db = level.rms;
        return 100 - 10 ** (db / 20) * 80;
      }
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
};
</script>

<style>
div.preview {
  display: flex;
  flex-direction: row;
  border: 0.2rem solid #000000ff;
  background: black;
  margin: 0.5rem;
}

div.preview img.room {
  width: 320px;
}

div.preview img.source {
  width: 240px;
}

div.preview .room {
  height: 180px;
}

div.preview .source {
  height: 135px;
}

img.stale {
  opacity: 0.5;
  background: red;
  border-color: red;
}

div.audio-level-bg {
  display: block;
  background: rgb(0, 1, 232);
  background: linear-gradient(
    0deg,
    rgba(0, 1, 232, 1) 0%,
    rgba(0, 105, 75, 1) 80%,
    rgba(0, 255, 33, 1) 90%,
    rgba(255, 0, 0, 1) 100%
  );
  width: 10px;
}

div.vu-wrapper {
  position: absolute;
  width: 10px;
}

div.vu-rms {
  position: absolute;
  display: block;
  top: 0px;
  background: black;
  width: 100%;
}
div.vu-peak {
  display: block;
  position: absolute;
  background: red;
  width: 100%;
  height: 2px;
}
</style>
