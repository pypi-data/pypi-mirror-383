<script>
import AvatarContent from "../person/AvatarContent.vue";
import groupOverviewTabMixin from "../../mixins/groupOverviewTabMixin";
import SecondaryActionButton from "../generic/buttons/SecondaryActionButton.vue";
import itemsPerPageMixin from "../../mixins/itemsPerPageMixin.js";
import RoleChip from "../role/RoleChip.vue";

export default {
  name: "GroupMembers",
  components: { AvatarContent, SecondaryActionButton, RoleChip },
  mixins: [groupOverviewTabMixin, itemsPerPageMixin],
  data() {
    return {
      headers: [
        {
          text: this.$t("person.avatar"),
          align: "start",
          sortable: false,
          value: "person.avatarContentUrl",
        },
        { text: this.$t("person.first_name"), value: "person.firstName" },
        { text: this.$t("person.last_name"), value: "person.lastName" },
        { text: this.$t("person.short_name"), value: "person.shortName" },
        { text: this.$t("person.birth_date"), value: "person.dateOfBirth" },
        { text: this.$t("person.sex.field"), value: "person.sex" },
        { text: this.$t("person.email_address"), value: "person.email" },
        { text: this.$t("person.username"), value: "person.username" },
        { text: this.$t("role.title_plural"), value: "roles" },
        { align: "end", sortable: false, value: "person.id" },
      ],
    };
  },
};
</script>

<template>
  <v-data-table
    :headers="headers"
    :items="group.relationships"
    :items-per-page="itemsPerPage"
    :footer-props="footerProps"
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.person.avatarContentUrl="{ item }">
      <v-avatar class="my-1">
        <avatar-content :image-url="item.person.avatarContentUrl" />
      </v-avatar>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.person.shortName="{ item }">
      {{ item.person.shortName || "–" }}
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.person.sex="{ item }">
      {{
        item.person.sex
          ? $t("person.sex." + item.person.sex.toLowerCase())
          : "–"
      }}
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.person.dateOfBirth="{ item }">
      {{
        item.person.dateOfBirth
          ? $d($parseISODate(item.person.dateOfBirth), "short")
          : "–"
      }}
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.person.email="{ item }">
      <a v-if="item.person.email" :href="'mailto:' + item.person.email">{{
        item.person.email
      }}</a>
      <span v-else>–</span>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.person.username="{ item }">
      {{ item.person.username || "–" }}
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.person.id="{ item }">
      <v-tooltip location="bottom">
        <template #activator="{ props }">
          <secondary-action-button
            v-bind="props"
            icon
            variant="text"
            icon-text="mdi-open-in-new"
            i18n-key="actions.open_in_new"
            target="_blank"
            :to="{
              name: 'core.personById',
              params: {
                id: item.person.id,
              },
            }"
          >
          </secondary-action-button>
        </template>
        <span>{{ $t("person.view_in_new_tab", item.person) }}</span>
      </v-tooltip>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.roles="{ item }">
      <role-chip
        v-for="role in item.roles"
        :key="role.id"
        :role="role"
        class="mr-1"
      />
    </template>
  </v-data-table>
</template>

<style scoped></style>
