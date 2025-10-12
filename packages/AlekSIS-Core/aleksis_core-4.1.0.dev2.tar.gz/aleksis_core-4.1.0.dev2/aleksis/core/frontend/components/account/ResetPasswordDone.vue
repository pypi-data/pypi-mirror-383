<script>
import AdminEmailList from "./AdminEmailList.vue";

export default {
  name: "ResetPasswordDone",
  components: { AdminEmailList },
};
</script>

<template>
  <small-container>
    <v-card>
      <v-card-title>
        <v-avatar>
          <v-icon color="success">$success</v-icon>
        </v-avatar>
        {{ $t("accounts.reset_password.done.title") }}
      </v-card-title>
      <v-card-text>
        <p>
          {{ $t("accounts.reset_password.done.message") }}
        </p>

        <admin-email-list />
      </v-card-text>
    </v-card>
  </small-container>
</template>
