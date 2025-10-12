<template>
  <v-card class="mb-4">
    <v-card-title>
      <v-icon class="mr-2" size="large">mdi-key-outline</v-icon>
      {{ $t("accounts.two_factor.webauthn.title") }}
      <v-spacer />
      <activated-chip :activated="webauthn.authenticators.length > 0">
        <template #activated>
          {{
            $tc(
              "accounts.two_factor.webauthn.count",
              webauthn.authenticators.length,
              {
                count: webauthn.authenticators.length,
              },
            )
          }}
        </template>
        <template #deactivated>
          {{
            $tc(
              "accounts.two_factor.webauthn.count",
              webauthn.authenticators.length,
              {
                count: webauthn.authenticators.length,
              },
            )
          }}
        </template>
      </activated-chip>
    </v-card-title>
    <v-card-text>
      <span>{{ $t("accounts.two_factor.webauthn.description") }}</span>
    </v-card-text>
    <v-list lines="two">
      <v-list-item
        v-for="authenticator in webauthn.authenticators"
        :key="authenticator.id"
      >
        <v-list-item-title>
          {{ authenticator.name }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{
            $t("accounts.two_factor.webauthn.key_added_at", {
              created: $d($parseISODate(authenticator.createdAt), "short"),
            })
          }}
          {{
            authenticator.lastUsedAt
              ? $t("accounts.two_factor.webauthn.key_last_used_at", {
                  last_used: $d(
                    $parseISODate(authenticator.lastUsedAt, "shortDateTime"),
                  ),
                })
              : $t("accounts.two_factor.webauthn.key_never_used")
          }}
        </v-list-item-subtitle>
        <v-list-item-action>
          <icon-button
            :to="{
              name: 'core.twoFactor',
              query: { _ui_action: 'deactivate', id: authenticator.id },
            }"
            icon-text="mdi-delete-outline"
            i18n-key="accounts.two_factor.deactivate_button"
            color="red"
          />
        </v-list-item-action>
      </v-list-item>
    </v-list>
    <v-card-actions>
      <activate-webauthn-dialog @save="$emit('save')" />
      <secondary-action-button
        :to="{
          name: 'core.twoFactor',
          query: { _ui_action: 'activate_webauthn' },
        }"
        i18n-key="accounts.two_factor.webauthn.activate_button"
        icon-text="mdi-key-plus"
        color="primary"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { defineEmits, defineProps } from "vue";
import ActivatedChip from "../ActivatedChip.vue";
import ActivateWebauthnDialog from "./ActivateWebauthnDialog.vue";

defineEmits(["save"]);
defineProps({
  webauthn: {
    type: Object,
    required: true,
  },
});
</script>
