<template>
  <div class="test-api-config">
    <APITestDashboard />
  </div>
</template>

<script>
import APITestDashboard from '../APITestDashboard.vue'

export default {
  name: 'APITestConfig',
  components: {
    APITestDashboard
  }
}
</script>

<style scoped>
.test-api-config {
  width: 100%;
}
</style>
