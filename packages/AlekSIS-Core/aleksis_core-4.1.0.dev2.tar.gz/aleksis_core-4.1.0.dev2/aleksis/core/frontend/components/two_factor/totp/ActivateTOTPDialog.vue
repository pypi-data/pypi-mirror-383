<script>
import CopyToClipboardButton from "../../generic/CopyToClipboardButton.vue";
import mutateMixin from "../../../mixins/mutateMixin";
import { activateTotp } from "../twoFactor.graphql";
import twoFactorDialogMixin from "../twoFactorDialogMixin";

const TOTP_LENGTH = 6;
export default {
  name: "ActivateTOTPDialog",
  mixins: [mutateMixin, twoFactorDialogMixin],
  components: { CopyToClipboardButton },
  props: {
    authenticator: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      code: "",
      TOTP_LENGTH,
      uiAction: "activate_totp",
    };
  },
  computed: {
    codeValid() {
      return this.code.length === TOTP_LENGTH;
    },
  },

  methods: {
    activate() {
      this.mutate(activateTotp, {
        code: this.code,
      });
    },
  },
};
</script>

<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-card-title>
        {{ $t("accounts.two_factor.totp.activate.title") }}
      </v-card-title>
      <v-card-text
        v-if="$apollo.queries.didRecentlyAuthenticate.loading"
        class="text-center"
      >
        <v-progress-circular
          indeterminate
          color="primary"
        ></v-progress-circular>
      </v-card-text>
      <v-card-text v-else>
        <p>
          {{ $t("accounts.two_factor.totp.activate.description") }}
        </p>
        <div
          v-html="authenticator.totpQrCode"
          class="w-100 d-flex justify-center"
        ></div>
        <div class="d-flex justify-center mb-4">
          <copy-to-clipboard-button
            :button-text="$t('accounts.two_factor.totp.activate.copy_url')"
            :text="authenticator.totpUrl"
            color="primary"
          />
          <copy-to-clipboard-button
            :button-text="$t('accounts.two_factor.totp.activate.copy_secret')"
            :text="authenticator.secret"
            color="primary"
          />
        </div>

        {{ $t("accounts.two_factor.totp.activate.enter_code") }}

        <v-otp-input
          v-model="code"
          :length="TOTP_LENGTH"
          :disabled="loading"
          @finish="activate"
        ></v-otp-input>
      </v-card-text>
      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>
        <primary-action-button
          @click="activate"
          :loading="loading"
          :disabled="loading || !codeValid"
          i18n-key="accounts.two_factor.totp.activate.button"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
