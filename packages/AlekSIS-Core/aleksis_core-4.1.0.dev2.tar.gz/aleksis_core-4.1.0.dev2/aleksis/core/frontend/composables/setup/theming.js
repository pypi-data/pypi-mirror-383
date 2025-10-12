import {
  argbFromHex,
  DynamicScheme,
  Hct,
  hexFromArgb,
  TonalPalette,
} from "@material/material-color-utilities";
import * as math from "@/@material/material-color-utilities/utils/math_utils";
import { watchEffect } from "vue";

export function useTheming(theme, primary, secondary, design) {
  const primarySourceColorHct = Hct.fromInt(argbFromHex(primary));

  const schemeLight = new DynamicScheme({
    sourceColorHct: primarySourceColorHct,
    variant: 4,
    contrastLevel: 1,
    isDark: false,
    primaryPalette: TonalPalette.fromInt(argbFromHex(primary)),
    secondaryPalette: TonalPalette.fromInt(argbFromHex(secondary)),
    tertiaryPalette: TonalPalette.fromHueAndChroma(
      math.sanitizeDegreesDouble(primarySourceColorHct.hue + 60.0),
      24.0,
    ),
    neutralPalette: TonalPalette.fromHueAndChroma(
      primarySourceColorHct.hue,
      10.0,
    ),
    neutralVariantPalette: TonalPalette.fromHueAndChroma(
      primarySourceColorHct.hue,
      16.0,
    ),
  });

  const schemeDark = new DynamicScheme({
    sourceColorHct: primarySourceColorHct,
    variant: 4,
    contrastLevel: 1,
    isDark: true,
    primaryPalette: TonalPalette.fromInt(argbFromHex(primary)),
    secondaryPalette: TonalPalette.fromInt(argbFromHex(secondary)),
    tertiaryPalette: TonalPalette.fromHueAndChroma(
      math.sanitizeDegreesDouble(primarySourceColorHct.hue + 60.0),
      24.0,
    ),
    neutralPalette: TonalPalette.fromHueAndChroma(
      primarySourceColorHct.hue,
      10.0,
    ),
    neutralVariantPalette: TonalPalette.fromHueAndChroma(
      primarySourceColorHct.hue,
      16.0,
    ),
  });

  theme.themes.value.light.colors = {
    ...theme.themes.value.light.colors,

    primary,
    "on-primary": hexFromArgb(schemeLight.onPrimary),
    secondary,
    "on-secondary": hexFromArgb(schemeLight.onSecondary),
    tertiary: hexFromArgb(schemeLight.tertiary),
    "on-tertiary": hexFromArgb(schemeLight.onTertiary),

    background: hexFromArgb(schemeLight.background),
    surface: hexFromArgb(schemeLight.surface),
    "surface-dim": hexFromArgb(schemeLight.surfaceDim),
    "surface-variant": hexFromArgb(schemeLight.surfaceDim),
    "surface-bright": hexFromArgb(schemeLight.surfaceBright),
    "surface-light": hexFromArgb(schemeLight.surfaceBright),
    "on-surface": hexFromArgb(schemeLight.onSurface),

    outline: hexFromArgb(schemeLight.outline),
    "outline-variant": hexFromArgb(schemeLight.outlineVariant),

    error: hexFromArgb(schemeLight.error),
    "on-error": hexFromArgb(schemeLight.onError),
  };

  theme.themes.value.dark.colors = {
    ...theme.themes.value.dark.colors,

    primary: hexFromArgb(schemeDark.primary),
    "on-primary": hexFromArgb(schemeDark.onPrimary),
    secondary: hexFromArgb(schemeDark.secondary),
    "on-secondary": hexFromArgb(schemeDark.onSecondary),
    accent: hexFromArgb(schemeDark.tertiary),
    "on-accent": hexFromArgb(schemeDark.onTertiary),
    tertiary: hexFromArgb(schemeDark.tertiary),
    "on-tertiary": hexFromArgb(schemeDark.onTertiary),

    background: hexFromArgb(schemeDark.background),
    surface: hexFromArgb(schemeDark.surface),
    "surface-dim": hexFromArgb(schemeDark.surfaceDim),
    "surface-variant": hexFromArgb(schemeDark.surfaceDim),
    "surface-bright": hexFromArgb(schemeDark.surfaceBright),
    "surface-light": hexFromArgb(schemeDark.surfaceBright),
    "on-surface": hexFromArgb(schemeDark.onSurface),

    outline: hexFromArgb(schemeDark.outline),
    "outline-variant": hexFromArgb(schemeDark.outlineVariant),

    error: hexFromArgb(schemeDark.error),
    "on-error": hexFromArgb(schemeDark.onError),
  };

  watchEffect(() => {
    if (design !== "system") {
      // System theme cannot be set this way, only via defaultTheme in the vuetify constructor
      theme.change(design);
    }
  });
}
