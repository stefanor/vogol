<template>
  <div class="card">
    <div class="card-header">Logged in as {{ username }}</div>
    <ul class="list-group list-group-flush">
      <li class="list-group-item">Online: {{ connected_users.join(', ') }}</li>
    </ul>
  </div>
</template>

<script>
import {mapState} from 'vuex';
export default {
  computed: mapState({
    connected_users: state => state.users.connected_users,
    username: state => state.users.username,
  }),
};
</script>
