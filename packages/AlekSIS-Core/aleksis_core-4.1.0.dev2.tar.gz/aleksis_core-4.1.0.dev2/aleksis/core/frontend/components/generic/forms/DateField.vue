<script setup></script>

<template>
  <v-date-input v-bind="$attrs" show-adjacent-months />
</template>

<style>
.v-overlay:has(> .v-overlay__content > .v-date-picker) {
  z-index: 9999 !important;
}
</style>
