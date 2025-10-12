<script>
import {
  activeSchoolTerm,
  schoolTermsForActiveSchoolTerm,
  setActiveSchoolTerm,
} from "./activeSchoolTerm.graphql";
import loadingMixin from "../../mixins/loadingMixin";
export default {
  name: "ActiveSchoolTermSelect",
  mixins: [loadingMixin],
  emits: ["update:modelValue"],
  apollo: {
    schoolTerms: {
      query: schoolTermsForActiveSchoolTerm,
    },
    activeSchoolTerm: {
      query: activeSchoolTerm,
      result() {
        this.$emit("update:modelValue", this.activeSchoolTerm);
      },
    },
  },
  props: {
    affectedQuery: {
      type: Number,
      default: 0,
    },
    modelValue: {
      type: Object,
      required: false,
      default: null,
    },
    disableInvalidate: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  data() {
    return {
      activeSchoolTerm: null,
      schoolTerms: [],
      showSuccess: false,
    };
  },
  computed: {
    schoolTerm: {
      get() {
        return this.activeSchoolTerm?.id;
      },
      set(value) {
        if (this.activeSchoolTerm?.id === value) {
          return;
        }

        this.handleLoading(true);

        this.$apollo
          .mutate({
            mutation: setActiveSchoolTerm,
            variables: { id: value },
            update: (store, data) => {
              const newTerm = data.data.setActiveSchoolTerm;

              // Update cached data
              store.writeQuery({ query: activeSchoolTerm, data: newTerm });
              this.$emit("update:modelValue", newTerm);
            },
          })
          .catch((error) => {
            this.handleMutationError(error);
          })
          .finally(() => {
            this.handleLoading(false);
            this.showSuccess = true;
            setTimeout(() => {
              this.showSuccess = false;
            }, 2000);

            if (!this.disableInvalidate) {
              this.$invalidateState();
            }
          });
      },
    },
  },
  watch: {
    modelValue(value) {
      if (!value) {
        value = this.schoolTerms.find((term) => term.current);
      }
      if (Object.hasOwn(value, "activeSchoolTerm")) {
        value = value.activeSchoolTerm;
      }
      if (Object.hasOwn(value, "id")) {
        value = value.id;
      }

      if (this.schoolTerm === value) {
        return;
      }

      this.schoolTerm = value;
    },
  },
};
</script>

<template>
  <v-menu :close-on-content-click="false">
    <template #activator="{ props }">
      <v-btn
        icon
        v-bind="{ ...$attrs, ...props }"
        :loading="$apollo.queries.activeSchoolTerm.loading"
        :aria-label="$t('actions.select_school_term')"
      >
        <v-icon v-if="activeSchoolTerm?.current">$schoolTerm</v-icon>
        <v-icon v-else>mdi-calendar-alert-outline</v-icon>
      </v-btn>
    </template>
    <v-list
      :disabled="loading"
      selectable
      :selected="[schoolTerm]"
      @update:selected="schoolTerm = $event[0]"
      active-strategy="single-leaf"
      :mandatory="!!activeSchoolTerm"
    >
      <v-list-item disabled>
        <v-list-item-title>
          {{ $t("school_term.active_school_term.title") }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("school_term.active_school_term.subtitle") }}
        </v-list-item-subtitle>

        <template #append>
          <v-progress-circular
            v-if="loading"
            indeterminate
            :size="16"
            :width="2"
          />
          <v-icon v-else-if="showSuccess" color="success">$success</v-icon>
        </template>
      </v-list-item>

      <v-list-item v-for="term in schoolTerms" :key="term.id" :value="term.id">
        <v-list-item-title>
          {{ term.name }}
        </v-list-item-title>

        <template #append v-if="term.current">
          <v-chip label color="secondary">
            {{ $t("school_term.current") }}
          </v-chip>
        </template>
      </v-list-item>
    </v-list>
  </v-menu>
</template>
