import { onMounted, onUnmounted } from "vue";

/**
 * Vue composable to add an event listener to a target element.
 *
 * @param {EventTarget} target The target element to listen on.
 * @param {string} event The event type to listen for.
 * @param {Function} callback The callback function to execute when the event occurs.
 */
export function useEventListener(target, event, callback) {
  onMounted(() => {
    console.debug("Safely adding handler for %s on %o", event, target);
    target.addEventListener(event, callback);
  });
  onUnmounted(() => {
    console.debug("Removing handler for %s on %o", event, target);
    target.removeEventListener(event, callback);
  });
}
