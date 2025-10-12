<script setup>
import { ref } from "vue";
import { useRouter } from "@/vue-router";
import CRUDProvider from "../generic/crud/CRUDProvider.vue";
import ConfirmDialog from "../generic/dialogs/ConfirmDialog.vue";

const deleteItems = ref(false);
const router = useRouter();
function handleDeleteDone() {
  deleteItems.value = false;
  router.push({
    name: "core.persons",
  });
}
</script>

<template>
  <div>
    <primary-action-button
      v-if="person.canEdit"
      :to="{
        name: 'core.personById',
        params: { id: person.id },
        query: { _ui_action: 'edit' },
      }"
      i18n-key="actions.edit"
      icon-text="$edit"
    />
    <secondary-action-button
      v-if="person.canChangePersonPreferences"
      :to="{
        name: 'core.preferencesPersonByPk',
        params: { pk: person.id },
      }"
      icon-text="$preferences"
      i18n-key="preferences.person.change_preferences"
    />

    <button-menu
      v-if="
        person.canImpersonatePerson ||
        person.canInvitePerson ||
        person.canDelete ||
        person.canChangePassword ||
        person.canSendPasswordResetRequest
      "
      icon-only
      text-translation-key="actions.more_actions"
    >
      <v-list-item
        v-if="person.canImpersonatePerson && person.userid"
        :to="{
          name: 'impersonate.impersonateByUserPk',
          params: { uid: person.userid },
          query: { next: $route.path },
        }"
        prepend-icon="mdi-account-box-outline"
      >
        <v-list-item-title>
          {{ $t("person.impersonation.impersonate") }}
        </v-list-item-title>
      </v-list-item>

      <v-list-item
        v-if="person.canInvitePerson"
        :to="{
          name: 'core.invitePerson',
          params: { id: person.id },
        }"
        prepend-icon="mdi-account-plus-outline"
      >
        <v-list-item-title>
          {{ $t("person.invite") }}
        </v-list-item-title>
      </v-list-item>

      <v-list-item
        v-if="person.canDelete"
        @click="deleteItems = [person]"
        class="text-error"
      >
        <template #prepend>
          <v-icon color="error">$deleteContent</v-icon>
        </template>

        <v-list-item-title>
          {{ $t("person.delete") }}
        </v-list-item-title>
      </v-list-item>

      <v-list-item
        v-if="
          person.userid && person.email && person.canSendPasswordResetRequest
        "
        @click="showConfirmPasswordReset = true"
        class="text-error"
      >
        <template #prepend>
          <v-icon color="error">mdi-form-textbox-password</v-icon>
        </template>

        <v-list-item-title>
          {{ $t("accounts.reset_password.button") }}
        </v-list-item-title>
      </v-list-item>

      <v-list-item
        v-if="person.userid && person.canChangePassword"
        class="text-error"
        :to="{
          name: 'core.personById',
          params: { id: person.id },
          query: { _ui_action: 'change_password' },
        }"
      >
        <template #prepend>
          <v-icon color="error">mdi-form-textbox-password</v-icon>
        </template>

        <v-list-item-title>
          {{ $t("accounts.change_password.action") }}
        </v-list-item-title>
      </v-list-item>
    </button-menu>
    <c-r-u-d-provider
      disable-query
      disable-create
      disable-patch
      :object-schema="{ type: 'PersonType' }"
      name-attribute="fullName"
      :delete-items="deleteItems"
      @delete-done="handleDeleteDone"
    />
    <confirm-dialog
      v-model="showConfirmPasswordReset"
      @confirm="sendPasswortReset"
    >
      <template #title>
        {{ $t("accounts.reset_password.foreign_user.confirm.title") }}
      </template>
      <template #text>
        {{ $t("accounts.reset_password.foreign_user.confirm.message") }}
      </template>
    </confirm-dialog>
  </div>
</template>

<script>
import { deletePersons } from "./personList.graphql";
import { requestPasswordReset } from "../account/passwordReset.graphql";

export default {
  name: "PersonActions",
  props: {
    person: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      showDeleteConfirm: false,
      showConfirmPasswordReset: false,
      deleteMutation: deletePersons,
    };
  },
  methods: {
    sendPasswortReset() {
      this.$apollo
        .mutate({
          mutation: requestPasswordReset,
          variables: {
            email: this.person.email,
          },
        })
        .then(() => {
          this.$toastSuccess(this.$t("accounts.reset_password.done.title"));
        })
        .catch((error) => {
          this.handleMutationError(error);
        })
        .finally(() => {
          this.handleLoading(false);
        });
    },
  },
};
</script>

<style scoped></style>
