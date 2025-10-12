<template>
  <small-container>
    <v-card>
      <v-card-title v-if="!personId">{{
        $t("accounts.change_password.title")
      }}</v-card-title>
      <v-card-title v-else>{{
        $t("accounts.change_password.title_foreign", personUserPw)
      }}</v-card-title>

      <v-form
        @submit.prevent="handlePasswordChange"
        v-model="formValid"
        v-if="ready"
      >
        <v-card-text>
          <div aria-required="true" class="mb-4" v-if="!personId">
            <v-text-field
              type="password"
              autocomplete="old-password"
              v-model="oldPassword"
              :label="$t('accounts.change_password.old_password')"
              variant="outlined"
              :rules="$rules().required.build()"
            />
          </div>
          <div aria-required="true" class="mb-4">
            <password-field
              autocomplete="new-password"
              v-model="newPassword"
              :label="$t('accounts.change_password.new_password')"
              outlined
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
      <v-card-text v-if="this.$apollo.queries.personUserPw.loading">
        <v-skeleton-loader type="paragraph" />
      </v-card-text>
    </v-card>
  </small-container>
</template>

<script>
import formRulesMixin from "../../mixins/formRulesMixin";
import loadingMixin from "../../mixins/loadingMixin";
import { changePassword, personUserPw } from "./changePassword.graphql";
import PasswordField from "../generic/forms/PasswordField.vue";
export default {
  name: "ChangePassword",
  mixins: [formRulesMixin, loadingMixin],
  components: { PasswordField },
  data() {
    return {
      oldPassword: "",
      newPassword: "",
      confirmPassword: "",

      personUserPw: {},

      formValid: false,
    };
  },
  computed: {
    ready() {
      return !this.personId || this.personUserPw;
    },
  },
  props: {
    personId: {
      type: [String, Number],
      required: false,
      default: undefined,
    },
    successUrl: {
      type: Object,
      default: () => ({ name: "index" }),
    },
  },
  apollo: {
    personUserPw: {
      query: personUserPw,
      variables() {
        return {
          id: this.personId,
        };
      },
      skip() {
        return !this.personId;
      },
      result() {
        this.$setToolBarTitle(
          this.$t(
            "accounts.change_password.menu_title_foreign",
            this.personUserPw,
          ),
        );
      },
    },
  },
  methods: {
    handlePasswordChange() {
      this.handleLoading(true);
      this.$apollo
        .mutate({
          mutation: changePassword,
          variables: {
            userId: this.personUserPw?.userid,
            oldPassword: this.oldPassword || null,
            password: this.newPassword,
          },
        })
        .then(() => {
          this.$router.push(this.successUrl);
        })
        .catch((error) => {
          this.handleMutationError(error);
        })
        .finally(() => {
          this.handleLoading(false);
        });
    },
  },
  mounted() {
    this.$setToolBarTitle(
      this.$t("accounts.change_password.menu_title_self", this.personUserPw),
    );
  },
};
</script>
