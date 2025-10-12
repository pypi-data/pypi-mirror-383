<template>
  <div>
    <v-list-item v-for="i in numberOfDays" :key="'i-' + i">
      <v-list-item-title>
        <v-skeleton-loader type="heading" />
      </v-list-item-title>
      <v-list max-width="100%">
        <v-list-item v-for="j in numberOfItems" :key="'j-' + j">
          <slot name="itemLoader" />
        </v-list-item>
      </v-list>
    </v-list-item>
  </div>
</template>
<script>
export default {
  name: "DateItemsLoader",
  props: {
    numberOfDays: {
      type: Number,
      required: false,
      default: 1,
    },
    numberOfItems: {
      type: Number,
      required: false,
      default: 1,
    },
  },
};
</script>
