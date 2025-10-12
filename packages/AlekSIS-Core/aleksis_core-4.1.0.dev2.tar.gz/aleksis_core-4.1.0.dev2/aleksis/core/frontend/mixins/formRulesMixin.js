/**
 * @typedef {function(any): (boolean|string)} Rule
 */

/**
 * Mixin that provides generic default rules to avoid repetition
 */
export default {
  methods: {
    /**
     * Interactive rule builder.
     *
     * Keep in mind that the order of adding rules matters.
     *
     * @example
     * $rules.required.build();
     * $rules.build(additionalRules);
     * $rules.isANumber.isSmallerThan(50).build(additionalRules);
     * $rules.isANumber.isAWholeNumber.isGreaterThan(0).build();
     */
    $rules() {
      const mixin = this;
      return {
        _rules: [],
        /**
         * Finish rule creating
         *
         * @param {Rule[]} additional Optional list of addtional rules to add
         * @returns {Rule[]} the built array of rules
         */
        build(additional = []) {
          return [...this._rules, ...additional];
        },

        get required() {
          this._rules.push(
            (value) => !!value || mixin.$t("forms.errors.required"),
          );
          return this;
        },

        get isANumber() {
          this._rules.push(
            (value) =>
              !value ||
              !isNaN(parseFloat(value)) ||
              mixin.$t("forms.errors.not_a_number"),
          );
          return this;
        },
        get isAWholeNumber() {
          this._rules.push(
            (value) =>
              !value ||
              value % 1 === 0 ||
              mixin.$t("forms.errors.not_a_whole_number"),
          );
          return this;
        },
        isGreaterThan(min = 0) {
          this._rules.push(
            (value) =>
              !value ||
              parseInt(value) >= min ||
              mixin.$t("forms.errors.number_too_small"),
          );
          return this;
        },
        isGreaterAndNotSameThan(min = 0) {
          this._rules.push(
            (value) =>
              !value ||
              parseInt(value) > min ||
              mixin.$t("forms.errors.number_too_small"),
          );
          return this;
        },
        isSmallerThan(max = 0) {
          this._rules.push(
            (value) =>
              !value ||
              parseInt(value) <= max ||
              mixin.$t("forms.errors.number_too_big"),
          );
          return this;
        },
        isSmallerAndNotSameThan(max = 0) {
          this._rules.push(
            (value) =>
              !value ||
              parseInt(value) < max ||
              mixin.$t("forms.errors.number_too_big"),
          );
          return this;
        },
        isHexColor(allowAlpha = true) {
          const regex = allowAlpha
            ? /^(#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8}))?$/i
            : /^(#([0-9a-f]{3}[0-9a-f]{3}?))?$/i;
          this._rules.push(
            (value) =>
              regex.test(value) || mixin.$t("forms.errors.invalid_color"),
          );
          return this;
        },
        hasMinLength(minLength) {
          this._rules.push(
            (value) =>
              !value ||
              value.length >= minLength ||
              mixin.$t("forms.errors.string_too_short", {
                minLength: minLength,
              }),
          );
          return this;
        },
        hasMaxLength(maxLength) {
          this._rules.push(
            (value) =>
              !value ||
              value.length <= maxLength ||
              mixin.$t("forms.errors.string_too_long", {
                maxLength: maxLength,
              }),
          );
          return this;
        },
        get isNonEmpty() {
          this._rules.push(
            (value) => value.length > 0 || mixin.$t("forms.errors.required"),
          );
          return this;
        },
        get isEmail() {
          const emailRegex =
            // eslint-disable-next-line no-control-regex
            /(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])*/;
          this._rules.push(
            (value) =>
              !value ||
              emailRegex.test(value) ||
              mixin.$t("forms.errors.invalid_email"),
          );
          return this;
        },
        equalTo(field, i18nKey = "forms.errors.not_equal") {
          this._rules.push(
            (value) =>
              !value || value === field || mixin.$t(i18nKey, { field: field }),
          );
          return this;
        },
      };
    },
  },
};
