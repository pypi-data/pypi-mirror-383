<template>
  <v-dialog v-model="popup" max-width="fit-content" v-if="src">
    <template #activator="{ props }">
      <v-card v-bind="props">
        <v-img
          :src="src"
          :alt="$t('person.additional_image')"
          class="text-white align-end"
          gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
          :max-width="activatorMaxWidth"
          :max-heigth="activatorMaxHeigth"
        >
          <v-card-title v-if="!hideCardTitle">
            {{ $t("person.additional_image") }}
          </v-card-title>
        </v-img>
      </v-card>
    </template>
    <v-sheet
      class="d-flex justify-center align-center flex-column text-center bg-transparent"
    >
      <v-img
        :src="src"
        :alt="$t('person.additional_image')"
        width="80vmin"
        max-height="80vmin"
      />
    </v-sheet>
  </v-dialog>
  <v-card v-else>
    <v-list>
      <v-list-item prepend-icon="mdi-image-off-outline">
        <v-list-item-title>
          {{ $t("person.no_additional_image") }}
        </v-list-item-title>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script>
export default {
  name: "AdditionalImage",
  props: {
    src: {
      required: true,
      validator: (p) => {
        return typeof p === "string" || p === null;
      },
    },
    hideCardTitle: {
      type: Boolean,
      default: false,
    },
    activatorMaxWidth: {
      type: [Number, String],
      default: undefined,
    },
  },
  data: () => ({
    popup: false,
  }),
};
</script>

<style scoped></style>
