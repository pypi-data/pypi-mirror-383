<template>
  <div>
    <v-row class="align-center">
      <v-col
        v-if="!noAvatar"
        cols="5"
        sm="4"
        md="3"
        lg="2"
        xl="1"
        order="first"
        max-width="220px"
      >
        <slot name="avatarContent" />
      </v-col>

      <v-col order="last" order-sm="1" cols="12" sm="">
        <h1>
          <slot name="title" />
        </h1>

        <div class="text-h5 text-grey-darken-2">
          <slot name="subtitle" />
        </div>
      </v-col>

      <v-col order="1" order-sm="last" class="ms-5">
        <slot
          name="actions"
          :classes="'d-flex gap justify-md-end flex-column-reverse flex-md-row align-end align-md-center'"
        />
      </v-col>
    </v-row>
    <slot />
  </div>
</template>

<script>
export default {
  name: "DetailView",
  props: {
    noAvatar: {
      type: Boolean,
      required: false,
    },
  },
};
</script>

<style>
.gap {
  gap: 0.5rem;
}
</style>
