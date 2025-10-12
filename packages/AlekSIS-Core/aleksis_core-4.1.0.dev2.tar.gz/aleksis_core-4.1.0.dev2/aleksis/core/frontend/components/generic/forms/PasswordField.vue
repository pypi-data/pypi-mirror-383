<template>
  <v-text-field
    v-bind="$attrs"
    :rules="[...rules, ...passwordRules.passwordValidation]"
    type="password"
    :hint="passwordHelpTexts.join(' · ')"
    persistent-hint
    :loading="$apollo.queries.passwordValidationStatus.loading"
    @change="refetchValidation"
    validate-on="blur"
    ref="passwordField"
  />
</template>

<script>
import {
  gqlPasswordHelpTexts,
  gqlPasswordValidationStatus,
} from "./password.graphql";

export default {
  name: "PasswordField",
  extends: "v-text-field",
  data() {
    return {
      passwordHelpTexts: [],
      passwordValidationStatus: [],
    };
  },
  props: {
    rules: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  computed: {
    passwordRules() {
      return {
        passwordValidation: [
          () =>
            this.passwordValidationStatus.length === 0 ||
            this.passwordValidationStatus.join(" · "),
        ],
      };
    },
  },
  apollo: {
    passwordHelpTexts: gqlPasswordHelpTexts,
    passwordValidationStatus: {
      query: gqlPasswordValidationStatus,
      skip: true,
      result() {
        this.$refs.passwordField.validate();
      },
    },
  },
  methods: {
    refetchValidation(password) {
      this.$apollo.queries.passwordValidationStatus.setVariables({
        password: password,
      });
      this.$apollo.queries.passwordValidationStatus.skip = false;
    },
  },
};
</script>
