import { defineStore } from "@/pinia";
import { ref } from "vue";

export const usePermissionStore = defineStore("permission", () => {
  // The results of global permission checks
  const permissions = ref([]);
  // Names of permissions that are requested
  const permissionNames = ref([]);
  // The results of object permission checks
  const objectPermissions = ref([]);
  // Descriptions of requested object permissions
  const objectPermissionItems = ref([]);

  function isPermissionFetched(permissionName) {
    return permissions.value.some((p) => p.name === permissionName);
  }

  function checkPermission(permissionName) {
    return (
      this.isPermissionFetched(permissionName) &&
      permissions.value.find((p) => p.name === permissionName).result
    );
  }

  function addPermissions(newPermissionNames) {
    permissionNames.value = [
      ...new Set([...permissionNames.value, ...newPermissionNames]),
    ];
  }

  function checkObjectPermission(name, objId, objType, appLabel) {
    if (objectPermissions.value) {
      const permissionItem = objectPermissions.value.find(
        (p) =>
          p.name === name &&
          p.objId === objId &&
          p.objType === objType &&
          p.appLabel === appLabel,
      );
      if (permissionItem) {
        return permissionItem.result;
      }
    }
    return false;
  }

  function addObjectPermission(name, objId, objType, appLabel) {
    const newPermissionItem = {
      name,
      objId,
      objType,
      appLabel,
    };
    const mergedObjectPermissionArray = Array.from(
      new Set(
        [...objectPermissionItems.value, newPermissionItem].map((o) =>
          JSON.stringify(o),
        ),
      ),
    );

    objectPermissionItems.value = mergedObjectPermissionArray.map((str) =>
      JSON.parse(str),
    );
  }

  return {
    setPermissionResults: (newPermissions) => {
      permissions.value = newPermissions;
    },
    setObjectPermissionResults: (newObjectPermissions) => {
      objectPermissions.value = newObjectPermissions;
    },
    permissionNames,
    objectPermissionItems,
    isPermissionFetched,
    addPermissions,
    checkPermission,
    addObjectPermission,
    checkObjectPermission,
  };
});
