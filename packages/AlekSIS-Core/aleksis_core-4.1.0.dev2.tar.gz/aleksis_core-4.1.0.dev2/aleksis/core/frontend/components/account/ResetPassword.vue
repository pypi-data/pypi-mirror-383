<script>
import formRulesMixin from "../../mixins/formRulesMixin";
import AdminEmailList from "./AdminEmailList.vue";
import { requestPasswordReset } from "./passwordReset.graphql";
import loadingMixin from "../../mixins/loadingMixin";

export default {
  name: "ResetPassword",
  components: { AdminEmailList },
  mixins: [formRulesMixin, loadingMixin],
  data() {
    return {
      email: "",
      formValid: false,
    };
  },
  methods: {
    handlePasswordReset() {
      this.handleLoading(true);
      this.$apollo
        .mutate({
          mutation: requestPasswordReset,
          variables: {
            email: this.email,
          },
        })
        .then(() => {
          this.$router.push({
            name: "core.accounts.resetPasswordDone",
          });
        })
        .catch((error) => {
          this.handleMutationError(error);
        })
        .finally(() => {
          this.handleLoading(false);
        });
    },
  },
};
</script>

<template>
  <small-container>
    <v-form ref="form" v-model="formValid">
      <v-card class="mb-2">
        <v-card-title>
          {{ $t("accounts.reset_password.title") }}
        </v-card-title>
        <v-card-text>
          <p>
            {{ $t("accounts.reset_password.message") }}
          </p>
          <div aria-required="true">
            <v-text-field
              variant="outlined"
              v-model="email"
              :rules="$rules().required.isEmail.build()"
              :label="$t('accounts.reset_password.email')"
              name="email"
              type="email"
              required
            />
          </div>
        </v-card-text>
        <v-card-actions>
          <primary-action-button
            :loading="loading"
            :disabled="!formValid"
            i18n-key="accounts.reset_password.button"
            type="submit"
            @click.prevent="handlePasswordReset"
          />
        </v-card-actions>
      </v-card>
      <v-card>
        <v-card-text>
          <p>
            {{ $t("accounts.reset_password.contact_admins") }}
          </p>
          <admin-email-list />
        </v-card-text>
      </v-card>
    </v-form>
  </small-container>
</template>
