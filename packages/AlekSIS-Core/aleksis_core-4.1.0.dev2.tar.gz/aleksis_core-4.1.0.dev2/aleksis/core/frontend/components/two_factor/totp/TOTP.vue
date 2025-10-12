<template>
  <v-card class="mb-4">
    <v-card-title>
      <v-icon class="mr-2" size="large">mdi-two-factor-authentication</v-icon>
      {{ $t("accounts.two_factor.totp.title") }}
      <v-spacer />
      <activated-chip :activated="totp.activated" />
    </v-card-title>
    <v-card-text>
      {{ $t("accounts.two_factor.totp.description") }}
    </v-card-text>
    <v-card-actions>
      <secondary-action-button
        v-if="!totp.activated"
        :to="{
          name: 'core.twoFactor',
          query: { _ui_action: 'activate_totp' },
        }"
        i18n-key="accounts.two_factor.totp.activate_button"
        icon-text="mdi-key-plus"
        color="primary"
      />
      <secondary-action-button
        v-else
        color="error"
        :to="{
          name: 'core.twoFactor',
          query: { _ui_action: 'deactivate', id: totp.id },
        }"
        icon-text="mdi-trash-can-outline"
        i18n-key="accounts.two_factor.deactivate_button"
      />
      <activate-t-o-t-p-dialog
        :authenticator="totp"
        ref="activateTotpDialog"
        @save="$emit('save')"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";
import ActivatedChip from "../ActivatedChip.vue";
import ActivateTOTPDialog from "./ActivateTOTPDialog.vue";

defineEmits(["save"]);
defineProps({
  totp: {
    type: Object,
    required: true,
  },
});
</script>
