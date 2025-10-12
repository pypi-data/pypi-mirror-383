<template>
  <div class="mt-4 mb-4">
    <about-aleksis></about-aleksis>
    <installed-apps-list />
  </div>
</template>

<script>
import InstalledAppsList from "./InstalledAppsList.vue";
import AboutAleksis from "./AboutAleksis.vue";

export default {
  name: "About",
  components: { AboutAleksis, InstalledAppsList },
};
</script>
