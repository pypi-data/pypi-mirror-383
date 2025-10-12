import { objectSchemas, objectLayouts } from "objectSchemas";
import { ref } from "vue";
import i18n from "../../app/i18n";

import ObjectField from "../../components/generic/crud/ObjectField.vue";

// Layout components
import GridLayout from "../../components/generic/crud/form/GridLayout.vue";

// Encapsulate objectSchemas & objectLayouts in getter fns
export function getDefaultObjectSchema(type) {
  return objectSchemas.find((objectSchema) => type === objectSchema.type);
}

export function getDefaultObjectLayout(type) {
  return objectLayouts.find((objectLayout) => type === objectLayout.type);
}

/// objectSchema

export function convertCamelToSnake(str) {
  return str.replace(/([a-zA-Z])(?=[A-Z])/g, "$1_").toLowerCase();
}

function generateAdditionalObjectSchemaProps(objectSchema, field, schema) {
  const app = objectSchema.app === "core" ? "" : objectSchema.app + ".";
  return {
    label: objectSchema.model
      ? i18n.global.t(
          `${app}${convertCamelToSnake(objectSchema.model)}.${convertCamelToSnake(field)}`,
        )
      : "",
    // TODO: Add more rules derived from models (needs mechanism to get at models first)
    rules: [
      ...(schema.required && schema.type !== "Boolean"
        ? [(value) => !!value || i18n.global.t("forms.errors.required")]
        : []),
      ...(schema.required && schema.type === "Boolean"
        ? [
            (value) =>
              (value !== undefined && value !== null) ||
              i18n.global.t("forms.errors.required"),
          ]
        : []),
      ...(schema.rules || []),
    ],
  };
}

export function fillObjectSchemaWithDefaults(objectSchema, depth) {
  if (depth === undefined) {
    return fillObjectSchemaWithDefaults(objectSchema, 0);
  } else if (depth === 2) {
    return objectSchema;
  } else {
    // TODO: Can this keep reactivity?
    // objectSchema is required to have type at least!
    const defaultObjectSchema = getDefaultObjectSchema(objectSchema.type);
    const fullObjectSchema = {
      ...defaultObjectSchema,
      ...objectSchema,
    };
    if (fullObjectSchema.items) {
      fullObjectSchema.items = fillObjectSchemaWithDefaults(
        fullObjectSchema.items,
        depth,
      );
    }
    if (fullObjectSchema.properties) {
      // Recursivly merge the properties
      fullObjectSchema.properties = Object.fromEntries(
        Object.entries(defaultObjectSchema.properties).map(
          ([field, schema]) => {
            const combinedSchema = {
              // Add property from default after expanding it
              ...fillObjectSchemaWithDefaults(schema, depth + 1),
              // Add property from objectSchema
              ...objectSchema?.properties?.[field],
            };
            const fullSchema = {
              ...combinedSchema,
              ...generateAdditionalObjectSchemaProps(
                defaultObjectSchema,
                field,
                combinedSchema,
              ),
            };
            return [field, fullSchema];
          },
        ),
      );
    }
    return fullObjectSchema;
  }
}

export function generateField(schema, slot) {
  const component = schema.editComponent
    ? schema.editComponent
    : schema.type.endsWith("Type")
      ? ObjectField
      : undefined;
  return {
    slot: slot,
    component,
    props: {
      ...schema,
      ...(schema?.hint ? { hint: i18n.global.t(schema.hint) } : {}),
    },
  };
}

export function generateFields(objectSchema, slots = {}) {
  // compile and return fields indexed by field name
  // TODO: Danger! Should work BUT js objects have no garanteed order => might need to use another notation
  //       But this one (with properties object) is json schema!
  //       Also I am doing fields the same now
  const properties = objectSchema.editFields
    ? objectSchema.editFields.map((field) => [
        field,
        objectSchema.properties[field],
      ])
    : Object.entries(objectSchema.properties);

  return Object.fromEntries(
    properties
      .map(([field, schema]) => {
        if (schema.hideEdit) {
          return false;
        } else {
          return [field, generateField(schema, slots[field + ".field"])];
        }
      })
      .filter((i) => i),
  );
}

export function instrumentFields(
  fields,
  editItem = {},
  onItemUpdate = (x) => x,
) {
  // Intstrument fields to show  and update editItem.
  // Return a patch of the inputs.
  // Call an optional onItemUpdate callback with each update.
  const item = {};
  const patch = ref({});
  return {
    patch: patch,
    fields: Object.fromEntries(
      Object.entries(fields).map(([field, { props, ...rest }]) => {
        item[field] = ref(editItem[field]);
        function updateValue(value) {
          item[field].value = value;
          onItemUpdate(item);
          patch.value[field] = item[field];
        }

        return [
          field,
          {
            ...rest,
            props: {
              ...props,
              item: item,
              "onUpdate:modelValue": updateValue,
              modelValue: item[field],
            },
          },
        ];
      }),
    ),
  };
}

/// objectLayout

export function fillObjectLayoutWithDefaults(objectLayout) {
  // TODO: How are objectLayouts indexed? How can they be found?
  // const defaultObjectLayout =
  // TODO implement actual filling from defaultObjectLayout
  return objectLayout;
}

export function gridLayoutObjectSchema(objectSchema, fields) {
  const fieldsWithCols = Object.fromEntries(
    Object.entries(fields).map(([name, field]) => [
      name,
      { cols: objectSchema.properties[name].cols || 6, field: field },
    ]),
  );
  return { component: GridLayout, props: { fields: fieldsWithCols } };
}

export function layoutObjectSchema(objectSchema, objectLayout = {}, fields) {
  // for now only default grid layout inspired by old ObjectForm
  // think about how to integrate this default with objectLayout
  // = how can empty layout be grid?

  // return one component and its props ready for render via template
  return gridLayoutObjectSchema(objectSchema, fields);
}

export function useObjectForm(
  objectSchema,
  objectLayout,
  editItem,
  slots,
  onItemUpdate,
) {
  const fullObjectSchema = fillObjectSchemaWithDefaults(objectSchema);
  const { fields, patch } = instrumentFields(
    generateFields(fullObjectSchema, slots),
    editItem,
    onItemUpdate,
  );
  return {
    form: layoutObjectSchema(
      fullObjectSchema,
      fillObjectLayoutWithDefaults(objectLayout),
      fields,
    ),
    patch: patch,
  };
}

// TODO: How does tableField integrate with CRUDIterator? Should it become viewFields?
export function transformObjectSchemaToTableHeaders(objectSchema) {
  const properties = objectSchema.tableFields
    ? objectSchema.tableFields.map((field) => [
        field,
        objectSchema.properties[field],
      ])
    : Object.entries(objectSchema.properties);

  return properties
    .map(([field, schema]) => ({
      // TODO: Actually add whole schema? Makes it possible to define in schema.
      ...schema,
      key: field,
      title: schema.label,
    }))
    .filter((header) => !header.hideTable);
}
