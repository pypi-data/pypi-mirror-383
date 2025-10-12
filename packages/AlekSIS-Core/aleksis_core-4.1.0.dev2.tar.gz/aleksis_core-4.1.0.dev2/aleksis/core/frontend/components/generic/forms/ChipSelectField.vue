<script>
import VAutocomplete from "@/vuetify/lib/components/VAutocomplete";
import chipHeightMixin from "../../../mixins/chipHeightMixin";
import ForeignKeyField from "./ForeignKeyField.vue";
export default {
  name: "ChipSelectField",
  components: { ForeignKeyField },
  extends: VAutocomplete,
  mixins: [chipHeightMixin],
  computed: {
    classes() {
      return {
        ...VAutocomplete.options.computed.classes.call(this),
        "chip-select-field": true,
      };
    },
  },
  props: {
    rounded: {
      type: Boolean,
      default: true,
    },
    hideDetails: {
      type: Boolean,
      default: true,
    },
    filled: {
      type: Boolean,
      default: true,
    },
  },
};
</script>

<style lang="scss">
.chip-select-field {
  & .v-input__control > .v-input__slot {
    min-height: auto !important;
    padding: 0 12px;
    cursor: pointer !important;
  }
  & .v-input__slot > .v-progress-linear {
    margin-left: v-bind(progressPadding);
    width: calc(100% - v-bind(heightString));
    top: calc(100% - 2px);
  }
  & .v-input__slot > .v-select__slot {
    & input {
      color: v-bind(color);
    }
    & > .v-input__append-inner {
      margin-top: 0;
      align-self: center !important;

      & i {
        color: v-bind(color);
      }
    }
  }
  & .v-input__append-outer {
    margin-top: 0;
    margin-bottom: 0;
    align-self: center !important;
  }
}
</style>
