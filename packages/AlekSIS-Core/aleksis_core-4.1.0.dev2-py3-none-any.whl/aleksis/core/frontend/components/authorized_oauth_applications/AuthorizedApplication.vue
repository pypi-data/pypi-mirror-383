<template>
  <v-expansion-panel>
    <v-expansion-panel-title v-slot="{ open }">
      <div class="d-flex justify-start align-center">
        <v-avatar
          x-large
          v-if="accessToken.application.icon.absoluteUrl"
          class="mr-4"
        >
          <img
            :src="accessToken.application.icon.absoluteUrl"
            :alt="accessToken.application.name"
          />
        </v-avatar>
        <v-avatar x-large v-else class="mr-4" color="secondary">
          <v-icon color="on-secondary">mdi-apps</v-icon>
        </v-avatar>
        <div class="text-subtitle-1 font-weight-medium">
          {{ accessToken.application.name }}
        </div>
      </div>
    </v-expansion-panel-title>
    <v-expansion-panel-text>
      <v-list density="compact" class="pa-0">
        <v-list-item>
          {{
            $t("oauth.authorized_application.access_since", {
              date: $d($parseISODate(accessToken.created), "longNumeric"),
            })
          }}
          ·
          {{
            $t("oauth.authorized_application.valid_until", {
              date: $d($parseISODate(accessToken.expires), "longNumeric"),
            })
          }}
          <v-list-item-action>
            <v-btn color="primary" @click="deleteItem(accessToken)">
              {{ $t("oauth.authorized_application.revoke") }}
            </v-btn>
          </v-list-item-action>
        </v-list-item>
        <v-list-item v-if="accessToken.scopes && accessToken.scopes.length > 0">
          <div class="pr-4">
            {{ $t("oauth.authorized_application.has_access_to") }}
          </div>
          <v-list density="compact" class="pa-0 flex-grow-1">
            <div v-for="(scope, idx) in accessToken.scopes" :key="scope.name">
              <v-list-item>
                {{ scope.description }}
              </v-list-item>
              <v-divider v-if="idx < accessToken.scopes.length - 1" />
            </div>
          </v-list>
        </v-list-item>
      </v-list>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script>
export default {
  name: "AuthorizedApplication",
  props: {
    accessToken: {
      type: Object,
      required: true,
    },
  },
  emits: ["delete-item"],
  methods: {
    deleteItem(item) {
      this.$emit("delete-item", item);
    },
  },
};
</script>
