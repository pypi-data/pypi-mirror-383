<template>
  <v-menu>
    <template #activator="{ props }">
      <v-avatar
        v-bind="props"
        tag="button"
        tabindex="0"
        :aria-label="$t('actions.account_menu')"
        class="fullsize"
      >
        <avatar-content
          v-if="whoAmI.person"
          :image-url="whoAmI.person.avatarContentUrl"
          :id="whoAmI.person.id"
        />
        <v-icon v-else>mdi-person</v-icon>
      </v-avatar>
    </template>
    <v-list>
      <v-list-subheader>
        {{
          $t(
            whoAmI && whoAmI.isImpersonate
              ? "person.impersonation.impersonating"
              : "person.logged_in_as",
          )
        }}
        {{ whoAmI.person.fullName ? whoAmI.person.fullName : whoAmI.username }}
      </v-list-subheader>
      <v-list-item
        v-if="whoAmI && whoAmI.isImpersonate"
        :to="{ name: 'impersonate.stop', query: { next: $route.path } }"
      >
        <template #prepend>
          <v-icon> mdi-stop</v-icon>
        </template>
        <v-list-item-title>
          {{ $t("person.impersonation.stop") }}
        </v-list-item-title>
      </v-list-item>
      <div v-for="menuItem in accountMenu" :key="menuItem.name">
        <v-divider v-if="menuItem.divider"></v-divider>
        <v-list-item
          :to="{ name: menuItem.name }"
          :target="menuItem.newTab ? '_blank' : '_self'"
        >
          <template #prepend>
            <v-icon v-if="menuItem.icon">{{ menuItem.icon }}</v-icon>
          </template>
          <v-list-item-title>{{
            !menuItem.rawTitleString
              ? $t(menuItem.titleKey)
              : menuItem.rawTitleString
          }}</v-list-item-title>
        </v-list-item>
      </div>
    </v-list>
  </v-menu>
</template>

<script>
import AvatarContent from "../person/AvatarContent.vue";

export default {
  name: "AccountMenu",
  components: { AvatarContent },
  props: {
    accountMenu: {
      type: Array,
      required: false,
      default: () => [],
    },
    systemProperties: {
      type: Object,
      required: true,
    },
    whoAmI: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style></style>
