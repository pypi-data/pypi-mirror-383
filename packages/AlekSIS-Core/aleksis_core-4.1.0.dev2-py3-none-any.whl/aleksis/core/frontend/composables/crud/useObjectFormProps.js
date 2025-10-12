export const objectSchemaProp = {
  // TODO:
  // - Can it be optional? That would mean default values alone work. Should be desirable.
  //   1. Results in empty defaultItem
  //   2. Currently can not be empty, because it is used for type!
  objectSchema: {
    type: Object,
    // required: false,
    // default: () => ({}),
    required: true,
  },
};

export const objectFormProps = {
  ...objectSchemaProp,
  objectLayout: {
    type: Object,
    required: false,
    default: () => ({}),
  },
  /**
   * The item offered for editing
   */
  editItem: {
    type: Object,
    required: false,
    default: () => ({}),
  },
};
