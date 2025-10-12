// This composable contains the CRUDProvider's action logic
// which is at the same time the logic for the ActionSelect
// The CRUDProvider uses the maxActionsProps and the ActionSelect the minActionsProps.
// This composable enables the CRUDProvider's other slots to do stuff with actions.

// Unused in CRUDProvider
export function useActionFilter(action, items) {
  return items.filter(action.predicate);
}

export function useAction(action, items) {
  action.handler(items);
  return action.clearSelection ? [] : items;
}

// Only used in CRUDProvider
export const maxActionsProps = {
  /**
   * Array of action objects
   *
   * An action object has a name (string), an icon (string),
   * a predicate (function called on item),
   * a handler (function called on item array) and
   * a clearSelection toggle.
   *
   * @example [
   *            {
   *              name: "action's name",
   *              icon: "action's icon",
   *              predicate: (item) => {
   *                return true if item can be handled
   *              },
   *              handler: (items) => {
   *                do the action on array of items
   *              },
   *              clearSelection: true/false,
   *            },
   *            ...
   *          ]
   */
  additionalActions: {
    type: Array,
    required: false,
    default: () => [],
  },
};

export const minActionsProps = {
  /**
   * Actions offered for selection
   *
   * @example [
   *            {
   *              name: "action's name",
   *              icon: "action's icon",
   *            },
   *            ...
   *          ]
   */
  actions: {
    type: Array,
    required: false,
    default: () => [],
  },
  /**
   * Number of items the action will apply to
   */
  selectionCount: {
    type: Number,
    required: false,
    default: 0,
  },
};
