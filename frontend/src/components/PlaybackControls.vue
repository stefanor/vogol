<template>
  <div class="card">
    <div class="card-header">
      Recordings
      <b-icon-play-fill scale="1.5" v-if="playing" />
      <b-icon-stop-fill scale="1.5" v-if="stopped" />
    </div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item" v-if="stopped">
        <button class="btn btn-primary" v-b-modal.playback-file-modal>
          Select File
        </button>
      </li>
      <li class="list-group-item" v-if="file">Selected: {{ file }}</li>
      <li class="list-group-item" v-if="position">
        Position: {{ position }} / {{ duration }}
      </li>
      <li class="list-group-item" v-else-if="duration">
        Duration: {{ duration }}
      </li>
      <li class="list-group-item" v-if="playing">
        <button class="btn btn-danger" v-on:click="stop">
          <b-icon-stop-fill /> Stop
        </button>
      </li>
      <li class="list-group-item" v-if="stopped">
        <button class="btn btn-success" v-if="file" v-on:click="play">
          <b-icon-play-fill /> Play
        </button>
      </li>
    </ul>
    <b-modal
      title="Select File"
      id="playback-file-modal"
      ok-title="Load for Playback"
      v-on:ok="load_file"
      v-on:show="refresh_files"
    >
      <div class="modal-body">
        <b-form-radio
          name="select-file"
          v-model="selected_file"
          stacked
          v-for="file in files"
          v-bind:value="file"
          v-bind:key="file"
        >
          {{ file }}
        </b-form-radio>
      </div>
    </b-modal>
  </div>
</template>

<script>
import {BFormRadio, BIconPlayFill, BIconStopFill, BModal} from 'bootstrap-vue';

export default {
  data: () => ({
    selected_file: null,
  }),
  components: {
    BFormRadio,
    BIconPlayFill,
    BIconStopFill,
    BModal,
  },
  computed: {
    duration() {
      return this.$store.state.playback.duration;
    },
    file() {
      return this.$store.state.playback.file;
    },
    files() {
      return this.$store.state.playback.files;
    },
    playing() {
      return this.$store.state.playback.playback == 'playing';
    },
    position() {
      return this.$store.state.playback.position;
    },
    stopped() {
      return this.$store.state.playback.playback == 'stopped';
    },
  },
  methods: {
    load_file() {
      const file = this.selected_file;
      this.$store.dispatch('playback_action', {action: 'load', file});
    },
    play() {
      this.$store.dispatch('playback_action', {action: 'play'});
    },
    refresh_files() {
      this.$store.dispatch('refresh_files');
    },
    stop() {
      this.$bvModal
        .msgBoxConfirm(
          'Are you sure you want to stop playback? ' +
            'You will only be able to restart it from the beginning.',
          {
            title: 'Confirm stop',
            headerBgVariant: 'danger',
            okTitle: 'STOP Playback',
            okVariant: 'danger',
          }
        )
        .then(value => {
          if (value) {
            this.$store.dispatch('playback_action', {action: 'stop'});
          }
        });
    },
  },
};
</script>
