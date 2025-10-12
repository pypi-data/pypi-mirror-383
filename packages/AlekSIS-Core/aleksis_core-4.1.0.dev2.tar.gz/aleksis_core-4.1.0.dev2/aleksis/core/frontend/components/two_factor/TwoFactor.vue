<template>
  <div>
    <div v-if="$apollo.queries.twoFactor.loading">
      <v-skeleton-loader type="card,card,card"></v-skeleton-loader>
    </div>
    <div v-else-if="twoFactor">
      <deactivate-authenticator-dialog @save="afterSave" />

      <t-o-t-p :totp="twoFactor.totp" @save="afterSave" />
      <recovery-codes
        v-if="
          twoFactor.totp.activated ||
          twoFactor.webauthn.authenticators.length > 0
        "
        :recovery-codes="twoFactor.recoveryCodes"
        @save="afterSave"
      />
      <webauthn :webauthn="twoFactor.webauthn" @save="afterSave" />
    </div>
  </div>
</template>

<script>
import { twoFactor } from "./twoFactor.graphql";
import DeactivateAuthenticatorDialog from "./DeactivateAuthenticatorDialog.vue";
import RecoveryCodes from "./recovery_codes/RecoveryCodes.vue";
import TOTP from "./totp/TOTP.vue";
import Webauthn from "./webauthn/Webauthn.vue";

export default {
  name: "TwoFactor",
  components: {
    Webauthn,
    TOTP,
    RecoveryCodes,
    DeactivateAuthenticatorDialog,
  },
  apollo: {
    twoFactor: {
      query: twoFactor,
      fetchPolicy: "network-only",
    },
  },
  methods: {
    afterSave() {
      this.$apollo.queries.twoFactor.refetch();
      this.$router.push({ name: "core.twoFactor" });
    },
  },
};
</script>
