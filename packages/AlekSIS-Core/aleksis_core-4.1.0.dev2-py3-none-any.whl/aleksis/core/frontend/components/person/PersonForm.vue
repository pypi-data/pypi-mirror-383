<script setup>
import PersonField from "../generic/forms/PersonField.vue";
import GroupField from "../generic/forms/GroupField.vue";
import DateField from "../generic/forms/DateField.vue";
import FileField from "../generic/forms/FileField.vue";
import SexSelect from "../generic/forms/SexSelect.vue";
import CountryField from "../generic/forms/CountryField.vue";
import FullscreenDialogObjectForm from "../generic/crud/FullscreenDialogObjectForm.vue";
import AdditionalImage from "./AdditionalImage.vue";
</script>

<template>
  <fullscreen-dialog-object-form
    v-bind="$attrs"
    :i18n-key="i18nKey"
    :gql-query="gqlQuery"
    :gql-delete-mutation="gqlDeleteMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-create-mutation="gqlCreateMutation"
    full-width
    :fields="filteredFields"
    :create-item-i18n-key="createItemI18nKey"
    :edit-item-i18n-key="editItemI18nKey"
    :get-patch-data="getPatchData"
    :edit-item="editItem"
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #firstName.field="{ attrs, on }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          :rules="$rules().required.build()"
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #lastName.field="{ attrs, on }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          :rules="$rules().required.build()"
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #user.field="{ attrs, on }">
      <v-autocomplete
        :items="users"
        item-title="username"
        item-value="id"
        v-bind="attrs"
        v-on="on"
        chips
        closable-chips
      />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #primaryGroup.field="{ attrs, on }">
      <group-field v-bind="attrs" v-on="on" chips deletable-chips />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #guardians.field="{ attrs, on }">
      <person-field
        v-bind="attrs"
        v-on="on"
        multiple
        chips
        deletable-chips
        :server-search="true"
        :initial-items="person ? person.guardians : []"
      />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #sex.field="{ attrs, on }">
      <sex-select v-bind="attrs" v-on="on" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #dateOfBirth.field="{ attrs, on, item, isCreate }">
      <date-field v-bind="attrs" v-on="on"></date-field>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #postalCode.field="{ attrs, on }">
      <div aria-required="false">
        <v-text-field v-bind="attrs" v-on="on" />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #country.field="{ attrs, on }">
      <country-field v-bind="attrs" v-on="on" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #email.field="{ attrs, on }">
      <div aria-required="false">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          :rules="$rules().isEmail.build()"
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #avatar.field="{ attrs, on }">
      <div aria-required="false">
        <file-field v-bind="attrs" v-on="on" accept="image/jpeg, image/png">
          <template #append-outer="{ fileUrl }">
            <additional-image
              :src="fileUrl"
              :hide-card-title="true"
              activator-max-width="32"
            />
          </template>
        </file-field>
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #photo.field="{ attrs, on }">
      <div aria-required="false">
        <file-field v-bind="attrs" v-on="on" accept="image/jpeg, image/png">
          <template #append-outer="{ fileUrl }">
            <additional-image
              :src="fileUrl"
              :hide-card-title="true"
              activator-max-width="32"
            />
          </template>
        </file-field>
      </div>
    </template>
  </fullscreen-dialog-object-form>
</template>

<script>
import formRulesMixin from "../../mixins/formRulesMixin.js";
import permissionsMixin from "../../mixins/permissions.js";
import personCRUDMixin from "../../mixins/personCRUDMixin.js";

import { gqlEditableFieldsPreference, gqlUsers } from "./personForm.graphql";

import gqlPersonOverview from "./personOverview.graphql";

export default {
  name: "PersonForm",
  mixins: [formRulesMixin, permissionsMixin, personCRUDMixin],
  data() {
    return {
      fields: [
        {
          text: this.$t("person.form.titles.base_data"),
          value: "baseData",
          title: true,
        },
        {
          text: this.$t("person.first_name"),
          value: "firstName",
          cols: 4,
        },
        {
          text: this.$t("person.additional_name"),
          value: "additionalName",
          cols: 4,
        },
        {
          text: this.$t("person.last_name"),
          value: "lastName",
          cols: 4,
        },
        {
          text: this.$t("person.short_name"),
          value: "shortName",
        },
        {
          text: this.$t("person.user"),
          value: "user",
        },
        {
          text: this.$t("person.form.titles.address"),
          value: "address",
          title: true,
        },
        {
          text: this.$t("person.street"),
          value: "street",
          cols: 9,
        },
        {
          text: this.$t("person.housenumber"),
          value: "housenumber",
          cols: 3,
        },
        {
          text: this.$t("person.postal_code"),
          value: "postalCode",
          cols: 4,
        },
        {
          text: this.$t("person.place"),
          value: "place",
          cols: 4,
        },
        {
          text: this.$t("person.country"),
          value: "country",
          cols: 4,
        },
        {
          text: this.$t("person.form.titles.contact_data"),
          value: "contactData",
          title: true,
        },
        {
          text: this.$t("person.email"),
          value: "email",
          cols: 12,
        },
        {
          text: this.$t("person.phone_number"),
          value: "phoneNumber",
          type: "phonenumber",
        },
        {
          text: this.$t("person.mobile_number"),
          value: "mobileNumber",
          type: "phonenumber",
        },
        {
          text: this.$t("person.form.titles.advanced_personal_data"),
          value: "advancedPersonalData",
          title: true,
        },
        {
          text: this.$t("person.date_of_birth"),
          value: "dateOfBirth",
        },
        {
          text: this.$t("person.place_of_birth"),
          value: "placeOfBirth",
        },
        {
          text: this.$t("person.sex.field"),
          value: "sex",
        },
        {
          text: this.$t("person.primary_group"),
          value: "primaryGroup",
        },
        {
          text: this.$t("person.guardians"),
          value: "guardians",
          cols: 12,
        },
        {
          text: this.$t("person.description"),
          value: "description",
          cols: 12,
        },
        {
          text: this.$t("person.avatar"),
          value: "avatar",
        },
        {
          text: this.$t("person.photo"),
          value: "photo",
        },
      ],
      createItemI18nKey: "person.form.create",
      editItemI18nKey: "person.form.edit",
      person: null,
      users: [],
    };
  },
  props: {
    id: {
      type: String,
      required: false,
      default: null,
    },
  },
  apollo: {
    users: gqlUsers,
    systemProperties: {
      query: gqlEditableFieldsPreference,
    },
    person: {
      query: gqlPersonOverview,
      variables() {
        return {
          id: this.id,
        };
      },
      skip() {
        return !this.id;
      },
      update: (data) => data.object,
    },
  },
  computed: {
    editPersonID() {
      return this.$attrs["edit-item"]?.id;
    },
    areEditableFieldsSet() {
      if (this.$attrs["isCreate"] || !this.editPersonID) {
        return false;
      }
      return (
        !this.$attrs["isCreate"] &&
        !this.checkPermission("core.change_person") &&
        !this.checkObjectPermission(
          "core.change_person",
          this.editPersonID,
          "person",
        )
      );
    },
    editableFields() {
      if (this.systemProperties?.sitePreferences?.editableFieldsPerson) {
        return this.systemProperties.sitePreferences.editableFieldsPerson.map(
          (string) => this.toCamelCase(string),
        );
      }
      return [];
    },
    filteredFields() {
      if (this.areEditableFieldsSet) {
        return this.fields.map((f) => ({
          ...f,
          ...(!this.editableFields.includes(f.value) && { disabled: true }),
        }));
      }
      return this.fields;
    },
    editItem() {
      if (this.person) {
        return {
          id: this.person.id,
          firstName: this.person.firstName,
          additionalName: this.person.additionalName,
          lastName: this.person.lastName,
          shortName: this.person.shortName,
          user: this.person.userid,
          description: this.person.description,
          sex: this.person.sex,
          street: this.person.addresses[0]?.street,
          housenumber: this.person.addresses[0]?.housenumber,
          postalCode: this.person.addresses[0]?.postalCode,
          place: this.person.addresses[0]?.place,
          country: this.person.addresses[0]?.country,
          phoneNumber: this.person.phoneNumber,
          mobileNumber: this.person.mobileNumber,
          email: this.person.email,
          dateOfBirth: this.person.dateOfBirth,
          placeOfBirth: this.person.placeOfBirth,
          photo: this.person.photo,
          avatar: this.person.avatar,
          guardians: this.person.guardians.map((g) => g.id),
          primaryGroup: this.person?.primaryGroup?.id,
        };
      }
      return null;
    },
  },
  methods: {
    handleNameInput(input, itemModel, setter) {
      if (!itemModel.shortName || itemModel.shortName.length < 2) {
        setter("shortName", input.substring(0, 3));
      }
    },
    toCamelCase(string) {
      return string.replace(/([-_][a-z])/gi, (part) => {
        return part.toUpperCase().replace("-", "").replace("_", "");
      });
    },
    getPatchData(item) {
      if (this.checkEditableFieldsPreference) {
        return ["id", ...this.editableFields]
          .filter((key) => key in item)
          .reduce(
            (reducedItem, key) => ((reducedItem[key] = item[key]), reducedItem),
            {},
          );
      }
      return item;
    },
  },
  mounted() {
    if (!this.$attrs["isCreate"] && this.editPersonID) {
      this.addPermissions(["core.change_person"]);
      this.addObjectPermission(
        "core.change_person",
        this.editPersonID,
        "person",
        "core",
      );
    }
  },
};
</script>

<style scoped></style>
