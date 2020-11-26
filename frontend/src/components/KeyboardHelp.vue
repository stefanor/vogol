<template>
  <b-modal title="Keyboard Shortcuts" id="keyboard-shortcuts" ok-only>
    <table>
      <tr>
        <th>
          <span class="badge badge-light">1</span>
        </th>
        <td>
          Select the first source from the left.
        </td>
      </tr>
      <tr>
        <th>
          <span class="badge badge-light">2</span>
        </th>
        <td>
          Select the second source from the left.
        </td>
      </tr>
      <tr>
        <th>
          <span class="badge badge-light">Ctrl+1</span>
        </th>
        <td>
          Make the first source from the left
          <span class="badge source-b">B</span>.
        </td>
      </tr>
      <tr>
        <th>
          <span class="badge badge-light">F1</span>
        </th>
        <td>
          Use the Full Screen layout.
        </td>
      </tr>
      <tr>
        <th>
          <span class="badge badge-light">F2</span>
        </th>
        <td>
          Use the Side by Side layout.
        </td>
      </tr>
      <tr>
        <th>
          <span class="badge badge-light">F3</span>
        </th>
        <td>
          Use the Side by Side Preview layout.
        </td>
      </tr>
      <tr>
        <th>
          <span class="badge badge-light">F4</span>
        </th>
        <td>
          Use the Picture in Picture layout.
        </td>
      </tr>
      <tr>
        <th>
          <span class="badge badge-light">F11</span>
        </th>
        <td>
          Stream the maintenance loop.
        </td>
      </tr>
      <tr>
        <th>
          <span class="badge badge-light">F12</span>
        </th>
        <td>
          Stream Live.
        </td>
      </tr>
    </table>
  </b-modal>
</template>

<script>
import {BModal} from 'bootstrap-vue';
export default {
  components: {
    BModal,
  },
  methods: {
    on_key_down(ev) {
      if (ev.key == '?') {
        ev.preventDefault();
        this.$bvModal.show('keyboard-shortcuts');
      }
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
