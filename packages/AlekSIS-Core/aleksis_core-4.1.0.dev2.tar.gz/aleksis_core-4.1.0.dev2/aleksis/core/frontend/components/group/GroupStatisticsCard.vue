<script>
export default {
  name: "GroupStatisticsCard",
  props: {
    group: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <v-card>
    <v-card-title>{{ $t("group.statistics.title") }}</v-card-title>

    <v-list>
      <v-list-item prepend-icon="mdi-file-account-outline">
        <v-list-item-title>
          {{ $t("group.statistics.members_n", group.statistics.members) }}
        </v-list-item-title>
      </v-list-item>
      <v-divider inset />

      <v-list-item
        v-if="group.statistics.ageRangeMin !== group.statistics.ageRangeMax"
        prepend-icon="mdi-calendar-range-outline"
      >
        <v-list-item-title>
          {{
            $t("group.statistics.age_range_from_to", {
              min: group.statistics.ageRangeMin,
              max: group.statistics.ageRangeMax,
            })
          }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("group.statistics.age_range") }}
        </v-list-item-subtitle>
      </v-list-item>
      <v-divider inset />

      <v-list-item prepend-icon="mdi-cake-variant-outline">
        <v-list-item-title>
          {{
            $t("time.years_n", group.statistics.ageAvg, {
              n: $n(group.statistics.ageAvg),
            })
          }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("group.statistics.age_average") }}
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<style scoped></style>
