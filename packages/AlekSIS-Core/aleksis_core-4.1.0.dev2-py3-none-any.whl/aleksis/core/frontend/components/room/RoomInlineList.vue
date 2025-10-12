<!-- TODO: We should propably autogenerate files like this. -->
<script setup>
import CRUDProvider from "../generic/crud/CRUDProvider.vue";
</script>

<template>
  <c-r-u-d-provider :object-schema="{ type: 'RoomType' }" />
</template>
