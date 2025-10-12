<template>
  <div>
    <div v-if="$apollo.queries.accessTokens.loading">
      <v-skeleton-loader type="card"></v-skeleton-loader>
    </div>
    <div v-else-if="accessTokens">
      <v-card class="mb-4">
        <v-card-title>
          {{ $t("oauth.authorized_application.subtitle") }}
        </v-card-title>
        <v-card-text>
          {{ $t("oauth.authorized_application.description") }}
        </v-card-text>
        <v-expansion-panels flat>
          <authorized-application
            v-for="(accessToken, index) in accessTokens"
            :key="accessToken.id"
            :access-token="accessToken"
            @delete-item="openDeleteDialog"
          />
        </v-expansion-panels>
      </v-card>
    </div>
    <delete-dialog
      :items="[deleteItem]"
      :gql-delete-mutation="revokeOauthTokens"
      :affected-query="$apollo.queries.accessTokens"
      v-model="deleteDialog"
    >
      <template #title>
        {{ $t("oauth.authorized_application.revoke_question") }}
      </template>
      <template #body>
        <span v-if="deleteItem">{{ deleteItem.application.name }}</span>
      </template>
      <template #deleteContent>
        {{ $t("oauth.authorized_application.revoke") }}
      </template>
    </delete-dialog>
  </div>
</template>

<script>
import gqlAccessTokens from "./accessTokens.graphql";
import AuthorizedApplication from "./AuthorizedApplication.vue";
import DeleteDialog from "../generic/dialogs/DeleteDialog.vue";
import { revokeOauthTokens } from "./revokeOauthToken.graphql";

export default {
  name: "AuthorizedApplications",
  components: { DeleteDialog, AuthorizedApplication },
  data() {
    return {
      deleteDialog: false,
      deleteItem: null,
      revokeOauthTokens,
    };
  },
  methods: {
    openDeleteDialog(item) {
      this.deleteItem = item;
      this.deleteDialog = true;
    },
  },
  apollo: {
    accessTokens: {
      query: gqlAccessTokens,
    },
  },
};
</script>
