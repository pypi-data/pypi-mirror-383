<!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
<template>
  <v-card v-bind="$attrs">
    <v-card-title>{{ $t(titleKey) }}</v-card-title>

    <v-list lines="two">
      <v-list-item
        v-if="
          showWhenEmpty ||
          person.firstName ||
          person.additionalName ||
          person.lastName
        "
        prepend-icon="mdi-account-outline"
      >
        <v-list-item-title>
          {{ person.firstName }}
          {{ person.additionalName }}
          {{ person.lastName }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("person.name") }}
        </v-list-item-subtitle>
      </v-list-item>
      <v-divider inset />

      <v-list-item v-if="showUsername" prepend-icon="mdi-login-variant">
        <v-list-item-title>
          {{ person.username }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("person.username") }}
        </v-list-item-subtitle>
      </v-list-item>
      <v-divider inset />

      <v-list-item
        v-if="showWhenEmpty || person.sex"
        prepend-icon="mdi-human-non-binary"
      >
        <v-list-item-title>
          {{ person.sex ? $t(`person.sex.${person.sex.toLowerCase()}`) : "–" }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("person.sex_description") }}
        </v-list-item-subtitle>
      </v-list-item>
      <v-divider inset />

      <v-list-item
        v-for="(address, index) in filteredAddresses"
        :key="address.id"
      >
        <template #prepend>
          <v-icon v-if="index === 0">mdi-map-marker-outline</v-icon>
          <!-- TODO: test if this still works -->
          <div v-else></div>
        </template>

        <v-list-item-title>
          {{ address.street || "–" }} {{ address.housenumber }}
          <span v-if="address.postalCode || address.place || address.country">
            ,
          </span>
          <br v-if="address.postalCode || address.place" />
          {{ address.postalCode }} {{ address.place }}
          <span v-if="(address.postalCode || address.place) && address.country">
            ,
          </span>
          <br v-if="address.country" />
          {{ address.country }}
        </v-list-item-title>
        <v-list-item-subtitle
          v-for="addresstype in address.addressTypes"
          :key="addresstype.id"
        >
          {{ addresstype.name }}
        </v-list-item-subtitle>
      </v-list-item>

      <v-list-item
        v-if="showWhenEmpty || person.phoneNumber"
        :href="person.phoneNumber ? 'tel:' + person.phoneNumber : ''"
        prepend-icon="mdi-phone-outline"
      >
        <v-list-item-title>
          {{ person.phoneNumber || "–" }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("person.home") }}
        </v-list-item-subtitle>
      </v-list-item>

      <v-list-item
        v-if="showWhenEmpty || person.mobileNumber"
        :href="person.mobileNumber ? 'tel:' + person.mobileNumber : ''"
      >
        <template #prepend>
          <v-avatar />
        </template>

        <v-list-item-title>
          {{ person.mobileNumber || "–" }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("person.mobile") }}
        </v-list-item-subtitle>
      </v-list-item>
      <v-divider inset />

      <v-list-item
        v-if="showWhenEmpty || person.email"
        :href="person.email ? 'mailto:' + person.email : ''"
        prepend-icon="mdi-email-outline"
      >
        <v-list-item-title>
          {{ person.email || "–" }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ $t("person.email_address") }}
        </v-list-item-subtitle>
      </v-list-item>
      <v-divider inset />

      <v-list-item
        v-if="showWhenEmpty || person.dateOfBirth || person.placeOfBirth"
        prepend-icon="mdi-cake-variant-outline"
      >
        <v-list-item-title>
          <span v-if="person.dateOfBirth && person.placeOfBirth">
            {{
              $t("person.birth_date_and_birth_place_formatted", {
                date: $d($parseISODate(person.dateOfBirth), "short"),
                place: person.placeOfBirth,
              })
            }}
          </span>
          <span v-else-if="person.dateOfBirth">{{
            $d($parseISODate(person.dateOfBirth), "short")
          }}</span>
          <span v-else-if="person.placeOfBirth">{{ person.placeOfBirth }}</span>
          <span v-else>–</span>
        </v-list-item-title>
        <v-list-item-subtitle>
          <span v-if="!person.dateOfBirth === !person.placeOfBirth">
            {{ $t("person.birth_date_and_birth_place") }}
          </span>
          <span v-else-if="person.dateOfBirth">
            {{ $t("person.birth_date") }}
          </span>
          <span v-else-if="person.placeOfBirth">
            {{ $t("person.birth_place") }}
          </span>
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script>
export default {
  name: "PersonDetailsCard",
  props: {
    person: {
      type: Object,
      required: true,
    },
    showUsername: {
      type: Boolean,
      required: false,
      default: false,
    },
    titleKey: {
      type: String,
      required: false,
      default: "person.details",
    },
    showWhenEmpty: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
  computed: {
    filteredAddresses() {
      if (this.showWhenEmpty) {
        return this.person.addresses;
      }
      return this.person.addresses.filter(
        (a) =>
          a.street || a.housenumber || a.postalCode || a.place || a.country,
      );
    },
  },
};
</script>
