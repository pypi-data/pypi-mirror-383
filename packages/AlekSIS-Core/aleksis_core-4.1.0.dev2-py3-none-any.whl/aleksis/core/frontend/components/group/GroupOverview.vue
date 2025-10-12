<script>
import ObjectOverview from "../generic/ObjectOverview.vue";
import { groupById } from "./groups.graphql";
import PersonCollection from "../person/PersonCollection.vue";
import GroupPropertiesCard from "./GroupPropertiesCard.vue";
import GroupStatisticsCard from "./GroupStatisticsCard.vue";
import GroupAvatarClickBox from "./GroupAvatarClickbox.vue";
import { collections } from "aleksisAppImporter";
import GroupActions from "./GroupActions.vue";

export default {
  name: "GroupOverview",
  components: {
    GroupActions,
    GroupAvatarClickBox,
    GroupPropertiesCard,
    PersonCollection,
    ObjectOverview,
    GroupStatisticsCard,
  },
  data() {
    return {
      query: groupById,
      tabIndex: 0,
    };
  },
  props: {
    id: {
      type: String,
      required: false,
      default: null,
    },
  },
  computed: {
    tabs() {
      return collections.coreGroupOverview.items;
    },
    tabSlug() {
      return this.$hash;
    },
  },
  mounted() {
    const tab = this.tabs.findIndex((tab) => tab.tab.id === this.tabSlug);

    if (tab >= 0 && this.tabIndex !== tab) {
      this.tabIndex = tab;
    }
  },
  watch: {
    tabSlug(newValue) {
      const tab = this.tabs.findIndex((tab) => tab.tab.id === newValue);

      if (tab >= 0 && this.tabIndex !== tab) {
        this.tabIndex = tab;
      }
    },
    tabIndex(value) {
      const tabSlug = this.tabs[value].tab.id;

      if (this.tabSlug !== tabSlug) {
        this.$router.push({
          ...this.$route,
          hash: "#" + tabSlug,
        });
      }
    },
  },
};
</script>

<template>
  <div>
    <object-overview :query="query" title-attr="name" :id="id">
      <template #loading>
        <v-skeleton-loader type="article" />

        <v-row>
          <v-col cols="12" lg="4" v-for="idx in 3" :key="idx">
            <v-skeleton-loader type="card" />
          </v-col>
        </v-row>
      </template>

      <template #default="group">
        <detail-view>
          <template #avatarContent>
            <group-avatar-click-box :url="group.avatarUrl || ''" />
          </template>

          <template #title> {{ group.name }} {{ group.lastName }} </template>

          <template #subtitle>
            <span v-if="group.shortName">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ group.shortName }}</span>
                </template>
                <span>{{ $t("group.short_name") }}</span>
              </v-tooltip>
            </span>
            <span v-if="group.shortName && group.schoolTerm"> · </span>
            <span v-if="group.schoolTerm">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props">{{ group.schoolTerm.name }}</span>
                </template>
                <span>{{ $t("group.school_term") }}</span>
              </v-tooltip>
            </span>
          </template>

          <template #actions="{ classes }">
            <group-actions :group="group" :class="classes" />
          </template>

          <v-row>
            <v-col cols="12" md="6" lg="4">
              <group-properties-card :group="group" />
            </v-col>
            <v-col cols="12" md="6" lg="4">
              <v-card>
                <v-card-title>{{ $t("group.ownership") }}</v-card-title>
                <person-collection :persons="group.owners" />
              </v-card>
            </v-col>
            <v-col cols="12" md="6" lg="4">
              <group-statistics-card :group="group" />
            </v-col>

            <v-col cols="12">
              <v-card>
                <v-row>
                  <v-col cols="12" md="6" order-md="2">
                    <v-tabs grow v-model="tabIndex">
                      <v-tab v-for="tab in tabs" :key="tab.tab.id">
                        {{ $t(tab.tab.titleKey) }}
                      </v-tab>
                    </v-tabs>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-card-title>
                      {{ $t(tabs[tabIndex].titleKey) }}
                    </v-card-title>
                  </v-col>
                </v-row>

                <v-tabs-window v-model="tabIndex">
                  <v-tabs-window-item v-for="tab in tabs" :key="tab.tab.id">
                    <v-card flat>
                      <component
                        :is="tab.component"
                        :group="group"
                        :school-term="group.schoolTerm"
                      />
                    </v-card>
                  </v-tabs-window-item>
                </v-tabs-window>
              </v-card>
            </v-col>
          </v-row>
        </detail-view>
      </template>
    </object-overview>
  </div>
</template>

<style scoped></style>
