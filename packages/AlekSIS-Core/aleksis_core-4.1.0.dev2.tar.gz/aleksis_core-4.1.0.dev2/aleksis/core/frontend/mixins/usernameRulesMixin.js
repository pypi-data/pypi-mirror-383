import { gqlUsernameSystemProperties } from "../components/app/systemProperties.graphql";

/**
 * This mixin provides rules checking whether a string conforms with the requiremends set out for usernames set in the site preferences.
 */
export default {
  apollo: {
    usernameSystemProperties: gqlUsernameSystemProperties,
  },
  computed: {
    usernameRules() {
      return {
        usernameAllowed: [
          (v) =>
            (!this.checkDisallowed(v) && this.checkAllowed(v)) ||
            this.$t("forms.errors.username_not_allowed"),
        ],
        usernameASCII: [
          (v) =>
            this.getNonASCIIChars(v).length === 0 ||
            this.$t("forms.errors.username_not_ascii", {
              characters: this.getNonASCIIChars(v).join(", "),
            }),
        ],
      };
    },
  },
  methods: {
    getNonASCIIChars(string) {
      // eslint-disable-next-line no-control-regex
      return string.match(/[^\x00-\x7F]/g) || [];
    },
    checkDisallowed(string) {
      return this.usernameSystemProperties.sitePreferences.authDisallowedUids?.includes(
        string,
      );
    },
    checkAllowed(string) {
      const regEx = new RegExp(
        this.usernameSystemProperties.sitePreferences.authAllowedUsernameRegex,
      );
      return regEx.test(string);
    },
  },
};
