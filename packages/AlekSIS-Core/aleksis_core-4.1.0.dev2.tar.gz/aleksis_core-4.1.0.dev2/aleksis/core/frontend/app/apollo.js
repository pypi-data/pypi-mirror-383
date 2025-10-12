/*
 * Configuration for Apollo provider, client, and caches.
 */

import { ApolloClient, InMemoryCache } from "@apollo/client/core";
import { onError } from "@/@apollo/client/link/error";

import { persistCache, LocalStorageWrapper } from "@/apollo3-cache-persist";
import createUploadLink from "@/apollo-upload-client/createUploadLink.mjs";
import { createApolloProvider } from "@vue/apollo-option";
import { logErrorMessages } from "@vue/apollo-util";
export { DefaultApolloClient } from "@vue/apollo-composable";

import { possibleTypes } from "aleksisApolloOptions";

import { useAppStore } from "../stores/appStore";
import { useError } from "../composables/app/error";

import errorCodes from "../errorCodes";
import * as Sentry from "@sentry/vue";

// Cache for GraphQL query results in memory and persistent across sessions
const cache = new InMemoryCache({
  possibleTypes,
  typePolicies: {
    DashboardType: {
      merge: true,
    },
  },
});
await persistCache({
  cache: cache,
  storage: new LocalStorageWrapper(window.localStorage),
});

/**
 * Construct the GraphQL endpoint URI.
 *
 * @returns The URI of the GraphQL endpoint on the AlekSIS server
 */
function getGraphqlURL() {
  const settings = JSON.parse(
    document.getElementById("frontend_settings").textContent,
  );
  const base = settings.urls.base || window.location.origin;
  return new URL(settings.urls.graphql, base);
}

// Handle errors
const errorLink = onError((error) => {
  const { graphQLErrors, networkError } = error;

  if (import.meta.env.DEV) {
    logErrorMessages(error);
  }

  const appStore = useAppStore();

  if (networkError) {
    // Set app offline globally on network errors
    //  This will cause the offline logic to kick in, starting a ping check or
    //  similar recovery strategies depending on the app/navigator state
    console.error("Network error:", networkError.statusCode, networkError);
    if (
      (!networkError.statusCode || networkError.statusCode >= 500) &&
      (!graphQLErrors || graphQLErrors.length === 0)
    ) {
      console.error(
        "Network error during GraphQL query, setting offline state",
      );
      appStore.offline = true;
    }

    appStore.maintenance = networkError.statusCode === 503;
  }
  if (graphQLErrors && graphQLErrors.length > 0) {
    for (let err of graphQLErrors) {
      if (
        JSON.parse(document.getElementById("frontend_settings").textContent)
          .sentry &&
        JSON.parse(document.getElementById("frontend_settings").textContent)
          .sentry.enabled
      ) {
        Sentry.captureException(err);
      }
      console.error(
        "GraphQL error in query",
        err.path.join("."),
        ":",
        err.message,
      );
    }
    // Add a snackbar on all errors returned by the GraphQL endpoint
    //  If App is offline, don't add snackbar since only the ping query is active
    if (!appStore.offline) {
      useError("graphql.snackbar_error_message", errorCodes.graphQlErrorQuery);
    }
  }
});

const uploadLink = createUploadLink({
  uri: getGraphqlURL(),
});

/** Upstream Apollo GraphQL client */
export const apolloClient = new ApolloClient({
  cache,
  link: errorLink.concat(uploadLink),
  addTypename: true,
});

export const apolloOpts = {
  defaultClient: apolloClient,
  defaultOptions: {
    $query: {
      skip: function (vm, queryKey) {
        const appStore = useAppStore();

        if (queryKey in vm.$apollo.queries) {
          // We only want to run this query when background activity is on and we are not reported offline
          return !!(
            vm.$apollo.queries[queryKey].options.pollInterval &&
            (!appStore.backgroundActive || appStore.offline)
          );
        }
        return false;
      },
      fetchPolicy: "cache-and-network",
    },
  },
};

export default createApolloProvider(apolloOpts);
