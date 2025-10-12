<template>
  <object-overview :query="query" title-attr="fullName" :id="id" ref="overview">
    <template #loading>
      <v-skeleton-loader type="article" />

      <v-row>
        <v-col cols="12" lg="4" v-for="idx in 3" :key="idx">
          <v-skeleton-loader type="card" />
        </v-col>
      </v-row>
    </template>
    <template #default="person">
      <detail-view>
        <template #avatarContent>
          <person-avatar-clickbox :id="id" />
        </template>

        <template #title>
          {{ person.firstName }} {{ person.lastName }}
        </template>

        <template #subtitle>
          <span v-if="person.shortName">
            <v-tooltip location="bottom">
              <template #activator="{ props }">
                <span v-bind="props">{{ person.shortName }}</span>
              </template>
              <span>{{ $t("person.short_name") }}</span>
            </v-tooltip>
          </span>
          <span v-if="person.shortName && person.username"> · </span>
          <span v-if="person.username">
            <v-tooltip location="bottom">
              <template #activator="{ props }">
                <span v-bind="props">{{ person.username }}</span>
              </template>
              <span>{{ $t("person.username") }}</span>
            </v-tooltip>
          </span>
        </template>

        <template #actions="{ classes }">
          <person-actions :class="classes" :person="person" />
        </template>

        <div class="text-center my-5" v-text="person.description"></div>

        <v-row>
          <v-col cols="12" lg="4">
            <person-details-card class="mb-6" :person="person" />

            <additional-image :src="person.secondaryImageUrl" />
          </v-col>

          <v-col
            cols="12"
            md="6"
            lg="4"
            v-if="person.children.length || person.guardians.length"
          >
            <v-card v-if="person.children.length" class="mb-6">
              <v-card-title>{{ $t("person.children") }}</v-card-title>
              <person-collection :persons="person.children" />
            </v-card>
            <v-card v-if="person.guardians.length">
              <v-card-title>{{ $t("person.guardians") }}</v-card-title>
              <person-collection :persons="person.guardians" />
            </v-card>
          </v-col>

          <v-col
            cols="12"
            md="6"
            lg="4"
            v-if="person.memberOf.length || person.ownerOf.length"
          >
            <v-card>
              <v-card-title>{{ $t("group.title_plural") }}</v-card-title>
              <v-list>
                <v-list-group>
                  <template #activator="{ props }">
                    <v-list-item
                      prepend-icon="mdi-account-group-outline"
                      v-bind="props"
                      :disabled="person.memberOf.length === 0"
                      :append-icon="
                        person.memberOf.length === 0 ? null : undefined
                      "
                    >
                      <v-list-item-title>
                        {{ $t("group.member_of_n", person.memberOf.length) }}
                      </v-list-item-title>
                    </v-list-item>
                  </template>
                  <group-collection :groups="person.memberOf" dense />
                </v-list-group>
                <v-list-group>
                  <template #activator="{ props }">
                    <v-list-item
                      prepend-icon="mdi-account-tie-hat-outline"
                      v-bind="props"
                      :disabled="person.ownerOf.length === 0"
                      :append-icon="
                        person.ownerOf.length === 0 ? null : undefined
                      "
                    >
                      <v-list-item-title>
                        {{ $t("group.owner_of_n", person.ownerOf.length) }}
                      </v-list-item-title>
                    </v-list-item>
                  </template>
                  <group-collection :groups="person.ownerOf" dense />
                </v-list-group>
              </v-list>
            </v-card>
          </v-col>

          <template v-for="widget in widgets">
            <v-col
              v-if="widget.shouldDisplay(person, $root.activeSchoolTerm)"
              v-bind="widget.colProps"
              :key="widget.key"
            >
              <!-- Props defined in aleksis/core/frontend/mixins/personOverviewCardMixin.js -->
              <component
                :is="widget.component"
                :person="person"
                :school-term="$root.activeSchoolTerm"
                :maximized="widgetSlug === widget.key"
                @maximize="maximizeWidget(widget.key)"
                @minimize="minimizeWidgets()"
              />
            </v-col>
          </template>
        </v-row>
      </detail-view>
    </template>
  </object-overview>
</template>

<script>
import AdditionalImage from "./AdditionalImage.vue";
import GroupCollection from "../group/GroupCollection.vue";
import ObjectOverview from "../generic/ObjectOverview.vue";
import PersonActions from "./PersonActions.vue";
import PersonAvatarClickbox from "./PersonAvatarClickbox.vue";
import PersonCollection from "./PersonCollection.vue";
import PersonDetailsCard from "./PersonDetailsCard.vue";

import gqlPersonOverview from "./personOverview.graphql";

import { collections } from "aleksisAppImporter";

import { useAppStore } from "../../stores/appStore";

export default {
  setup() {
    return {
      appstore: useAppStore(),
    };
  },
  name: "PersonOverview",
  components: {
    AdditionalImage,
    GroupCollection,
    ObjectOverview,
    PersonActions,
    PersonAvatarClickbox,
    PersonCollection,
    PersonDetailsCard,
  },
  data() {
    return {
      query: gqlPersonOverview,
    };
  },
  props: {
    id: {
      type: String,
      required: false,
      default: null,
    },
  },
  mounted() {
    if (this.$route.name === "core.me") {
      this.$router.replace({
        name: "core.personById",
        params: { id: this.appstore.whoAmI.person.id },
        query: this.$route.query,
        hash: this.$route.hash,
      });
    }
  },
  methods: {
    maximizeWidget(slug) {
      if (this.widgetSlug !== slug) {
        if (this.id) {
          this.$router.push({
            name: "core.personById",
            params: { id: this.id },
            hash: "#" + slug,
          });
        } else {
          this.$router.push({
            name: "core.me",
            hash: "#" + slug,
          });
        }
      }
    },
    minimizeWidgets() {
      if (this.id) {
        this.$router.push({
          name: "core.personById",
          params: { id: this.id },
        });
      } else {
        this.$router.push({
          name: "core.me",
        });
      }
    },
  },
  computed: {
    widgets() {
      return collections.corePersonWidgets.items;
    },
    widgetSlug() {
      return this.$hash;
    },
  },
};
</script>

<style scoped></style>
