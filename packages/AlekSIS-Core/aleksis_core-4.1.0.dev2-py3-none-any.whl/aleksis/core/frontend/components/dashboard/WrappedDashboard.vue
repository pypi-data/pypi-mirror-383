<script>
import UiActionWrapper from "../generic/routing/UiActionWrapper.vue";
import Dashboard from "./Dashboard.vue";
import ManageDashboard from "./management/ManageDashboard.vue";

export default {
  name: "WrappedDashboard",
  extends: UiActionWrapper,
  data() {
    return {
      components: {
        default: Dashboard,
        edit: ManageDashboard,
      },
    };
  },
};
</script>
