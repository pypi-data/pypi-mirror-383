<script setup></script>

<template>
  <v-switch
    v-bind="$attrs"
    inset
    :false-value="false"
    :true-value="true"
    persistent-hint
  />
</template>
