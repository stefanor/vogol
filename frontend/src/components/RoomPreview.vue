<template>
  <div class="card">
    <div class="card-header">Mixed Output</div>
    <div class="card-body">
      <VideoPreview room="room" />
    </div>
  </div>
</template>

<script>
import VideoPreview from './VideoPreview.vue';

export default {
  components: {
    VideoPreview,
  },
};
</script>
