export const getNameProps = {
  /**
   * The item's name property displayed (per default) in confirm delete dialog.
   */
  nameAttribute: {
    type: String,
    required: false,
    default: "name",
  },
  /**
   * Method to get the text displayed per item in confirm delete dialog.
   */
  getNameOfItem: {
    type: Function,
    required: false,
    default: function (item, nameAttribute) {
      return item[nameAttribute] || item.toString();
    },
  },
};
