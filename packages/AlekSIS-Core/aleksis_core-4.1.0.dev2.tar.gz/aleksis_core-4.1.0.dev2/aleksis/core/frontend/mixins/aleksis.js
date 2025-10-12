/**
 * Mixin with utilities for AlekSIS view components.
 */
import { DateTime } from "luxon";

import errorCodes from "../errorCodes";
import {
  useErrorToast,
  useInfoToast,
  useSuccessToast,
  useToast,
  useWarningToast,
} from "../composables/app/toasting";
import { useError } from "../composables/app/error";
import { useEventListener } from "../composables/utils/domEvent";

const aleksisMixin = {
  computed: {
    $hash() {
      return this.$route?.hash ? this.$route.hash.substring(1) : "";
    },
  },
  methods: {
    safeAddEventListener(target, event, handler) {
      console.warn(
        "safeAddEventListener(…) is deprecated, use useEventListener(…) instead",
      );
      return useEventListener(target, event, handler);
    },
    $toast(message, state, timeout) {
      console.warn("$toast(…) is deprecated, use useToast(…) instead");
      return useToast(message, state, { timeout });
    },
    $toastError(message, timeout) {
      console.warn(
        "$toastError(…) is deprecated, use useErrorToast(…) instead",
      );
      return useErrorToast(message, { timeout });
    },
    $toastSuccess(message, timeout) {
      console.warn(
        "$toastSuccess(…) is deprecated, use useSuccessToast(…) instead",
      );
      return useSuccessToast(message, { timeout });
    },
    $toastInfo(message, timeout) {
      console.warn("$toastInfo(…) is deprecated, use useInfoToast(…) instead");
      return useInfoToast(message, { timeout });
    },
    $toastWarning(message, timeout) {
      console.warn(
        "$toastWarning(…) is deprecated, use useWarningToast(…) instead",
      );
      return useWarningToast(message, { timeout });
    },
    $parseISODate(value) {
      return DateTime.fromISO(value);
    },
    $d(value, arg) {
      console.info("custom $d", value, arg);
      if (DateTime.isDateTime(value)) {
        value = value.toJSDate();
      }
      return this.$i18n.d(value, arg);
    },
    /**
     * Convert a luxon DateTime object to an ISO representation in UTC
     * @param {DateTime} dateTime DateTime object to convert
     * @return {String} ISO string
     */
    $toUTCISO(dateTime) {
      return dateTime.setZone("utc").toISO();
    },
    /**
     * Generic error handler
     * Logs to console, emits an error event &
     * posts a suitable message to the snackbar
     */
    handleMutationError({ graphQLErrors, networkError }) {
      if (graphQLErrors) {
        for (let err of graphQLErrors) {
          console.error(
            "GraphQL error in mutation",
            err.path.join("."),
            ":",
            err.message,
          );
          if (typeof err.message == "string") {
            this.handleError(err.message, errorCodes.graphQlErrorMutation);
          } else if (err.message instanceof Object) {
            // This is for Django's validation mechanism

            if ("fieldErrors" in this) {
              this.fieldErrors = err.message;
            }

            // If field errors are not handled by this component, show them as error message
            let message = "";

            for (const [key, value] of Object.entries(err.message)) {
              if (key === "__all__") {
                message += `${value}<br/>`;
              } else {
                message += `${key}: ${value}<br/>`;
              }
            }
            this.handleError(
              message,
              errorCodes.graphQlErrorMutationValidation,
            );
          }
        }
      }
      if (networkError) {
        console.error("GraphQL network error", networkError);
        this.handleError(
          this.$t("network_errors.snackbar_error_message"),
          errorCodes.networkErrorMutation,
        );
      }
    },
    handleError(error, errorCode) {
      console.warn(
        "handleError(…) is deprecated, use useError(…) composable instead",
      );
      return useError(error, errorCode);
    },
    /**
     * Lookup nested key
     * Keys are either an array of string keys or one string with . seperated keys.
     *
     * @returns The value of the nested key
     */
    getKeysRecursive(keys, object) {
      if (Array.isArray(keys)) {
        return keys.reduce((obj, key) => obj[key], object);
      }
      if (typeof keys === "string") {
        return this.getKeysRecursive(keys.split("."), object);
      } else {
        console.error("Expeced array or string got:", keys);
      }
    },
    /**
     * Set nested key
     * Keys are either an array of string keys or one string with . seperated keys.
     *
     * @returns The new value of the nested key
     */
    setKeysRecursive(keys, object, value) {
      if (Array.isArray(keys)) {
        const [first, ...rest] = keys;
        if (rest.length == 0) {
          return (object[first] = value);
        } else {
          return this.setKeysRecursive(rest, object[first], value);
        }
      }
      if (typeof keys === "string") {
        return this.setKeysRecursive(keys.split("."), object, value);
      } else {
        console.error("Expeced array or string got:", keys);
      }
    },
    $backOrElse(fallback = null) {
      if (fallback == null) {
        fallback = this.$router.base || "/";
      }

      if (
        window.history.length <= 2 &&
        this.$route.path === this.$router.history._startLocation
      ) {
        // No history → navigate to fallback
        this.$router.replace(fallback);
        return;
      }

      this.$router.back();
    },
    /**
     * Parse a number from string according to locale.
     *
     * This might seem hacky at first. But hear me out. This might be
     * JavaScript's best number parser since it adds the missing
     * parser to the standardized Intl.NumberFormat.
     *
     * Source: https://stackoverflow.com/a/78941643
     */
    $parseNumber(number) {
      class NumberParser {
        constructor(locale) {
          const format = new Intl.NumberFormat(locale);
          const parts = format.formatToParts(-12345.6);
          const numerals = Array.from({ length: 10 }).map((_, i) =>
            format.format(i),
          );
          const index = new Map(numerals.map((d, i) => [d, i]));
          this._minusSign = new RegExp(
            `[${parts.find((d) => d.type === "minusSign").value}]`,
          );
          this._group = new RegExp(
            `[${parts.find((d) => d.type === "group").value}]`,
            "g",
          );
          this._decimal = new RegExp(
            `[${parts.find((d) => d.type === "decimal").value}]`,
          );
          this._numeral = new RegExp(`[${numerals.join("")}]`, "g");
          this._index = (d) => index.get(d);
        }
        parse(string) {
          const DIRECTION_MARK = /\u061c|\u200e/g;
          return +string
            .trim()
            .replace(DIRECTION_MARK, "")
            .replace(this._group, "")
            .replace(this._decimal, ".")
            .replace(this._numeral, this._index)
            .replace(this._minusSign, "-");
        }
      }

      return new NumberParser().parse(number);
    },
  },
  mounted() {
    this.$emit("mounted");
  },
  emits: ["mounted"],
};

export default aleksisMixin;
