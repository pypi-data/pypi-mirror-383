<script setup>
import CRUDProvider from "../generic/crud/CRUDProvider.vue";
import DateField from "../generic/forms/DateField.vue";
</script>

<template>
  <c-r-u-d-provider :object-schema="{ type: 'SchoolTermType' }">
    <template #filters="{ propsForField }">
      <date-field
        v-bind="propsForField('dateEnd', 'gte')"
        :label="$t('school_term.after')"
      />

      <date-field
        v-bind="propsForField('dateStart', 'lte')"
        :label="$t('school_term.before')"
      />
    </template>
  </c-r-u-d-provider>
</template>
