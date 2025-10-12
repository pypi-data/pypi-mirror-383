<script setup>
import CRUDProvider from "../generic/crud/CRUDProvider.vue";

import CreateButton from "../generic/buttons/CreateButton.vue";
import TableLink from "../generic/TableLink.vue";
import AvatarContent from "../person/AvatarContent.vue";
import ObjectField from "../generic/crud/ObjectField.vue";
</script>

<template>
  <c-r-u-d-provider :object-schema="{ type: 'GroupType' }" disable-inline-edit>
    <template #additionalActions>
      <create-button :to="{ name: 'core.createGroup' }" />
    </template>

    <template #filters="{ propsForField }">
      <object-field v-bind="propsForField('groupType')" type="GroupTypeType" />
    </template>

    <template #item.avatarUrl="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        <v-avatar class="my-1 me-2">
          <avatar-content :image-url="item.avatarUrl" contain />
        </v-avatar>
      </table-link>
    </template>

    <template #item.name="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        {{ item.name }}
      </table-link>
    </template>

    <template #item.shortName="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        {{ item.shortName }}
      </table-link>
    </template>

    <template #item.groupType="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        {{ item.groupType?.name || "–" }}
      </table-link>
    </template>

    <template #item.schoolTerm="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        {{ item.schoolTerm?.name || "–" }}
      </table-link>
    </template>
  </c-r-u-d-provider>
</template>
