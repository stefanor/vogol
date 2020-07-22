<template>
  <div class="card">
    <div class="card-header">Layout</div>
    <div class="card-body">
      <div v-for="layout in layouts" v-bind:key="layout.id">
        <button
          class="btn btn-info"
          v-bind:disabled="composite_mode == layout.id"
          v-on:click="set_mode(layout.id)"
        >
          {{ layout.name }}
        </button>
      </div>
      <div>Layout: {{ composite_mode }}</div>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex';

export default {
  data: () => ({
    layouts: [
      {
        id: 'fullscreen',
        name: 'Full Screen',
      },
      {
        id: 'side_by_side_equal',
        name: 'Side by Side',
      },
      {
        id: 'side_by_side_preview',
        name: 'Side by Side Preview',
      },
      {
        id: 'picture_in_picture',
        name: 'Picture in Picture',
      },
    ],
  }),
  computed: mapState({
    composite_mode: 'composite_mode',
  }),
  methods: {
    set_mode(mode) {
      const action = 'set_composite_mode';
      this.$store.dispatch('send_action', {action, mode});
    },
  },
};
</script>
