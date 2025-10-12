<script setup>
import CRUDProvider from "../generic/crud/CRUDProvider.vue";

// TODO: Generate usefull defaults for start and end date(time). We have this often -> make it generally usefull.
// defaultItem: {
//   datetimeStart: DateTime.now()
//     .startOf("minute")
//     .toISO({ suppressSeconds: true }),
//   datetimeEnd: DateTime.now()
//     .startOf("minute")
//     .plus({ hours: 1 })
//     .toISO({ suppressSeconds: true }),
//   recipientGroups: [],
//   recipientPersons: [],
//   title: "",
//   description: "",
// },
</script>

<template>
  <div>
    <message-box type="info">
      {{ $t("announcement.explanation") }}
    </message-box>
    <c-r-u-d-provider
      :object-schema="{ type: 'AnnouncementType' }"
      :default-item="defaultItem"
      item-attribute="title"
      disable-inline-edit
    />
  </div>
</template>
