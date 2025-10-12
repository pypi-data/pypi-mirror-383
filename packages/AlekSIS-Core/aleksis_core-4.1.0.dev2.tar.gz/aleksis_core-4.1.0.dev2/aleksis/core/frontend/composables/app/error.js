import { useErrorToast } from "./toasting";
import i18n from "../../app/i18n";

export function useError(error, errorCode) {
  console.error(`[${errorCode}]`, error);
  /**
   * Emits an error
   */
  // this.$emit("error", error, errorCode);

  let message = "";
  if (typeof error == "string") {
    // error is a translation key or simply a string
    message = error;
  } else if (
    typeof error == "object" &&
    error.message &&
    typeof error.message == "string"
  ) {
    // error object has a message string
    message = error.message;
  }
  useErrorToast(
    `${i18n.global.t(message)} (${i18n.global.t("error_code", { errorCode })})`,
    { multiLine: true },
  );
}
