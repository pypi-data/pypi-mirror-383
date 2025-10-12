import { didRecentlyAuthenticate } from "./twoFactor.graphql";

export default {
  apollo: {
    didRecentlyAuthenticate: {
      query: didRecentlyAuthenticate,
      fetchPolicy: "network-only",
      result({ data }) {
        if (!data.didRecentlyAuthenticate.didRecentlyAuthenticate) {
          this.$router.push({
            name: "core.accounts.reauthenticate",
            query: { next: this.$route.fullPath },
          });
        } else {
          this.dialogValid = true;
        }
      },
      skip() {
        return !this.dialog;
      },
    },
  },
  emits: ["save"],
  data() {
    return {
      dialog: false,
      dialogValid: false,
      uiAction: null,
    };
  },
  methods: {
    openDialog() {
      this.dialog = this.$route.query._ui_action === this.uiAction;
    },
  },
  mounted() {
    this.openDialog();
  },
  watch: {
    $route() {
      this.openDialog();
    },
    dialog(val) {
      if (!val) {
        this.dialogValid = false;
        this.$router.push({ name: "core.twoFactor" });
      }
    },
  },
};
