<script setup></script>

<template>
  <v-color-input v-bind="$attrs" :modes="['hex']" mode="hex" />
</template>

<style>
.v-overlay:has(> .v-overlay__content > .v-color-picker) {
  z-index: 9999 !important;
}
</style>
