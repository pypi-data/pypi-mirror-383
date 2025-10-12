<template>
  <router-link
    v-bind="$attrs"
    class="text-decoration-none text-primary font-weight-medium d-inline-block full-width"
  >
    <slot />
  </router-link>
</template>
<script>
export default {
  name: "TableLink",
  extends: "router-link",
};
</script>
