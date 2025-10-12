<template>
  <v-card class="mb-4">
    <v-card-title>
      <v-icon class="mr-2" size="large">mdi-backup-restore</v-icon>
      {{ $t("accounts.two_factor.recovery_codes.title") }}
      <v-spacer />
      <activated-chip :activated="!!recoveryCodes">
        <template #activated>
          {{
            $tc(
              "accounts.two_factor.recovery_codes.count",
              recoveryCodes.unusedCodeCount,
              {
                count: recoveryCodes.unusedCodeCount,
              },
            )
          }}
        </template>
        <template #deactivated>
          {{
            $tc(
              "accounts.two_factor.recovery_codes.count",
              recoveryCodes.unusedCodeCount,
              {
                count: recoveryCodes.unusedCodeCount,
              },
            )
          }}
        </template>
      </activated-chip>
    </v-card-title>
    <v-card-text>
      <span>
        {{ $t("accounts.two_factor.recovery_codes.description") }}
      </span>
    </v-card-text>
    <v-card-actions>
      <recovery-codes-dialog />
      <generate-recovery-codes-dialog @save="$emit('save')" />
      <secondary-action-button
        v-if="recoveryCodes"
        :to="{
          name: 'core.twoFactor',
          query: { _ui_action: 'show_recovery_codes' },
        }"
        color="primary"
        i18n-key="accounts.two_factor.recovery_codes.show_button"
        icon-text="mdi-format-list-numbered"
      />
      <secondary-action-button
        v-if="recoveryCodes"
        :to="{
          name: 'core.accounts.downloadRecoveryCodes',
        }"
        target="_blank"
        i18n-key="accounts.two_factor.recovery_codes.download_button"
        icon-text="mdi-download-outline"
      />
      <secondary-action-button
        :to="{
          name: 'core.twoFactor',
          query: { _ui_action: 'generate_recovery_codes' },
        }"
        :color="recoveryCodes ? 'error' : 'secondary'"
        i18n-key="accounts.two_factor.recovery_codes.generate_button"
        icon-text="mdi-autorenew"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";
import ActivatedChip from "../ActivatedChip.vue";
import RecoveryCodesDialog from "./RecoveryCodesDialog.vue";
import GenerateRecoveryCodesDialog from "./GenerateRecoveryCodesDialog.vue";

defineEmits(["save"]);
defineProps({
  recoveryCodes: {
    type: Object,
    required: true,
  },
});
</script>
