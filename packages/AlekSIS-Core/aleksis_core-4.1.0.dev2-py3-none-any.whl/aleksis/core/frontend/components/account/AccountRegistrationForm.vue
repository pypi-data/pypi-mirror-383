<script setup>
import ControlRow from "../generic/multi_step/ControlRow.vue";
import DateField from "../generic/forms/DateField.vue";
import FileField from "../generic/forms/FileField.vue";
import SexSelect from "../generic/forms/SexSelect.vue";
import CountryField from "../generic/forms/CountryField.vue";
import PasswordField from "../generic/forms/PasswordField.vue";

import PrimaryActionButton from "../generic/buttons/PrimaryActionButton.vue";

import PersonDetailsCard from "../person/PersonDetailsCard.vue";
</script>

<template>
  <div>
    <div v-if="accountRegistrationSent">
      <v-card>
        <v-card-title>
          <v-icon class="mr-2" color="success">mdi-check-circle-outline</v-icon>
          {{ $t("accounts.signup.form.submitted.title") }}
        </v-card-title>
        <v-card-text class="text-body-1 text-black">
          {{ $t("accounts.signup.form.submitted.submitted_successfully") }}
        </v-card-text>
        <v-card-actions>
          <primary-action-button
            :to="{ name: 'core.accounts.login' }"
            i18n-key="accounts.signup.form.login_button"
          />
        </v-card-actions>
      </v-card>
    </div>
    <div
      v-else-if="
        checkPermission('core.invite_enabled') && !invitationCodeEntered
      "
    >
      <v-card>
        <v-card-title>
          {{ $t("accounts.signup.form.steps.invitation.title") }}
        </v-card-title>
        <v-card-text>
          <v-alert
            v-if="invitationCodeAutofilled"
            type="info"
            variant="outlined"
            class="mb-4"
            >{{
              $t("accounts.signup.form.steps.invitation.autofilled")
            }}</v-alert
          >
          <div class="mb-4">
            <v-form v-model="invitationCodeValidationStatus">
              <div :aria-required="invitationCodeRequired">
                <v-text-field
                  variant="outlined"
                  v-model="data.accountRegistration.invitationCode"
                  :label="
                    $t(
                      'accounts.signup.form.steps.invitation.fields.invitation_code.label',
                    )
                  "
                  :hint="
                    $t(
                      'accounts.signup.form.steps.invitation.fields.invitation_code.help_text',
                    )
                  "
                  persistent-hint
                  required
                  :rules="
                    invitationCodeRequired ? $rules().required.build() : []
                  "
                ></v-text-field>
              </div>
            </v-form>
          </div>
          <v-alert
            v-if="invitationCodeInvalid"
            type="error"
            variant="outlined"
            class="mb-4"
            >{{
              $t("accounts.signup.form.steps.invitation.not_valid")
            }}</v-alert
          >
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <primary-action-button
            @click="checkInvitationCode"
            :i18n-key="invitationNextI18nKey"
            :disabled="!invitationCodeValidationStatus"
          />
        </v-card-actions>
      </v-card>
    </div>
    <div v-else>
      <v-alert type="info" density="compact" variant="outlined" class="mb-4">
        <v-row align="center" no-gutters>
          <v-col cols="12" md="9">
            {{ $t("accounts.signup.form.existing_account_alert") }}
          </v-col>
          <v-col cols="12" md="3" align="right">
            <v-btn
              color="info"
              variant="outlined"
              size="small"
              :to="{ name: 'core.accounts.login' }"
            >
              {{ $t("accounts.signup.form.login_button") }}
            </v-btn>
          </v-col>
        </v-row>
      </v-alert>
      <v-stepper
        v-model="step"
        class="mb-4"
        v-if="isPermissionFetched('core.invite_enabled')"
      >
        <v-stepper-header>
          <template v-for="(stepChoice, index) in steps" :key="`${index}-step`">
            <v-stepper-step
              :complete="step > index + 1"
              :step="index + 1"
              :ref="`step-${index}`"
            >
              {{ $t(stepChoice.titleKey) }}
            </v-stepper-step>
            <v-divider v-if="index + 1 < steps.length"></v-divider>
          </template>
        </v-stepper-header>
        <v-stepper-items>
          <v-stepper-content
            v-if="isStepEnabled('email')"
            :step="getStepIndex('email')"
          >
            <h2 class="text-h6 mb-4">{{ $t(getStepTitleKey("email")) }}</h2>
            <div class="mb-4">
              <!-- TODO: Optional email fields when using injected component -->
              <component
                v-if="stepOverwrittenByInjection('email')"
                :is="collectionSteps.find((s) => s.key === 'email')?.component"
                @data-change="mergeIncomingData"
                v-model="validationStatuses['email']"
              />
              <v-form v-else v-model="validationStatuses['email']">
                <v-row class="mt-4">
                  <v-col cols="12" md="6">
                    <div :aria-required="isFieldRequired('email')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.user.email"
                        :label="
                          $t(
                            'accounts.signup.form.steps.email.fields.email.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('email')
                            ? $rules().required.isEmail.build()
                            : $rules().isEmail.build()
                        "
                        prepend-icon="mdi-email-outline"
                      ></v-text-field>
                    </div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div :aria-required="isFieldRequired('email')">
                      <v-text-field
                        variant="outlined"
                        v-model="confirmFields.email"
                        :label="
                          $t(
                            'accounts.signup.form.steps.email.fields.confirm_email.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('email')
                            ? $rules().required.build(rules.confirmEmail)
                            : rules.confirmEmail
                        "
                        prepend-icon="mdi-email-outline"
                      ></v-text-field>
                    </div>
                  </v-col>
                </v-row>
              </v-form>
            </div>
            <v-divider class="mb-4" />
            <control-row
              :step="step"
              @set-step="setStep"
              :next-disabled="!validationStatuses['email']"
            />
          </v-stepper-content>

          <v-stepper-content :step="getStepIndex('account')">
            <h2 class="text-h6 mb-4">{{ $t(getStepTitleKey("account")) }}</h2>
            <div class="mb-4">
              <v-form v-model="validationStatuses['account']">
                <v-row>
                  <v-col cols="12">
                    <div aria-required="true">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.user.username"
                        :label="
                          $t(
                            'accounts.signup.form.steps.account.fields.username.label',
                          )
                        "
                        required
                        :rules="
                          $rules().required.build([
                            ...usernameRules.usernameAllowed,
                            ...usernameRules.usernameASCII,
                          ])
                        "
                        prepend-icon="mdi-account-outline"
                      ></v-text-field>
                    </div>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" md="6">
                    <div aria-required="true">
                      <password-field
                        outlined
                        v-model="data.accountRegistration.user.password"
                        :label="
                          $t(
                            'accounts.signup.form.steps.account.fields.password.label',
                          )
                        "
                        required
                        :rules="$rules().required.build()"
                        prepend-icon="mdi-form-textbox-password"
                      />
                    </div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div aria-required="true">
                      <v-text-field
                        variant="outlined"
                        v-model="confirmFields.password"
                        :label="
                          $t(
                            'accounts.signup.form.steps.account.fields.confirm_password.label',
                          )
                        "
                        required
                        :rules="$rules().required.build(rules.confirmPassword)"
                        type="password"
                        prepend-icon="mdi-form-textbox-password"
                      ></v-text-field>
                    </div>
                  </v-col>
                </v-row>
              </v-form>
            </div>
            <v-divider class="mb-4" />
            <control-row
              :step="step"
              @set-step="setStep"
              :next-disabled="!validationStatuses['account']"
            />
          </v-stepper-content>

          <v-stepper-content :step="getStepIndex('base_data')">
            <h2 class="text-h6 mb-4">
              {{ $t(getStepTitleKey("base_data")) }}
            </h2>
            <div class="mb-4">
              <v-form v-model="validationStatuses['base_data']">
                <v-row>
                  <v-col>
                    <div aria-required="true">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.firstName"
                        :label="
                          $t(
                            'accounts.signup.form.steps.base_data.fields.first_name.label',
                          )
                        "
                        required
                        :rules="$rules().required.build()"
                      ></v-text-field>
                    </div>
                  </v-col>
                  <v-col v-if="isFieldVisible('additional_name')">
                    <div :aria-required="isFieldRequired('additional_name')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.additionalName"
                        :label="
                          $t(
                            'accounts.signup.form.steps.base_data.fields.additional_name.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('additional_name')
                            ? $rules().required.build()
                            : []
                        "
                      ></v-text-field>
                    </div>
                  </v-col>
                  <v-col>
                    <div aria-required="true">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.lastName"
                        :label="
                          $t(
                            'accounts.signup.form.steps.base_data.fields.last_name.label',
                          )
                        "
                        required
                        :rules="$rules().required.build()"
                      ></v-text-field>
                    </div>
                  </v-col>
                </v-row>
              </v-form>
            </div>
            <v-divider class="mb-4" />
            <control-row
              :step="step"
              @set-step="setStep"
              :next-disabled="!validationStatuses['base_data']"
            />
          </v-stepper-content>

          <v-stepper-content :step="getStepIndex('address_data')">
            <h2 class="text-h6 mb-4">
              {{ $t(getStepTitleKey("address_data")) }}
            </h2>
            <div class="mb-4">
              <v-form v-model="validationStatuses['address_data']">
                <v-row>
                  <v-col cols="12" lg="6" v-if="isFieldVisible('street')">
                    <div :aria-required="isFieldRequired('street')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.street"
                        :label="
                          $t(
                            'accounts.signup.form.steps.address_data.fields.street.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('street')
                            ? $rules().required.build()
                            : []
                        "
                      ></v-text-field>
                    </div>
                  </v-col>
                  <v-col cols="12" lg="6" v-if="isFieldVisible('housenumber')">
                    <div :aria-required="isFieldRequired('housenumber')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.housenumber"
                        :label="
                          $t(
                            'accounts.signup.form.steps.address_data.fields.housenumber.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('housenumber')
                            ? $rules().required.build()
                            : []
                        "
                      ></v-text-field>
                    </div>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" lg="4" v-if="isFieldVisible('postal_code')">
                    <div :aria-required="isFieldRequired('postal_code')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.postalCode"
                        :label="
                          $t(
                            'accounts.signup.form.steps.address_data.fields.postal_code.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('postal_code')
                            ? $rules().required.build()
                            : []
                        "
                      ></v-text-field>
                    </div>
                  </v-col>
                  <v-col cols="12" lg="4" v-if="isFieldVisible('place')">
                    <div :aria-required="isFieldRequired('place')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.place"
                        :label="
                          $t(
                            'accounts.signup.form.steps.address_data.fields.place.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('place')
                            ? $rules().required.build()
                            : []
                        "
                      ></v-text-field>
                    </div>
                  </v-col>
                  <v-col cols="12" lg="4" v-if="isFieldVisible('country')">
                    <div :aria-required="isFieldRequired('country')">
                      <country-field
                        outlined
                        v-model="data.accountRegistration.person.country"
                        :label="
                          $t(
                            'accounts.signup.form.steps.address_data.fields.country.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('country')
                            ? $rules().required.build()
                            : []
                        "
                      />
                    </div>
                  </v-col>
                </v-row>
              </v-form>
            </div>
            <v-divider class="mb-4" />
            <control-row
              :step="step"
              @set-step="setStep"
              :next-disabled="!validationStatuses['address_data']"
            />
          </v-stepper-content>

          <v-stepper-content :step="getStepIndex('contact_data')">
            <h2 class="text-h6 mb-4">
              {{ $t(getStepTitleKey("contact_data")) }}
            </h2>
            <div class="mb-4">
              <v-form v-model="validationStatuses['contact_data']">
                <v-row>
                  <v-col
                    cols="12"
                    md="6"
                    v-if="isFieldVisible('mobile_number')"
                  >
                    <div :aria-required="isFieldRequired('mobile_number')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.mobileNumber"
                        :label="
                          $t(
                            'accounts.signup.form.steps.contact_data.fields.mobile_number.label',
                          )
                        "
                        required
                        prepend-icon="mdi-cellphone-basic"
                        :rules="
                          isFieldRequired('mobile_number')
                            ? $rules().required.build()
                            : []
                        "
                      ></v-text-field>
                    </div>
                  </v-col>
                  <v-col cols="12" md="6" v-if="isFieldVisible('phone_number')">
                    <div :aria-required="isFieldRequired('phone_number')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.phoneNumber"
                        :label="
                          $t(
                            'accounts.signup.form.steps.contact_data.fields.phone_number.label',
                          )
                        "
                        required
                        prepend-icon="mdi-phone-outline"
                        :rules="
                          isFieldRequired('phone_number')
                            ? $rules().required.build()
                            : []
                        "
                      ></v-text-field>
                    </div>
                  </v-col>
                </v-row>
              </v-form>
            </div>
            <v-divider class="mb-4" />
            <control-row
              :step="step"
              @set-step="setStep"
              :next-disabled="!validationStatuses['contact_data']"
            />
          </v-stepper-content>

          <v-stepper-content :step="getStepIndex('additional_data')">
            <h2 class="text-h6 mb-4">
              {{ $t(getStepTitleKey("additional_data")) }}
            </h2>
            <div class="mb-4">
              <v-form v-model="validationStatuses['additional_data']">
                <v-row>
                  <v-col
                    cols="12"
                    md="6"
                    v-if="isFieldVisible('date_of_birth')"
                  >
                    <div :aria-required="isFieldRequired('date_of_birth')">
                      <date-field
                        outlined
                        v-model="data.accountRegistration.person.dateOfBirth"
                        :label="
                          $t(
                            'accounts.signup.form.steps.additional_data.fields.date_of_birth.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('date_of_birth')
                            ? $rules().required.build()
                            : []
                        "
                        prepend-icon="mdi-cake-variant-outline"
                      />
                    </div>
                  </v-col>
                  <v-col
                    cols="12"
                    md="6"
                    v-if="isFieldVisible('place_of_birth')"
                  >
                    <div :aria-required="isFieldRequired('place_of_birth')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.placeOfBirth"
                        :label="
                          $t(
                            'accounts.signup.form.steps.additional_data.fields.place_of_birth.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('place_of_birth')
                            ? $rules().required.build()
                            : []
                        "
                      />
                    </div>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" md="6" v-if="isFieldVisible('sex')">
                    <div :aria-required="isFieldRequired('sex')">
                      <sex-select
                        outlined
                        v-model="data.accountRegistration.person.sex"
                        :label="
                          $t(
                            'accounts.signup.form.steps.additional_data.fields.sex.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('sex')
                            ? $rules().required.build()
                            : []
                        "
                      />
                    </div>
                  </v-col>
                  <v-col cols="12" md="6" v-if="isFieldVisible('photo')">
                    <div :aria-required="isFieldRequired('photo')">
                      <file-field
                        outlined
                        v-model="data.accountRegistration.person.photo"
                        accept="image/jpeg, image/png"
                        :label="
                          $t(
                            'accounts.signup.form.steps.additional_data.fields.photo.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('photo')
                            ? $rules().required.build()
                            : []
                        "
                      />
                    </div>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" v-if="isFieldVisible('description')">
                    <div :aria-required="isFieldRequired('description')">
                      <v-text-field
                        variant="outlined"
                        v-model="data.accountRegistration.person.description"
                        :label="
                          $t(
                            'accounts.signup.form.steps.additional_data.fields.description.label',
                          )
                        "
                        required
                        :rules="
                          isFieldRequired('description')
                            ? $rules().required.build()
                            : []
                        "
                      />
                    </div>
                  </v-col>
                </v-row>
              </v-form>
            </div>
            <v-divider class="mb-4" />
            <control-row
              :step="step"
              @set-step="setStep"
              :next-disabled="!validationStatuses['additional_data']"
            />
          </v-stepper-content>

          <v-stepper-content :step="getStepIndex('confirm')">
            <h2 class="text-h6 mb-4">{{ $t(getStepTitleKey("confirm")) }}</h2>
            <v-alert
              v-if="invitation && (invitation.hasEmail || invitation.hasPerson)"
              type="info"
              variant="outlined"
              class="mb-4"
              >{{
                $t("accounts.signup.form.steps.confirm.invitation_used")
              }}</v-alert
            >
            <person-details-card
              class="mb-4"
              :person="personDataForSummary"
              :show-username="true"
              :show-when-empty="false"
              title-key="accounts.signup.form.steps.confirm.card_title"
            />

            <div
              v-if="systemProperties.sitePreferences.footerPrivacyUrl"
              aria-required="true"
              class="mb-4"
            >
              <v-checkbox required v-model="privacyPolicyAccepted">
                <template #label>
                  <i18n-t
                    keypath="accounts.signup.form.steps.confirm.privacy_policy.label"
                    tag="div"
                  >
                    <template #url>
                      <a
                        @click.stop
                        :href="
                          systemProperties.sitePreferences.footerPrivacyUrl
                        "
                        target="_blank"
                        >{{
                          $t(
                            "accounts.signup.form.steps.confirm.privacy_policy.url_text",
                          )
                        }}</a
                      >
                    </template>
                  </i18n-t>
                </template>
              </v-checkbox>
            </div>

            <ApolloMutation
              :mutation="combinedMutation"
              :variables="dataForMutation"
              @done="accountRegistrationDone"
            >
              <template #default="{ mutate, loading, error }">
                <control-row
                  :step="step"
                  final-step
                  @set-step="setStep"
                  @confirm="mutate"
                  :next-loading="loading"
                  :next-disabled="disableConfirm"
                />
                <v-alert
                  v-if="error"
                  type="error"
                  variant="outlined"
                  class="mt-4"
                  >{{ error.message }}</v-alert
                >
              </template>
            </ApolloMutation>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </div>
  </div>
</template>

<script>
import {
  gqlAccountWizardSystemProperties,
  gqlPersonInvitationByCode,
} from "./helpers.graphql";
import { sendAccountRegistration } from "./accountRegistrationMutation.graphql";
import { collections } from "aleksisAppImporter";

import formRulesMixin from "../../mixins/formRulesMixin";
import permissionsMixin from "../../mixins/permissions";
import usernameRulesMixin from "../../mixins/usernameRulesMixin";

import combineQuery from "@/graphql-combine-query";

export default {
  name: "AccountRegistrationForm",
  apollo: {
    systemProperties: {
      query: gqlAccountWizardSystemProperties,
    },
    personInvitationByCode: {
      query: gqlPersonInvitationByCode,
      variables() {
        return {
          code: this.data.accountRegistration.invitationCode,
        };
      },
      result({ data }) {
        if (data?.personInvitationByCode?.valid) {
          this.invitation = data.personInvitationByCode;
          this.invitationCodeEntered = true;
        } else {
          this.invitationCodeInvalid = true;
        }
      },
      skip: true,
    },
  },
  mixins: [formRulesMixin, permissionsMixin, usernameRulesMixin],
  methods: {
    stepOverwrittenByInjection(step) {
      return this.collectionSteps.some((s) => s.key === step);
    },
    setStep(step) {
      this.step = step;
      this.valid = false;
    },
    checkInvitationCode() {
      this.invitationCodeInvalid = false;
      if (this.data.accountRegistration.invitationCode) {
        this.$apollo.queries.personInvitationByCode.skip = false;
        this.$apollo.queries.personInvitationByCode.refetch();
      } else {
        this.invitationCodeEntered = true;
      }
    },
    accountRegistrationDone({ data }) {
      if (data.sendAccountRegistration.ok) {
        this.accountRegistrationSent = true;
      }
    },
    isFieldRequired(fieldName) {
      return (
        this?.systemProperties?.sitePreferences?.signupRequiredFields?.includes(
          fieldName,
        ) ||
        this?.systemProperties?.sitePreferences?.signupAddressRequiredFields?.includes(
          fieldName,
        )
      );
    },
    isFieldVisible(fieldName) {
      return (
        this?.systemProperties?.sitePreferences?.signupVisibleFields?.includes(
          fieldName,
        ) ||
        this?.systemProperties?.sitePreferences?.signupAddressVisibleFields?.includes(
          fieldName,
        )
      );
    },
    isStepEnabled(stepName) {
      return this.steps.some((s) => s.name === stepName);
    },
    getStepIndex(stepName) {
      return this.steps.findIndex((s) => s.name === stepName) + 1;
    },
    getStepTitleKey(stepName) {
      return this.steps.find((s) => s.name === stepName)?.titleKey;
    },
    setValidationStatus(stepName, validationStatus) {
      this.validationStatuses[stepName] = validationStatus;
    },
    getValidationStatus(stepName) {
      if (this.validationStatuses[stepName]) {
        return this.validationStatuses[stepName];
      }
      return false;
    },
    deepMerge(existing, incoming) {
      return Object.entries(incoming).reduce(
        (merged, [key, value]) => {
          if (typeof value === "object") {
            if (Array.isArray(value)) {
              merged[key] = this.deepMerge(existing[key] || [], value);
            } else {
              merged[key] = this.deepMerge(existing[key] || [], value);
            }
          } else {
            merged[key] = value;
          }
          return merged;
        },
        { ...existing },
      );
    },
    mergeIncomingData(incomingData) {
      this.data = this.deepMerge(this.data, incomingData);
    },
  },
  computed: {
    rules() {
      return {
        confirmPassword: [
          (v) =>
            this.data.accountRegistration.user.password == v ||
            this.$t("accounts.signup.form.rules.confirm_password.no_match"),
        ],
        confirmEmail: [
          (v) =>
            this.data.accountRegistration.user.email == v ||
            this.$t("accounts.signup.form.rules.confirm_email.no_match"),
        ],
      };
    },
    personDataForSummary() {
      return {
        ...this.data.accountRegistration.person,
        addresses: [
          {
            street: this.data.accountRegistration.person.street,
            housenumber: this.data.accountRegistration.person.housenumber,
            postalCode: this.data.accountRegistration.person.postalCode,
            place: this.data.accountRegistration.person.place,
            country: this.data.accountRegistration.person.country,
          },
        ],
        username: this.data.accountRegistration.user.username,
        email: this.data.accountRegistration.user.email,
      };
    },
    steps() {
      return [
        ...(!this.invitation?.hasEmail && this.isFieldVisible("email")
          ? [
              {
                name: "email",
                titleKey: "accounts.signup.form.steps.email.title",
              },
            ]
          : []),
        {
          name: "account",
          titleKey: "accounts.signup.form.steps.account.title",
        },
        ...(!this.invitation?.hasPerson
          ? [
              {
                name: "base_data",
                titleKey: "accounts.signup.form.steps.base_data.title",
              },
            ]
          : []),
        ...(this.isFieldVisible("street") |
        this.isFieldVisible("housenumber") |
        this.isFieldVisible("postal_code") |
        this.isFieldVisible("place") |
        this.isFieldVisible("country")
          ? [
              {
                name: "address_data",
                titleKey: "accounts.signup.form.steps.address_data.title",
              },
            ]
          : []),
        ...(this.isFieldVisible("mobile_number") |
        this.isFieldVisible("phone_number")
          ? [
              {
                name: "contact_data",
                titleKey: "accounts.signup.form.steps.contact_data.title",
              },
            ]
          : []),
        ...(this.isFieldVisible("date_of_birth") |
        this.isFieldVisible("place_of_birth") |
        this.isFieldVisible("sex") |
        this.isFieldVisible("photo") |
        this.isFieldVisible("description")
          ? [
              {
                name: "additional_data",
                titleKey: "accounts.signup.form.steps.additional_data.title",
              },
            ]
          : []),
        {
          name: "confirm",
          titleKey: "accounts.signup.form.steps.confirm.title",
        },
      ];
    },
    collectionSteps() {
      if (Object.hasOwn(collections, "coreAccountRegistrationSteps")) {
        return collections.coreAccountRegistrationSteps.items;
      }
      return [];
    },
    collectionExtraMutations() {
      if (Object.hasOwn(collections, "coreAccountRegistrationExtraMutations")) {
        return collections.coreAccountRegistrationExtraMutations.items;
      }
      return [];
    },
    invitationNextI18nKey() {
      return this.data.accountRegistration.invitationCode
        ? "accounts.signup.form.steps.invitation.next.with_code"
        : this.invitationCodeRequired
          ? "accounts.signup.form.steps.invitation.next.code_required"
          : "accounts.signup.form.steps.invitation.next.without_code";
    },
    invitationCodeRequired() {
      return (
        this.checkPermission("core.invite_enabled") &&
        !this.checkPermission("core.signup_rule")
      );
    },
    combinedMutation() {
      let combinedQuery = combineQuery("combinedMutation").add(
        sendAccountRegistration,
      );

      this.collectionExtraMutations.forEach((extraMutation) => {
        if (Object.hasOwn(extraMutation, "mutation")) {
          combinedQuery = combinedQuery.add(extraMutation.mutation);
        }
      });

      const { document } = combinedQuery;

      return document;
    },
    disableConfirm() {
      return (
        !!this?.systemProperties?.sitePreferences?.footerPrivacyUrl &&
        !this.privacyPolicyAccepted
      );
    },
    dataForMutation() {
      // Due to the backend logic used for handling addresses, empty values have to be filtered out
      const addressKeys = [
        "street",
        "housenumber",
        "postalCode",
        "place",
        "country",
      ];

      const cleanedPerson = Object.fromEntries(
        Object.entries(this.data.accountRegistration.person).filter(
          ([key, value]) => !(addressKeys.includes(key) && value === ""),
        ),
      );

      return {
        ...this.data,
        accountRegistration: {
          ...this.data.accountRegistration,
          person: cleanedPerson,
        },
      };
    },
  },
  data() {
    return {
      validationStatuses: {},
      invitation: null,
      invitationCodeEntered: false,
      invitationCodeValidationStatus: false,
      invitationCodeInvalid: false,
      invitationCodeAutofilled: false,
      accountRegistrationSent: false,
      step: 1,
      privacyPolicyAccepted: false,
      confirmFields: {
        email: "",
        password: "",
      },
      data: {
        accountRegistration: {
          person: {
            firstName: "",
            additionalName: "",
            lastName: "",
            shortName: "",
            dateOfBirth: null,
            placeOfBirth: "",
            sex: "",
            street: "",
            housenumber: "",
            postalCode: "",
            place: "",
            country: "",
            mobileNumber: "",
            phoneNumber: "",
            description: "",
            photo: null,
          },
          user: {
            username: "",
            email: "",
            password: "",
          },
          invitationCode: "",
        },
      },
    };
  },
  watch: {
    step() {
      const comp = this.$refs[`step-${this.step - 1}`][0];
      comp.$el.scrollIntoView();
    },
  },
  mounted() {
    this.addPermissions(["core.signup_rule", "core.invite_enabled"]);
    if (this.$route.query.invitation_code) {
      this.data.accountRegistration.invitationCode =
        this.$route.query.invitation_code;
      this.invitationCodeAutofilled = true;
    }
  },
};
</script>

<style>
.v-stepper__header {
  overflow: auto;
  display: flex;
  flex-wrap: nowrap;
  justify-content: left;
}
</style>
