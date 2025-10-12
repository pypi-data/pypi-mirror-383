<template>
  <div>
    <edit-button
      v-if="group.canEdit"
      color="primary"
      :to="{ name: 'core.editGroup', params: { id: group.id } }"
    />

    <button-menu
      :close-on-content-click="false"
      v-if="actions.length"
      icon-only
      text-translation-key="actions.more_actions"
    >
      <component
        :is="action.component"
        v-for="action in actions"
        :key="action.key"
        :group="group"
      />
    </button-menu>
  </div>
</template>

<script>
import EditButton from "../generic/buttons/EditButton.vue";
import { collections } from "aleksisAppImporter";
import groupActionsMixin from "./actions/groupActionsMixin";

export default {
  name: "GroupActions",
  components: { EditButton },
  mixins: [groupActionsMixin],
  computed: {
    actions() {
      return collections.coreGroupActions.items.filter((action) =>
        action.isActive.call(this, this.group),
      );
    },
  },
};
</script>
