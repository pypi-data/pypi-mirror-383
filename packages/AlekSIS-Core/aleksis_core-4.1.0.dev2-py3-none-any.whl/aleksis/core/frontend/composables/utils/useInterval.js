import { onMounted, onUnmounted, ref } from "vue";

/**
 * Vue composable to add an event listener to a target element.
 *
 * @param {TimerHandler} handler The function to run after the interval
 * @param {number} timeout The amount of time to wait after each run
 */
export function useInterval(handler, timeout) {
  const interval = ref(null);

  onMounted(() => {
    interval.value = setInterval(handler, timeout);
  });
  onUnmounted(() => {
    if (interval.value) {
      clearInterval(interval.value);
    }
  });
}
