<template>
  <div class="card">
    <div class="card-header">Logged in as {{ username }}</div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item">Online: {{ connected_users.join(', ') }}</li>
      <li
        class="list-group-item"
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
          >{{ action.action.action }}</span
        >
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
    username: state => state.users.username,
  }),
};
</script>
