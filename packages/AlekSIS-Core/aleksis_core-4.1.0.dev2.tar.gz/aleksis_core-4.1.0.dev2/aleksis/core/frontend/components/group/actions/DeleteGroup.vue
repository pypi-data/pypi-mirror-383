<script>
import CRUDProvider from "../../generic/crud/CRUDProvider.vue";
import groupActionsMixin from "./groupActionsMixin";
import { useRouter } from "@/vue-router";

const router = useRouter();

export default {
  name: "DeleteGroup",
  components: { CRUDProvider },
  mixins: [groupActionsMixin],
  data() {
    return {
      deleteItems: false,
    };
  },
  methods: {
    handleDeleteDone() {
      this.deleteItems = false;
      router.push({
        name: "core.groups",
      });
    },
  },
};
</script>

<template>
  <v-list-item @click="deleteItems = true" class="text-error">
    <template #prepend>
      <v-icon color="error">$deleteContent</v-icon>
    </template>

    <v-list-item-title>
      {{ $t("actions.delete") }}
    </v-list-item-title>

    <c-r-u-d-provider
      disable-query
      disable-create
      disable-patch
      :object-schema="{ type: 'GroupType' }"
      name-attribute="name"
      :delete-items="deleteItems"
      @delete-done="handleDeleteDone"
    />
  </v-list-item>
</template>

<style scoped></style>
