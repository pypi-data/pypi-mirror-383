/**
 * Vue mixin containing permission checking code.
 */
import { usePermissionStore } from "../stores/permissionStore";

const permissionsMixin = {
  computed: {
    permissionStore() {
      return usePermissionStore();
    },
  },
  methods: {
    isPermissionFetched(permissionName) {
      console.warn(
        "`isPermissionFetched` is deprecated, use `permissionStore.isPermissionFetched` instead.",
      );
      return this.permissionStore.isPermissionFetched(permissionName);
    },
    checkPermission(permissionName) {
      console.warn(
        this.$options.name,
        "`checkPermission` is deprecated, use `permissionStore.checkPermission` instead.",
      );
      return this.permissionStore.checkPermission(permissionName);
    },
    addPermissions(newPermissionNames) {
      console.warn(
        "`addPermissions` is deprecated, use `permissionStore.addPermissions` instead.",
      );
      return this.permissionStore.addPermissions(newPermissionNames);
    },
    checkObjectPermission(name, objId, objType, appLabel) {
      console.warn(
        "`checkObjectPermission` is deprecated, use `permissionStore.checkObjectPermission` instead.",
      );
      return this.permissionStore.checkObjectPermission(
        name,
        objId,
        objType,
        appLabel,
      );
    },
    addObjectPermission(name, objId, objType, appLabel) {
      console.warn(
        "`addObjectPermission` is deprecated, use `permissionStore.addObjectPermission` instead.",
      );
      return this.permissionStore.addObjectPermission(
        name,
        objId,
        objType,
        appLabel,
      );
    },
  },
};

export default permissionsMixin;
