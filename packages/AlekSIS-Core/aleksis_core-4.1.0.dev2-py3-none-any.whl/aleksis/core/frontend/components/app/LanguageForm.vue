<template>
  <v-select
    v-if="availableLanguages"
    v-model="language"
    :items="availableLanguages"
    :item-title="nameForMenu"
    item-value="code"
    variant="outlined"
    color="primary"
    hide-details="auto"
    single-line
    return-object
    density="compact"
    style="width: 75px"
    @update:model-value="setLanguage(language)"
  >
    <template #selection="{ item, index }">
      <span class="text-uppercase">{{ item.value }}</span>
    </template>
  </v-select>
</template>

<script>
export default {
  data: function () {
    return {
      language: {
        code: this.$i18n.locale,
      },
    };
  },
  props: {
    availableLanguages: {
      type: Array,
      required: true,
    },
    defaultLanguage: {
      type: Object,
      required: true,
    },
  },
  methods: {
    setLanguage: function (languageOption) {
      document.cookie = languageOption.cookie;
      this.$i18n.locale = languageOption.code;
      this.$vuetify.locale.current = languageOption.code;
      document.getElementsByTagName("html")[0].lang = languageOption.code;
      this.language = languageOption;
    },
    nameForMenu: function (item) {
      return `${item.nameLocal} (${item.code})`;
    },
  },
  mounted() {
    if (
      this.availableLanguages.filter((lang) => lang.code === this.$i18n.locale)
        .length === 0
    ) {
      console.warn(
        `Unsupported language ${this.$i18n.locale} selected, defaulting to ${this.defaultLanguage.code}`,
      );
      this.setLanguage(this.defaultLanguage);
    }
  },
  name: "LanguageForm",
};
</script>
