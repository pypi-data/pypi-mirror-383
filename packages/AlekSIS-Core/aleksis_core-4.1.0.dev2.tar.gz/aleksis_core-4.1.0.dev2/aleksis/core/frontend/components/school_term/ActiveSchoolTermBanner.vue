<script setup></script>

<template>
  <v-banner
    v-bind="$attrs"
    color="warning"
    icon="$warning"
    :lines="$vuetify.display.sm ? undefined : 'two'"
    :stacked="$vuetify.display.sm"
  >
    <v-banner-text>
      {{
        $t("school_term.active_school_term.warning", {
          termName: $root.activeSchoolTerm?.name,
        })
      }}
    </v-banner-text>

    <template #actions>
      <v-btn @click="$root.activeSchoolTerm = null">
        {{ $t("school_term.active_school_term.select_action") }}
      </v-btn>
    </template>
  </v-banner>
</template>
