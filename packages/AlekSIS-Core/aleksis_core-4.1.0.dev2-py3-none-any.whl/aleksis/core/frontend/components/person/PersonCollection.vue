<template>
  <v-list v-if="persons.length">
    <v-list-item
      v-for="person in persons"
      :key="person.id"
      :to="{ name: 'core.personById', params: { id: person.id } }"
    >
      <template #prepend>
        <v-avatar>
          <avatar-content :id="person.id" />
        </v-avatar>
      </template>

      <v-list-item-title>{{ person.fullName }}</v-list-item-title>
    </v-list-item>
  </v-list>
  <v-list v-else>
    <v-list-item>
      <v-list-item-title>
        {{ $t("person.no_persons") }}
      </v-list-item-title>
    </v-list-item>
  </v-list>
</template>

<script>
import AvatarContent from "./AvatarContent.vue";

export default {
  name: "PersonList",
  components: { AvatarContent },
  props: {
    persons: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped></style>
