<script>
import mutateMixin from "../../mixins/mutateMixin";
import { deactivateAuthenticator } from "./twoFactor.graphql";
import twoFactorDialogMixin from "./twoFactorDialogMixin";

export default {
  name: "DeactivateAuthenticatorDialog",
  mixins: [mutateMixin, twoFactorDialogMixin],
  data() {
    return {
      uiAction: "deactivate",
    };
  },
  methods: {
    deactivate() {
      this.mutate(deactivateAuthenticator, {
        id: this.$route.query.id,
      });
    },
  },
};
</script>

<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-card-title>
        {{ $t("accounts.two_factor.deactivate.title") }}
      </v-card-title>
      <v-card-text>
        {{ $t("accounts.two_factor.deactivate.description") }}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <secondary-action-button
          color="error"
          @click="dialog = false"
          :loading="loading"
          :disabled="loading"
          i18n-key="actions.abort"
        />
        <primary-action-button
          color="error"
          @click="deactivate"
          :loading="loading"
          :disabled="loading"
          i18n-key="accounts.two_factor.deactivate.button"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped></style>
