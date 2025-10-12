<script>
import SaveButton from "../buttons/SaveButton.vue";
import ObjectForm from "./ObjectForm.vue";
import CancelButton from "../buttons/CancelButton.vue";
import objectFormPropsMixin from "../../../mixins/objectFormPropsMixin";
import loadingMixin from "../../../mixins/loadingMixin";
import FullscreenDialogPage from "../dialogs/FullscreenDialogPage.vue";
import { useAppStore } from "../../../stores/appStore";

export default {
  setup() {
    const appStore = useAppStore();
    return { appStore };
  },
  name: "FullscreenDialogObjectForm",
  components: { FullscreenDialogPage, CancelButton, ObjectForm, SaveButton },
  mixins: [objectFormPropsMixin, loadingMixin],
  props: {
    fallbackUrl: {
      type: [Object, String],
      default: null,
    },
  },
  methods: {
    cancel() {
      this.$backOrElse(this.fallbackUrl);
    },
    save() {
      this.handleLoading(false);
      this.$backOrElse(this.fallbackUrl);
    },
  },
  data() {
    return {
      valid: false,
    };
  },
  mounted() {
    this.appStore.setToolbarTitle(this?.$refs?.form?.title);
  },
};
</script>

<template>
  <fullscreen-dialog-page v-bind="$attrs">
    <object-form
      ref="form"
      v-bind="objectFormProps"
      v-model:valid="valid"
      @loading="handleLoading"
      @save="save"
      @cancel="cancel"
    >
      <template v-for="(_, slot) of $slots" #[slot]="scope"
        ><slot :name="slot" v-bind="scope"
      /></template>
    </object-form>

    <template #actions>
      <v-spacer />
      <cancel-button @click="cancel" :disabled="loading" />
      <save-button
        @click="$refs?.form.submit()"
        :loading="loading"
        :disabled="!valid"
      />
    </template>
  </fullscreen-dialog-page>
</template>
