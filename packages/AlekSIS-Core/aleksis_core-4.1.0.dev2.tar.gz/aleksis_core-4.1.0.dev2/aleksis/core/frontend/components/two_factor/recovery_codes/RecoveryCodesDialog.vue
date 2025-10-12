<script>
import { recoveryCodes } from "../twoFactor.graphql";
import twoFactorDialogMixin from "../twoFactorDialogMixin";
import CopyToClipboardButton from "../../generic/CopyToClipboardButton.vue";

export default {
  name: "RecoveryCodesDialog",
  components: { CopyToClipboardButton },
  mixins: [twoFactorDialogMixin],
  apollo: {
    twoFactor: {
      query: recoveryCodes,
      fetchPolicy: "network-only",
      skip() {
        return !this.dialog;
      },
      result({ data }) {
        if (!data.twoFactor.recoveryCodes) {
          this.$router.push({ name: "core.twoFactor" });
        }
      },
    },
  },
  data() {
    return {
      uiAction: "show_recovery_codes",
    };
  },
};
</script>

<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-card-title>
        {{ $t("accounts.two_factor.recovery_codes.dialog_title") }}
      </v-card-title>
      <v-card-text v-if="twoFactor">
        {{
          $tc(
            "accounts.two_factor.recovery_codes.count",
            twoFactor.recoveryCodes.unusedCodeCount,
            {
              unused: twoFactor.recoveryCodes.unusedCodeCount,
              total: twoFactor.recoveryCodes.totalCodeCount,
            },
          )
        }}
        {{ $t("accounts.two_factor.recovery_codes.dialog_description") }}

        <v-list density="compact">
          <v-list-item
            v-for="code in twoFactor.recoveryCodes.unusedCodes"
            :key="code"
          >
            <v-list-item-title>
              <pre>{{ code }}</pre>
            </v-list-item-title>
          </v-list-item>
        </v-list>
        <copy-to-clipboard-button
          v-if="twoFactor"
          :button-text="$t('accounts.two_factor.recovery_codes.copy')"
          :text="twoFactor.recoveryCodes.unusedCodes.join('|')"
          color="primary"
        />
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <secondary-action-button
          v-if="twoFactor"
          :to="{
            name: 'core.accounts.downloadRecoveryCodes',
          }"
          target="_blank"
          icon-text="mdi-download-outline"
          i18n-key="accounts.two_factor.recovery_codes.download_button"
        />
        <secondary-action-button
          v-if="twoFactor"
          :to="{
            name: 'core.twoFactor',
            query: { _ui_action: 'generate_recovery_codes' },
          }"
          icon-text="mdi-autorenew"
          i18n-key="accounts.two_factor.recovery_codes.generate_button"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
