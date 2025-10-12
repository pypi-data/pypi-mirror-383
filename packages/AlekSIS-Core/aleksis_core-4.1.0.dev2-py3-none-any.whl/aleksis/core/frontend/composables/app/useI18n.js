import { useI18n as useOriginalI18n } from "vue-i18n";
import { DateTime } from "luxon";

export function useI18n(options) {
  const i18n = useOriginalI18n(options);

  function customD(value, ...args) {
    if (DateTime.isDateTime(value)) {
      value = value.toJSDate();
    }
    return i18n.d(value, ...args);
  }

  return {
    ...i18n,
    d: customD,
  };
}
