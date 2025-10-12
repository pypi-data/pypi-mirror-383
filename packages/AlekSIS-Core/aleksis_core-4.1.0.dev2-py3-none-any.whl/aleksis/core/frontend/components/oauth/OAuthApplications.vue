<script setup>
import CRUDProvider from "../generic/crud/CRUDProvider.vue";
import MobileFullscreenDialog from "../generic/dialogs/MobileFullscreenDialog.vue";
import { ref, watch } from "vue";
import CopyToClipboardButton from "../generic/CopyToClipboardButton.vue";

const dialogMode = ref(false);
const createdApplication = ref(null);

function onCreateDone(data) {
  console.log(data);
  dialogMode.value = true;
  createdApplication.value = data.createOauthApplications.items[0];
}
watch(dialogMode.value, () => {
  if (!dialogMode.value) {
    createdApplication.value = null;
  }
});
</script>

<template>
  <div>
    <mobile-fullscreen-dialog v-model="dialogMode" hide-actions>
      <template #title>
        {{ $t("o_auth_application.credentials_created") }}
      </template>
      <template #content>
        <message-box type="warning" class="mb-4">
          {{ $t("o_auth_application.credentials_warning") }}
        </message-box>
        <v-text-field
          :model-value="createdApplication.clientId"
          read-only
          :label="$t('o_auth_application.client_id')"
          persistent-placeholder
        >
          <template #append>
            <copy-to-clipboard-button :text="createdApplication.clientId" />
          </template>
        </v-text-field>
        <v-text-field
          :model-value="createdApplication.clientSecret"
          read-only
          :label="$t('o_auth_application.client_secret')"
          persistent-placeholder
        >
          <template #append>
            <copy-to-clipboard-button :text="createdApplication.clientSecret" />
          </template>
        </v-text-field>
      </template>
    </mobile-fullscreen-dialog>
    <c-r-u-d-provider
      :object-schema="{ type: 'OAuthApplicationType' }"
      disable-inline-edit
      @create-done="onCreateDone"
    >
      <template #item.icon="{ item }">
        <v-img
          v-if="item.icon.url"
          :src="item.icon.url"
          :alt="$t('o_auth_application.icon')"
          max-width="6em"
        />
        <span v-else>–</span>
      </template>
    </c-r-u-d-provider>
  </div>
</template>
