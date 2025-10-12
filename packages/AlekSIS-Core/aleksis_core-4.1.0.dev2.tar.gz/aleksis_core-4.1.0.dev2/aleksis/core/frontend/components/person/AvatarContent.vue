<template>
  <div class="fullsize">
    <template v-if="$apollo.queries.person.loading">
      <v-row class="fill-height ma-0" align="center" justify="center">
        <v-progress-circular
          indeterminate
          color="grey-lighten-5"
        ></v-progress-circular>
      </v-row>
    </template>
    <v-img
      v-else-if="person?.image || imageUrl"
      :src="person?.image || imageUrl"
      :alt="$t('person.avatar')"
      max-width="100%"
      max-height="100%"
      :cover="contain"
      class="fullsize"
    />
    <v-icon class="bg-grey-lighten-1" v-else>mdi-image-off-outline</v-icon>
  </div>
</template>

<script>
import gqlAvatarContent from "./avatarContent.graphql";
export default {
  name: "AvatarContent",
  props: {
    id: {
      type: String,
      required: false,
      default: "",
    },
    contain: {
      type: Boolean,
      required: false,
      default: false,
    },
    imageUrl: {
      type: String,
      required: false,
      default: null,
    },
  },
  apollo: {
    person: {
      query: gqlAvatarContent,
      variables() {
        return {
          id: this.id,
        };
      },
      skip() {
        return !!this.imageUrl;
      },
    },
  },
};
</script>

<style scoped></style>
