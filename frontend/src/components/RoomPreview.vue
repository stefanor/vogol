<template>
  <div class="card">
    <div class="card-header">
      Mixed Output
    </div>
    <div class="card-body">
      <div class="stream-blanked badge badge-danger" v-if="blank">
        Stream Blanked
      </div>
      <VideoPreview room="room" />
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex';
import VideoPreview from './VideoPreview.vue';

export default {
  components: {
    VideoPreview,
  },
  computed: mapState({
    blank: state => state.voctomix.stream_status != 'live',
  }),
};
</script>
<style>
.stream-blanked {
  position: absolute;
}
</style>
