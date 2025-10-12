<script>
import {
  webauthnCredentialCreationOptions,
  addSecurityKey,
} from "../twoFactor.graphql";
import twoFactorDialogMixin from "../twoFactorDialogMixin";
import {
  create,
  parseCreationOptionsFromJSON,
} from "@github/webauthn-json/browser-ponyfill";
import mutateMixin from "../../../mixins/mutateMixin";

export default {
  name: "ActivateWebauthnDialog",
  mixins: [twoFactorDialogMixin, mutateMixin],
  apollo: {
    twoFactor: {
      query: webauthnCredentialCreationOptions,
      fetchPolicy: "network-only",
      skip() {
        return !this.dialogValid;
      },
      result({ data }) {
        if (this.webauthnActive) return;
        const jsonData = JSON.parse(
          data.twoFactor.webauthn.credentialCreationOptions,
        );
        const options = parseCreationOptionsFromJSON(jsonData);
        this.webauthnActive = true;
        create(options)
          .then((result) => {
            this.webauthnActive = false;
            this.webauthnCredentials = result;
          })
          .catch((e) => {
            console.error(e);
            this.webauthnActive = false;
            this.$router.push({ name: "core.twoFactor" });
          });
      },
    },
  },
  data() {
    return {
      uiAction: "activate_webauthn",
      webauthnCredentials: null,
      webauthnActive: false,
      keyName: "",
    };
  },
  methods: {
    activate() {
      if (!this.webauthnCredentials || !this.keyName) return;
      this.mutate(addSecurityKey, {
        name: this.keyName,
        credential: JSON.stringify(this.webauthnCredentials),
      });
    },
  },
  watch: {
    dialog(val) {
      if (!val) {
        this.webauthnActive = false;
        this.webauthnCredentials = null;
        this.keyName = "";
      }
    },
  },
};
</script>

<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-form @submit.prevent="activate">
        <v-card-title>
          {{ $t("accounts.two_factor.webauthn.dialog_title") }}
        </v-card-title>
        <v-card-text v-if="!webauthnCredentials">
          <div class="text-center">
            <v-icon color="primary" size="80">mdi-key-outline</v-icon>
          </div>
          <div class="text-subtitle-1 text-center">
            {{ $t("accounts.two_factor.webauthn.dialog_description") }}
          </div>
        </v-card-text>
        <v-card-text v-else>
          <p>
            <v-icon start color="success">mdi-check-circle</v-icon>
            {{ $t("accounts.two_factor.webauthn.key_detected") }}
          </p>
          <p>
            {{ $t("accounts.two_factor.webauthn.dialog_name_description") }}
          </p>
          <v-text-field
            v-model="keyName"
            required
            autofocus
            variant="filled"
            :label="$t('accounts.two_factor.webauthn.key_name')"
          />
        </v-card-text>
        <v-divider />
        <v-card-actions v-if="webauthnCredentials">
          <v-spacer></v-spacer>
          <primary-action-button
            :disabled="!keyName || loading"
            :loading="loading"
            type="submit"
            i18n-key="accounts.two_factor.webauthn.dialog_add_button"
          />
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>
