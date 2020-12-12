<template>
  <div class="card connected-users">
    <div class="card-header">Logged in as {{ username }}</div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item">Online: {{ connected_users.join(', ') }}</li>
      <li
        class="list-group-item actions"
        v-for="(actions, bunch_index) in recent_actions"
        v-bind:key="bunch_index"
      >
        {{ actions.timestamp.toLocaleTimeString() }}
        {{ actions.username }}:
        <span
          class="badge"
          v-bind:class="{
            'badge-info': action.type == 'voctomix',
            'badge-warning': action.type == 'player',
          }"
          v-for="(action, action_index) in actions.actions"
          v-bind:key="action_index"
          v-bind:title="JSON.stringify(action.action)"
        >
          <span v-if="action.action.source">
            {{ action.action.action }}: {{ action.action.source }}
          </span>
          <span v-else-if="action.action.preset">
            {{ action.action.action }}: {{ action.action.preset }}
          </span>
          <span v-else-if="action.action.after_playback">
            {{ action.action.action }}:
            <span v-if="action.action.after_playback.source">
              Source: {{ action.action.after_playback.source }}
            </span>
            <span v-else-if="action.action.after_playback.preset">
              Preset: {{ action.action.after_playback.preset }}
            </span>
          </span>
          <span v-else>
            {{ action.action.action }}
          </span>
        </span>
      </li>
    </ul>
  </div>
</template>

<script>
import {mapState} from 'vuex';
export default {
  computed: mapState({
    connected_users: state => state.users.connected_users,
    recent_actions: state => state.users.recent_actions,
    username: state => state.auth.username,
  }),
};
</script>

<style>
.connected-users li.actions {
  max-width: 50rem;
  white-space: nowrap;
  overflow: hidden;
}
</style>
