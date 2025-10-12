<script setup>
import FilteredCalendarSelect from "../calendar/FilteredCalendarSelect.vue";
import NoCalendarEventCard from "../calendar/NoCalendarEventCard.vue";
</script>

<template>
  <div>
    <v-row>
      <v-dialog
        v-model="selectDialog"
        fullscreen
        :scrim="false"
        transition="dialog-bottom-transition"
      >
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>{{
              $t("free_busy.overview.select")
            }}</v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <filtered-calendar-select
            v-model="selected"
            :types="types"
            :items="items"
            search-placeholder-key="free_busy.overview.search"
            multiple
            @input="selectDialog = false"
          />
        </v-card>
      </v-dialog>

      <v-col md="3" lg="3" xl="3" v-if="$vuetify.display.lgAndUp">
        <v-card>
          <filtered-calendar-select
            v-model="selected"
            :types="types"
            :items="items"
            search-placeholder-key="free_busy.overview.search"
            multiple
          />
        </v-card>
      </v-col>
      <v-col sm="12" md="12" lg="9" xl="9" class="full-height">
        <no-calendar-event-card
          v-if="
            !selected || (!selectedGroups.length && !selectedPersons.length)
          "
          title-key="free_busy.overview.no_selection.title"
          description-key="free_busy.overview.no_selection.description"
          select-button-key="free_busy.overview.select"
          @select-calendar="selectDialog = true"
        />

        <!-- Calendar card-->
        <v-card v-else>
          <div class="d-flex justify-center" v-if="$vuetify.display.smAndDown">
            <v-card-title class="pt-2">
              <v-chip
                variant="outlined"
                color="secondary"
                @click="selectDialog = true"
              >
                {{ selectedNames }}
                <v-icon end>mdi-chevron-down</v-icon>
              </v-chip>
            </v-card-title>
          </div>

          <calendar-with-controls
            :calendar-feeds="[{ name: 'free_busy' }]"
            :params="{
              persons: selectedPersons.map((p) => p.id),
              groups: selectedGroups.map((g) => g.id),
            }"
            :start-with-first-time="false"
          />
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import freeBusyFeedTypes from "./freeBusyFeedTypes";
import { gqlGroups, gqlPersons } from "./helpers.graphql";

export default {
  name: "FreeBusyOverview",
  data() {
    return {
      persons: [],
      groups: [],
      selected: [],
      selectDialog: false,
      types: freeBusyFeedTypes,
    };
  },
  apollo: {
    persons: {
      query: gqlPersons,
    },
    groups: {
      query: gqlGroups,
    },
  },
  computed: {
    items() {
      return [
        ...this.persons.map((p) => ({
          ...p,
          uid: `person-${p.id}`,
          type: "PERSON",
        })),
        ...this.groups.map((g) => ({
          ...g,
          uid: `group-${g.id}`,
          type: "GROUP",
        })),
      ];
    },
    selectedPersons() {
      return this.selected.filter((i) => i.type === "PERSON");
    },
    selectedGroups() {
      return this.selected.filter((i) => i.type === "GROUP");
    },
    selectedNames() {
      return [
        ...this.selectedPersons.map((p) => p.fullName),
        ...this.selectedGroups.map((g) => g.shortName),
      ].join("; ");
    },
  },
};
</script>

<style scoped></style>
