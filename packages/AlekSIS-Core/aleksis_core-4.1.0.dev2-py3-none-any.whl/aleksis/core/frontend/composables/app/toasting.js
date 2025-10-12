import { useAppStore } from "../../stores/appStore";

const DEFAULT_TOAST_STATE = "error";

function useToast(
  message,
  state = DEFAULT_TOAST_STATE,
  additionalOptions = {},
) {
  const appStore = useAppStore();

  appStore.snackbarItems.push({
    id: crypto.randomUUID(),
    text: message,
    color: state || DEFAULT_TOAST_STATE,
    ...additionalOptions,
  });
}

function useErrorToast(message, options = {}) {
  return useToast(message || "generic_messages.error", "error", options);
}

function useSuccessToast(message, options = {}) {
  return useToast(message || "generic_messages.success", "success", options);
}

function useInfoToast(message, options = {}) {
  return useToast(message, "info", options);
}

function useWarningToast(message, options = {}) {
  return useToast(message, "warning", options);
}

export {
  useToast,
  useErrorToast,
  useSuccessToast,
  useInfoToast,
  useWarningToast,
};
