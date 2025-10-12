<template>
  <v-row>
    <v-col sm="0" md="1" lg="2" xl="3" />
    <v-col sm="12" md="10" lg="8" xl="6">
      <slot></slot>
    </v-col>
    <v-col sm="0" md="1" lg="2" xl="3" />
  </v-row>
</template>

<script>
export default {
  name: "SmallContainer",
};
</script>
