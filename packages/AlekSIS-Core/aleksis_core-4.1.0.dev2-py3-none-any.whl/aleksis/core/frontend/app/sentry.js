import * as Sentry from "@sentry/vue";

export function useSentry(app, router) {
  let frontendSettings = JSON.parse(
    document.getElementById("frontend_settings").textContent,
  );
  let sentryConfig = frontendSettings.sentry;

  if (sentryConfig && sentryConfig.enabled) {
    Sentry.init({
      app,
      dsn: sentryConfig.dsn,
      environment: sentryConfig.environment,
      tracesSampleRate: sentryConfig.traces_sample_rate,
      logError: true,
      trackComponents: true,
      integrations: [
        new Sentry.BrowserTracing({
          routingInstrumentation: Sentry.vueRouterInstrumentation(router),
        }),
        new Sentry.Replay(),
      ],
      tracePropagationTargets: [frontendSettings.urls.base],
    });
  }
}

export default useSentry;
