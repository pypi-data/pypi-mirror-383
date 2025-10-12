<!-- Information card for one AlekSIS app -->

<template>
  <v-col cols="12" md="6" lg="6" xl="4" class="d-flex align-stretch">
    <v-card :id="app.name" class="d-flex flex-column flex-grow-1">
      <v-card-title>
        {{ app.verboseName }}
      </v-card-title>

      <v-card-subtitle class="text-body-1 text-black">
        {{ app.version }}
      </v-card-subtitle>

      <v-card-text>
        <v-row v-if="app.licence" class="mb-2">
          <v-col cols="6">
            {{ $t("about.licenced_under") }} <br />
            <strong class="text-body-1 text-black">
              {{ app.licence.verboseName }}
            </strong>
          </v-col>
          <v-col cols="6">
            {{ $t("about.licence_type") }} <br />
            <v-chip
              v-if="app.licence.flags.isFsfLibre"
              color="green"
              size="small"
            >
              {{ $t("about.free_software") }}
            </v-chip>
            <v-chip
              v-else-if="app.licence.flags.isOsiApproved"
              color="green"
              size="small"
            >
              {{ $t("about.open_source") }}
            </v-chip>
            <v-chip v-else color="orange" size="small">
              {{ $t("about.proprietary") }}
            </v-chip>
          </v-col>

          <v-col cols="12" v-if="app.licence.licences.length !== 0">
            {{ $t("about.licence_consists_of") }}
            <div
              v-for="licence in app.licence.licences"
              class="mb-2"
              :key="licence.name"
            >
              <v-chip
                v-if="licence.isOsiApproved || licence.isFsfLibre"
                color="green"
                variant="outlined"
                size="small"
                :href="licence.url"
              >
                {{ licence.name }}
              </v-chip>
              <v-chip
                v-else
                color="orange"
                variant="outlined"
                :href="licence.url"
              >
                {{ licence.name }}
              </v-chip>
            </div>
          </v-col>
        </v-row>
      </v-card-text>

      <v-spacer />

      <v-card-actions v-if="app.urls.length !== 0">
        <v-btn variant="text" color="primary" @click="reveal = true">
          {{ $t("about.show_copyright") }}
        </v-btn>
        <v-btn
          v-for="url in app.urls"
          color="primary"
          variant="text"
          :href="url.url"
          :key="url.url"
        >
          {{ url.name }}
        </v-btn>
      </v-card-actions>

      <v-expand-transition>
        <v-card v-if="reveal" class="v-card--reveal d-flex flex-column">
          <v-card-text class="pb-0">
            <v-row>
              <v-col cols="12" v-if="app.copyrights.length !== 0">
                <span v-for="(copyright, index) in app.copyrights" :key="index">
                  {{ "Copyright ©" + copyright.years }}
                  <a :href="'mailto:' + copyright.email">
                    {{ copyright.name }}
                  </a>
                  <br />
                </span>
              </v-col>
            </v-row>
          </v-card-text>
          <v-spacer></v-spacer>
          <v-card-actions class="pt-0">
            <v-btn variant="text" color="primary" @click="reveal = false">{{
              $t("actions.close")
            }}</v-btn>
          </v-card-actions>
        </v-card>
      </v-expand-transition>
    </v-card>
  </v-col>
</template>

<script>
export default {
  name: "InstalledAppCard",
  data: () => ({
    reveal: false,
  }),
  props: {
    app: {
      type: Object,
      required: true,
    },
  },
};
</script>
