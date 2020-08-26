<template>
  <div>
    <div class="card" v-if="any_presets">
      <div class="card-header">Presets</div>
      <PresetControl
        v-for="(preset, id) in presets"
        v-bind:key="id"
        v-bind:preset_id="id"
      />
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex';
import PresetControl from './PresetControl';

export default {
  components: {
    PresetControl,
  },
  computed: mapState({
    any_presets: state => Object.keys(state.presets.presets).length > 0,
    presets: state => state.presets.presets,
  }),
};
</script>
