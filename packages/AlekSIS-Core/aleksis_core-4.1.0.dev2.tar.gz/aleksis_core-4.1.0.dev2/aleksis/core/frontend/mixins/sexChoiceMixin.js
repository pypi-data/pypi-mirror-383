/**
 * Mixin to supply choices for the supported sexes in AlekSIS
 */
export default {
  computed: {
    sexChoices() {
      return [
        {
          text: this.$t("person.sex.m"),
          value: "M",
          icon: "mdi-gender-male",
        },
        {
          text: this.$t("person.sex.f"),
          value: "F",
          icon: "mdi-gender-female",
        },
        {
          text: this.$t("person.sex.x"),
          value: "X",
          icon: "mdi-gender-non-binary",
        },
      ];
    },
  },
};
