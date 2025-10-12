// These correspond to the utils in apollo.js

import { isRef, computed, reactive, ref } from "vue";

export function argToRef(arg) {
  if (isRef(arg)) {
    return arg;
  } else if (typeof arg === "function") {
    return computed(arg);
  } else {
    return ref(arg);
  }
}

export function argToReactive(arg) {
  if (isRef(arg)) {
    return arg;
  } else if (typeof arg === "function") {
    return computed(arg);
  } else if (arg) {
    return reactive(arg);
  } else {
    return arg;
  }
}
