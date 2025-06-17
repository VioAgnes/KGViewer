<template>
  <div class="app-container">
    <KnowledgeGraph />
  </div>
</template>

<script lang="ts" setup>
import KnowledgeGraph from './components/KnowledgeGraph.vue';
</script>

<style>
.app-container {
  width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
}

body {
  margin: 0;
  padding: 0;
}
</style>
