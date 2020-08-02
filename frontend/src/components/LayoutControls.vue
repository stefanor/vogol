<template>
  <div class="card">
    <div class="card-header">
      Layout
      <div class="current-layout badge badge-info">{{ layout_name }}</div>
    </div>
    <div class="card-body">
      <button
        v-for="layout in layouts"
        v-bind:key="layout.id"
        class="btn btn-secondary"
        v-bind:disabled="composite_mode == layout.id"
        v-on:click="set_mode(layout.id)"
      >
        <img v-bind:src="layout.svg" v-bind:alt="layout.name" />
      </button>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex';
import fullscreen_svg from '../img/composite-fullscreen.svg';
import picture_in_picture_svg from '../img/composite-picture-in-picture.svg';
import side_by_side_equal_svg from '../img/composite-side-by-side-equal.svg';
import side_by_side_preview_svg from '../img/composite-side-by-side-preview.svg';

export default {
  data: () => ({
    layouts: [
      {
        id: 'fullscreen',
        svg: fullscreen_svg,
        name: 'Full Screen',
        key: 'F1',
      },
      {
        id: 'side_by_side_equal',
        svg: side_by_side_equal_svg,
        name: 'Side by Side',
        key: 'F2',
      },
      {
        id: 'side_by_side_preview',
        svg: side_by_side_preview_svg,
        name: 'Side by Side Preview',
        key: 'F3',
      },
      {
        id: 'picture_in_picture',
        svg: picture_in_picture_svg,
        name: 'Picture in Picture',
        key: 'F4',
      },
    ],
  }),
  computed: mapState({
    composite_mode: state => state.voctomix.composite_mode,
    layout_name() {
      const layout = this.layouts.find(
        layout => layout.id == this.composite_mode
      );
      if (layout) {
        return layout.name;
      }
    },
  }),
  methods: {
    on_key_down(ev) {
      const layout = this.layouts.find(layout => layout.key == ev.key);
      if (layout) {
        ev.preventDefault();
        this.set_mode(layout.id);
      }
    },
    set_mode(mode) {
      const action = 'set_composite_mode';
      this.$store.dispatch('voctomix_action', {action, mode});
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
div.current-layout {
  float: right;
  padding: 0.4em;
  margin: 0.1em;
}
</style>
