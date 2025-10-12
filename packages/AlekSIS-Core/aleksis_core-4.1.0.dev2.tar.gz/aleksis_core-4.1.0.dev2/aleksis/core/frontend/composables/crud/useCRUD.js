// useCRUD combines useQuery, useCreateMutation, usePatchMutation and useDeleteMutation into one function

import { computed, toRef, toRaw } from "vue";
import { argToRef } from "../utils.js";
import { useQuery } from "../app/apollo";
import { useMutation } from "@vue/apollo-composable";
import { getKeysRecursive, setKeysRecursive } from "../../util/lookups";

/// Cache update
// TODO: We do this by convention. Keep it? Make it configurable?
const ITEMS = "items";

// mutation mutation.document.value.definitions[0].name.value,
function updateCache(
  mutationVariables,
  query,
  queryVariables,
  mutation,
  updateFunction,
  dataKey = { value: ITEMS },
  mutationKey = { value: ITEMS },
) {
  return (cache, { data }) => {
    const fullQuery = {
      // Unwrap query.value as it may be a Proxy object
      query: toRaw(query.value),
    };
    if (queryVariables.value) {
      fullQuery.variables = queryVariables.value;
    }

    const cached = cache.readQuery(fullQuery);

    const queryData = JSON.parse(JSON.stringify(cached));

    setKeysRecursive(
      dataKey.value,
      queryData,
      updateFunction(
        getKeysRecursive(dataKey.value, cached),
        getKeysRecursive(
          mutationKey.value,
          data[mutation.value.definitions[0].name.value],
        ),
        mutationVariables,
      ),
    );

    cache.writeQuery({
      ...fullQuery,
      data: queryData,
    });
  };
}

function addUpdateToMutate(mutate, ...updateCacheArgs) {
  return (variables, overrideOptions) => {
    mutate(variables, {
      update: updateCache(variables, ...updateCacheArgs),
      ...overrideOptions,
    });
  };
}

function updateAfterCreate(cached, incoming) {
  return [...incoming, ...cached];
}

function updateAfterPatch(cached, incoming) {
  // Could be a bit more efficient by searching for incoming directly.
  // But this solves deep copy needed for the immutable store
  // TODO: Use itemId/idKey option instead of hardcoded .id?
  return cached.map(
    (oldVal) => incoming.find((newVal) => oldVal.id === newVal.id) || oldVal,
  );
}

function updateAfterDelete(cached, incoming, variables) {
  // TODO: Use idKey option instead of hardcoded itemId?
  // incoming is either an array of ids or null, in that case use query variables
  const ids = incoming || variables.ids;
  return [...cached.filter(({ id }) => !ids.includes(id))];
}

/// Read and Write over wire
export function useReadItem(objectSchema) {
  const readItem = computed(() =>
    Object.fromEntries(
      Object.entries(objectSchema.value.properties ?? {})
        .map(([field, schema]) => [field, schema.read])
        .filter(([field, read]) => read),
    ),
  );

  if (Object.keys(readItem.value).length > 0) {
    // Does a copy since item properties are readonly.
    return (item) =>
      Object.fromEntries(
        Object.entries(item).map(([field, value]) => [
          field,
          readItem.value[field] ? readItem.value[field](value) : value,
        ]),
      );
  } else {
    // But be the symmetrical solution but bad for optimizing
    //return (item) => item;
    return false;
  }
}

export function useWriteItem(objectSchema) {
  const writeItem = computed(() =>
    Object.fromEntries(
      Object.entries(objectSchema.value.properties ?? {})
        .map(([field, schema]) => [field, schema.write])
        .filter(([field, write]) => write),
    ),
  );
  if (Object.keys(writeItem.value).length > 0) {
    return (item) =>
      Object.fromEntries(
        Object.entries(item).map(([field, value]) => [
          field,
          value !== undefined && writeItem.value[field]
            ? writeItem.value[field](value)
            : value,
        ]),
      );
  } else {
    return false;
  }
}

function makeKeyPrefixer(prefix) {
  return ([key, val]) => [
    prefix + key.charAt(0).toUpperCase() + key.slice(1),
    val,
  ];
}

function prefixKeys(prefix, obj) {
  return Object.fromEntries(Object.entries(obj).map(makeKeyPrefixer(prefix)));
}

function serialize(mutate, writeItem) {
  return ({ input, ...restVars }, ...restArgs) =>
    mutate({ ...restVars, input: input.map(writeItem) }, ...restArgs);
}

function getDataKey(mutationOptions, defaultKeyRef) {
  if (mutationOptions.value && mutationOptions.value.dataKey) {
    return toRef(mutationOptions.value.dataKey);
  }

  return defaultKeyRef;
}

/**
 * useCRUD combines query and mutation functions (Query, Create, Patch, Delete) for GraphQL objects.
 *
 * It wraps the apollo.js primitives, providing them with cache update
 * and making them fully reactive.
 *
 * Each value of its configuration object can either be a ref, a plain
 * value or a function, which will be turned into a computed.
 *
 * Only the CRUD operations supported by the configuration object will
 * be setup and are present in the resulting CRUD interface.
 *
 * The object schema's read and write props can be used for
 * deserializing and serializing the object.
 *
 * @param {Object} args - Configuration object
 * @param [args.query] - GraphQL query (ref or object)
 * @param [args.queryVariables] - Variables for the query (ref or object)
 * @param [args.dataKey] - Key to access the object list within a query result. Defaults to `items`. Mutations use specific keys set in the mutationOptions.
 * @param [args.objectSchema] - Object Schema declaratively describing the graqhQL object
 * @param [args.createMutation] - GraphQL mutation for creation
 * @param [args.createOptions] - Options for the create mutation
 * @param [args.patchMutation] - GraphQL mutation for patching
 * @param [args.patchOptions] - Options for the patch mutation
 * @param [args.deleteMutation] - GraphQL mutation for deletion
 * @param [args.deleteOptions] - Options for the delete mutation
 * @returns {Record<string, any>} CRUD interface with query, create, patch, and delete methods, exposing all the apollo.js results
 *
 * @example
 * const crud = useCRUD({
 *   query: MY_QUERY,
 *   createMutation: MY_CREATE_MUTATION,
 *   patchMutation: MY_PATCH_MUTATION,
 *   deleteMutation: MY_DELETE_MUTATION,
 *   objectSchema: mySchema,
 * });
 * const result = crud.queryItems;
 * crud.create({ input: [...] });
 * crud.patch({ input: [...] });
 * crud.delete({ ids: [...] });
 */
export function useCRUD(args) {
  const useCRUDInterface = {
    query: undefined,
    queryVariables: {},
    dataKey: ITEMS,
    objectSchema: null,
    createMutation: undefined,
    createOptions: undefined,
    patchMutation: undefined,
    patchOptions: undefined,
    deleteMutation: undefined,
    deleteOptions: undefined,
  };

  const {
    query,
    queryVariables,
    dataKey,
    objectSchema,
    createMutation,
    createOptions,
    patchMutation,
    patchOptions,
    deleteMutation,
    deleteOptions,
  } = Object.fromEntries(
    Object.entries(useCRUDInterface).map(([key, val]) => [
      key,
      argToRef(args[key] || val),
    ]),
  );

  let crud = {};

  if (query.value) {
    const queryObject = useQuery(query, queryVariables);
    const readItem = objectSchema.value ? useReadItem(objectSchema) : false;
    crud = {
      ...crud,
      ...prefixKeys("query", queryObject),
      queryItems: computed(() => {
        const items = queryObject.result.value
          ? getKeysRecursive(dataKey.value, queryObject.result.value)
          : [];
        return items && readItem ? items.map(readItem) : items;
      }),
    };
  }

  if (createMutation.value || patchMutation.value) {
    const writeItem = objectSchema.value ? useWriteItem(objectSchema) : false;

    if (createMutation.value) {
      const createObject = useMutation(
        createMutation.value,
        createOptions.value,
      );
      const createFunction = writeItem
        ? serialize(createObject.mutate, writeItem)
        : createObject.mutate;
      delete createObject.mutate;
      crud = {
        ...crud,
        create: addUpdateToMutate(
          createFunction,
          query,
          queryVariables,
          createMutation,
          updateAfterCreate,
          dataKey,
          getDataKey(createOptions, dataKey),
        ),
        ...prefixKeys("create", createObject),
      };
    }

    if (patchMutation.value) {
      const patchObject = useMutation(patchMutation.value, patchOptions.value);
      const patchFunction = writeItem
        ? serialize(patchObject.mutate, writeItem)
        : patchObject.mutate;
      delete patchObject.mutate;
      crud = {
        ...crud,
        patch: addUpdateToMutate(
          patchFunction,
          query,
          queryVariables,
          patchMutation,
          updateAfterPatch,
          dataKey,
          getDataKey(patchOptions, dataKey),
        ),
        ...prefixKeys("patch", patchObject),
      };
    }
  }

  if (deleteMutation.value) {
    const deleteObject = useMutation(deleteMutation.value, deleteOptions.value);
    const deleteFunction = deleteObject.mutate;
    delete deleteObject.mutate;
    crud = {
      ...crud,
      delete: addUpdateToMutate(
        deleteFunction,
        query,
        queryVariables,
        deleteMutation,
        updateAfterDelete,
        dataKey,
        getDataKey(deleteOptions, { value: "deletedIds" }),
      ),
      ...prefixKeys("delete", deleteObject),
    };
  }

  return crud;
}

export const CRUDProps = {
  // UPDATE NOTICE: Name change from gqlXXXX to just XXXX for compliance with useCRUD (and apollo naming)
  // But in AlekSIS all could be renamed back to gqlXXXX
  /**
   * The graphQL query
   */
  query: {
    type: Object,
    required: false,
    default: undefined,
  },
  /**
   * Variables for the graphQL query
   *
   * UPDATE NOTICE: Name change from gqlAdditionalQueryArgs
   * Testing for simplicity for now since this is not additional any more
   */
  queryVariables: {
    type: Object,
    required: false,
    default: () => ({}),
  },
  /**
   * Key of the desired data payload
   * Key can be a single key or nested keys seperated by a '.'
   */
  dataKey: {
    type: String,
    required: false,
    default: "items",
  },
  /**
   * The graphQL create mutation
   */
  createMutation: {
    type: Object,
    required: false,
    default: undefined,
  },
  /**
   * Options for the graphQL create mutation
   */
  createOptions: {
    type: Object,
    required: false,
    default: undefined,
  },
  /**
   * The graphQL patch mutation
   */
  patchMutation: {
    type: Object,
    required: false,
    default: undefined,
  },
  /**
   * Options for the graphQL patch mutation
   */
  patchOptions: {
    type: Object,
    required: false,
    default: undefined,
  },
  /**
   * The graphQL delete mutation
   */
  deleteMutation: {
    type: Object,
    required: false,
    default: undefined,
  },
  /**
   * Options for the graphQL delete mutation
   */
  deleteOptions: {
    type: Object,
    required: false,
    default: undefined,
  },
};
