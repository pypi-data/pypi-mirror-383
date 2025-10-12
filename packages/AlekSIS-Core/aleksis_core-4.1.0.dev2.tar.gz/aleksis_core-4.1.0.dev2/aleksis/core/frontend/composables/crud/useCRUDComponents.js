// Shared interfaces of the CRUD components

export const disableProps = Object.fromEntries(
  [
    "disabled",
    "disableQuery",
    "disableFilter",
    "disableSearch",
    "disableActions",
    "disableCreate",
    "disablePatch",
    "disableDelete",
  ].map((prop) => [
    prop,
    {
      type: Boolean,
      required: false,
      default: false,
    },
  ]),
);

export const activeFilterCountProps = {
  activeFilterCount: {
    type: Number,
    required: false,
    default: 0,
  },
};

export const CRUDBarProps = {
  /**
   * Pass additional actions by prop
   * [{ component, props } ...]
   */
  additionalActions: {
    type: Array,
    required: false,
    default: [],
  },
  /**
   * Flat toolbar?
   */
  flat: {
    type: Boolean,
    required: false,
    default: true,
  },
  /**
   * Hide toolbar on scroll
   * @values true, false
   */
  hideOnScroll: {
    type: Boolean,
    required: false,
    default: false,
  },
};
