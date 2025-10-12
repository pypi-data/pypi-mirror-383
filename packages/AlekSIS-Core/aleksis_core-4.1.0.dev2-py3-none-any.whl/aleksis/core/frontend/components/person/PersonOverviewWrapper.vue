<template>
  <component :is="currentComponent" v-bind="componentProps" />
</template>

<script>
import PersonForm from "./PersonForm.vue";
import PersonOverview from "./PersonOverview.vue";
import ChangePassword from "../account/ChangePassword.vue";
import ErrorPage from "../app/ErrorPage.vue";
import permissionsMixin from "../../mixins/permissions";

export default {
  mixins: [permissionsMixin],
  computed: {
    action() {
      const action = this.$route.query._ui_action;

      if (action === "edit") {
        return action;
      }

      if (action === "change_password") {
        if (this.id === "me" || this.id === this.$root.whoAmI.person.id) {
          // Change password for the current user
          // Only allow if preference is set
          if (this.checkPermission("core.change_password_rule")) {
            return action;
          }

          return "403";
        }

        // Otherwise check if the user has permission to change the password
        if (
          this.checkObjectPermission(
            "core.change_user_password_rule",
            this.id,
            "person",
            "core",
          )
        ) {
          return "change_foreign_password";
        }

        return "403";
      }

      return PersonOverview;
    },
    currentComponent() {
      return (
        {
          edit: PersonForm,
          change_password: ChangePassword,
          change_foreign_password: ChangePassword,
          403: ErrorPage,
        }[this.action] || PersonOverview
      );
    },
    componentProps() {
      return (
        {
          edit: {
            fallbackUrl: { name: "core.personById", params: { id: this.id } },
            isCreate: false,
            id: this.id,
          },
          change_password: {
            successUrl: { name: "dashboard" },
          },
          change_foreign_password: {
            successUrl: { name: "core.personById", params: { id: this.id } },
            personId: this.id,
          },
          403: {
            shortErrorMessageKey: "base.no_permission_message_short",
            longErrorMessageKey: "base.no_permission_message_long",
            redirectButtonTextKey: "base.no_permission_redirect_text",
            redirectRouteName: "core.account.login",
            redirectButtonIcon: "mdi-login-variant",
            mascotType: "forbidden",
          },
        }[this.action] || {
          id: this.id,
        }
      );
    },
  },
  props: {
    id: {
      type: String,
      required: false,
      default: null,
    },
  },
  mounted() {
    this.addPermissions(["core.change_password_rule"]);
    this.addObjectPermission(
      "core.change_user_password_rule",
      this.id,
      "person",
      "core",
    );
  },
};
</script>
