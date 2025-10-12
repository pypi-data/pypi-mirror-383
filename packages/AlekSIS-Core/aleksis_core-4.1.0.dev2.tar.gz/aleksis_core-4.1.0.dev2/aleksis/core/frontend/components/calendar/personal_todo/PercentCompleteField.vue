<template>
  <div>
    <v-row>
      <v-col cols="3">
        <v-checkbox
          v-model="completed"
          :label="$t('calendar.create_event.personal_todos.completed_switch')"
        />
      </v-col>
      <v-col cols="9">
        <v-slider
          v-model="percent"
          v-bind="{ ...$attrs }"
          thumb-label
          label=""
          :hint="$attrs.label"
          persistent-hint
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  name: "PercentCompleteField",
  data() {
    return {
      innerValue: this.value,
    };
  },
  props: {
    value: {
      type: [Number, String],
      required: false,
      default: 0,
    },
    min: {
      type: String,
      required: false,
      default: "0",
    },
    max: {
      type: String,
      required: false,
      default: "100",
    },
  },
  computed: {
    percent: {
      get() {
        return this.innerValue;
      },
      set(value) {
        this.innerValue = value;
        this.$emit("input", value);
      },
    },
    completed: {
      get() {
        return Number(this.percent) === Number(this.max);
      },
      set(value) {
        if (value) {
          this.percent = this.max;
        } else {
          this.percent = this.min;
        }
      },
    },
  },
  watch: {
    value(newValue) {
      this.innerValue = newValue;
    },
  },
};
</script>

<style scoped></style>
