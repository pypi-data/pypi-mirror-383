<script>
import mutateMixin from "../../../mixins/mutateMixin";
import { generateRecoveryCodes } from "../twoFactor.graphql";
import twoFactorDialogMixin from "../twoFactorDialogMixin";
export default {
  name: "GenerateRecoveryCodesDialog",
  mixins: [mutateMixin, twoFactorDialogMixin],
  data() {
    return {
      uiAction: "generate_recovery_codes",
    };
  },
  methods: {
    activate() {
      this.mutate(generateRecoveryCodes);
    },
  },
};
</script>

<template>
  <v-dialog v-model="dialog" max-width="500">
    <v-card>
      <v-card-title>
        {{ $t("accounts.two_factor.recovery_codes.generate_title") }}
      </v-card-title>
      <v-card-text>
        {{ $t("accounts.two_factor.recovery_codes.generate_question") }}
      </v-card-text>
      <v-divider></v-divider>

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
          @click="activate"
          :loading="loading"
          :disabled="loading"
          i18n-key="accounts.two_factor.recovery_codes.generate_button"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped></style>
