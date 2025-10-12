<script>
import formRulesMixin from "../../mixins/formRulesMixin";
import {
  passwordRequestKeyVerificationStatus,
  resetPassword,
} from "./passwordReset.graphql";
import loadingMixin from "../../mixins/loadingMixin";
import PasswordField from "../generic/forms/PasswordField.vue";

const KeyStatus = {
  VALID: "VALID",
  INVALID: "INVALID",
  LOADING: "LOADING",
};

export default {
  name: "ResetPasswordFromKey",
  mixins: [formRulesMixin, loadingMixin],
  components: { PasswordField },
  data() {
    return {
      newPassword: "",
      confirmPassword: "",

      formValid: false,
      passwordRequestKeyVerificationStatus: null,

      KeyStatus,
    };
  },
  props: {
    resetKey: {
      type: String,
      required: true,
    },
  },
  apollo: {
    passwordRequestKeyVerificationStatus: {
      query: passwordRequestKeyVerificationStatus,
      variables() {
        return {
          key: this.resetKey,
        };
      },
    },
  },
  computed: {
    keyStatus() {
      if (this.$apollo.queries.passwordRequestKeyVerificationStatus.loading) {
        return KeyStatus.LOADING;
      }

      if (this.passwordRequestKeyVerificationStatus === true) {
        return KeyStatus.VALID;
      }

      return KeyStatus.INVALID;
    },
  },
  methods: {
    handlePasswordChange() {
      this.handleLoading(true);
      this.$apollo
        .mutate({
          mutation: resetPassword,
          variables: {
            key: this.resetKey,
            password: this.newPassword,
          },
        })
        .then(() => {
          this.$router.push({
            name: "core.account.login",
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
    <v-card>
      <v-form
        v-if="keyStatus === KeyStatus.VALID"
        @submit.prevent="handlePasswordChange"
        v-model="formValid"
      >
        <v-card-title>{{ $t("accounts.change_password.title") }}</v-card-title>
        <v-card-text>
          <div class="mb-4">
            {{ $t("accounts.reset_password.description") }}
          </div>
          <div aria-required="true" class="mb-4">
            <password-field
              autocomplete="new-password"
              v-model="newPassword"
              :label="$t('accounts.change_password.new_password')"
              outlined
              :rules="$rules().required.build()"
            />
          </div>
          <div aria-required="true" class="mb-4">
            <v-text-field
              type="password"
              autocomplete="new-password"
              v-model="confirmPassword"
              :label="$t('accounts.change_password.confirm_password')"
              variant="outlined"
              :rules="
                $rules()
                  .required.equalTo(
                    newPassword,
                    'forms.errors.passwords_do_not_match',
                  )
                  .build()
              "
            />
          </div>
        </v-card-text>

        <v-card-actions>
          <primary-action-button
            :loading="loading"
            :disabled="!formValid"
            i18n-key="accounts.change_password.action"
            type="submit"
          />
        </v-card-actions>
      </v-form>
      <v-card-text v-else-if="keyStatus === KeyStatus.LOADING">
        <v-skeleton-loader type="paragraph" />
      </v-card-text>
      <v-card-text v-else>
        <message-box type="error">
          {{ $t("accounts.reset_password.invalid_key") }}
        </message-box>
      </v-card-text>
    </v-card>
  </small-container>
</template>
