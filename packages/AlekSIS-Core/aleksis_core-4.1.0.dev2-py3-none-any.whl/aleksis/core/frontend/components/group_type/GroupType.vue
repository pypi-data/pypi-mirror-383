<script setup>
import CRUDProvider from "../generic/crud/CRUDProvider.vue";
import RoleChip from "../role/RoleChip.vue";
import i18n from "../../app/i18n";

// TODO: Generate this from ObjectSchema
const allowedInformationChoices = [
  {
    value: "personal_details",
    name: i18n.global.t("group_type.allowed_information.personal_details"),
  },
  {
    value: "address",
    name: i18n.global.t("group_type.allowed_information.address"),
  },
  {
    value: "contact_details",
    name: i18n.global.t("group_type.allowed_information.contact_details"),
  },
  {
    value: "photo",
    name: i18n.global.t("group_type.allowed_information.photo"),
  },
  {
    value: "avatar",
    name: i18n.global.t("group_type.allowed_information.avatar"),
  },
  {
    value: "groups",
    name: i18n.global.t("group_type.allowed_information.groups"),
  },
];
</script>

<template>
  <c-r-u-d-provider
    :object-schema="{ type: 'GroupTypeType' }"
    disable-inline-edit
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #ownersCanSeeMembersAllowedInformation.field="props">
      <v-autocomplete
        v-bind="props"
        chips
        multiple
        item-value="value"
        item-title="name"
        :items="allowedInformationChoices"
      />
    </template>

    <template #item.attributes="{ item }">
      <v-chip
        class="mr-2 mb-1"
        size="small"
        color="secondary"
        v-if="item.ownersCanSeeGroups"
      >
        <v-icon start size="small">mdi-check-circle-outline</v-icon>
        {{ $t("group.group_type.owners_can_see_groups") }}</v-chip
      >

      <v-chip
        class="mr-2 mb-1"
        size="small"
        color="secondary"
        v-if="item.ownersCanSeeMembers"
      >
        <v-icon start size="small">mdi-check-circle-outline</v-icon>
        {{ $t("group.group_type.owners_can_see_members") }}
        <template v-if="item.ownersCanSeeMembersAllowedInformation.length > 0">
          {{
            $t("group.group_type.owners_can_see_members_including", {
              allowedInformation: item.ownersCanSeeMembersAllowedInformation
                .map((value) =>
                  $t(`group.group_type.allowed_information.${value}`),
                )
                .join(", "),
            })
          }}
        </template>
      </v-chip>
    </template>

    <template #item.availableRoles="{ item }">
      <role-chip
        v-for="r in item.availableRoles"
        :key="r.id"
        :role="r"
        class="mr-1"
      />
      <span v-if="item.availableRoles.length === 0">–</span>
    </template>
  </c-r-u-d-provider>
</template>
