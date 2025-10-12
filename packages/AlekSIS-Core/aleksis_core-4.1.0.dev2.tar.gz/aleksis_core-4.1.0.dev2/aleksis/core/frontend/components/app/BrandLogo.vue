<template>
  <img
    :src="sitePreferences.themeLogo.url"
    :alt="sitePreferences.generalTitle + ' – ' + $t('base.logo')"
    class="fullsize"
  />
</template>

<script>
export default {
  name: "BrandLogo",
  props: {
    sitePreferences: {
      type: Object,
      required: true,
    },
  },
};
</script>
