<script setup>
import CRUDProvider from "../generic/crud/CRUDProvider.vue";

import CreateButton from "../generic/buttons/CreateButton.vue";
import EditButton from "../generic/buttons/EditButton.vue";
import InviteButton from "../generic/buttons/InviteButton.vue";
import SexSelect from "../generic/forms/SexSelect.vue";
import GroupChip from "../group/GroupChip.vue";
import TableLink from "../generic/TableLink.vue";
</script>

<template>
  <c-r-u-d-provider :object-schema="{ type: 'PersonType' }" disable-inline-edit>
    <template #additionalActions>
      <invite-button :to="{ name: 'core.invite_person' }" />
      <create-button
        color="secondary"
        :to="{
          name: 'core.persons',
          query: { _ui_action: 'create' },
        }"
        :disabled="$route.query._ui_action === 'create'"
      />
    </template>

    <template #filters="{ propsForField }">
      <v-text-field v-bind="propsForField('name')" :label="$t('person.name')" />
      <v-text-field
        v-bind="propsForField('contact')"
        :label="$t('person.details')"
      />
      <sex-select
        v-bind="propsForField('sex')"
        :label="$t('person.sex.field')"
      />
    </template>

    <template #item.lastName="{ item }">
      <table-link :to="{ name: 'core.personById', params: { id: item.id } }">
        {{ item.lastName }}
      </table-link>
    </template>

    <template #item.firstName="{ item }">
      <table-link :to="{ name: 'core.personById', params: { id: item.id } }">
        {{ item.firstName }}
      </table-link>
    </template>

    <template #item.shortName="{ item }">
      <table-link :to="{ name: 'core.personById', params: { id: item.id } }">
        {{ item.shortName }}
      </table-link>
    </template>

    <template #item.primaryGroup="{ item }">
      <group-chip :group="item.primaryGroup" v-if="item.primaryGroup" />
      <span v-else>–</span>
    </template>

    <template #actions="{ item }">
      <edit-button
        v-if="'canEdit' in item && item.canEdit"
        icon
        variant="text"
        color="secondary"
        :to="{
          name: 'core.personById',
          params: { id: item.id },
          query: { _ui_action: 'edit' },
        }"
      />
    </template>
  </c-r-u-d-provider>
</template>
