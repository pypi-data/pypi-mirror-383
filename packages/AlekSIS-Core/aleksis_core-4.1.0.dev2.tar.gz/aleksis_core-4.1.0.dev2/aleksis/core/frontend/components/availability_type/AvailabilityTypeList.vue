<script setup>
import CRUDProvider from "../generic/crud/CRUDProvider.vue";
</script>

<template>
  <c-r-u-d-provider
    :object-schema="{ type: 'AvailabilityTypeType' }"
    disable-inline-edit
  />
</template>
