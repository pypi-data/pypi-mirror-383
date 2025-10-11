export {bestColorContrast} from './bestColorContrast.js';

import {
  BOKEH_PALETTE_DATA,
  BOKEH_PALETTES,
  BOKEH_PALETTE_NAMES,
  BOKEH_DOCS_PALETTE_DATA,
  BOKEH_DOCS_PALETTES,
  BOKEH_CATEGORY_10,
  BOKEH_CATEGORY_20,
  BOKEH_CATEGORY_20_B,
  BOKEH_CATEGORY_20_C,
  BOKEH_COLORBLIND,
  BOKEH_ACCENT,
  BOKEH_DARK_2,
  BOKEH_PAIRED,
  BOKEH_PASTEL_1,
  BOKEH_PASTEL_2,
  BOKEH_SET_1,
  BOKEH_SET_2,
  BOKEH_SET_3,
  BOKEH_YELLOW_GREEN,
  BOKEH_YELLOW_GREEN_BLUE,
  BOKEH_GREEN_BLUE,
  BOKEH_BLUE_GREEN,
  BOKEH_PURPLE_BLUE_GREEN,
  BOKEH_PURPLE_BLUE,
  BOKEH_BLUE_PURPLE,
  BOKEH_RED_PURPLE,
  BOKEH_PURPLE_RED,
  BOKEH_ORANGE_RED,
  BOKEH_YELLOW_ORANGE_RED,
  BOKEH_YELLOW_ORANGE_BROWN,
  BOKEH_PURPLES,
  BOKEH_BLUES,
  BOKEH_GREENS,
  BOKEH_ORANGES,
  BOKEH_REDS,
  BOKEH_GREYS,
  BOKEH_PURPLE_ORANGE,
  BOKEH_BROWN_BLUE_GREEN,
  BOKEH_PURPLE_GREEN,
  BOKEH_PINK_YELLOW_GREEN,
  BOKEH_RED_BLUE,
  BOKEH_RED_GREY,
  BOKEH_RED_YELLOW_BLUE,
  BOKEH_SPECTRAL,
  BOKEH_RED_YELLOW_GREEN,
  BOKEH_INFERNO,
  BOKEH_MAGMA,
  BOKEH_PLASMA,
  BOKEH_VIRIDIS
} from '../../data/bokeh-palettes.js';

import {
  VEGA_PALETTE_DATA,
  VEGA_PALETTES,
  VEGA_PALETTE_NAMES,
  VEGA_DOCS_PALETTE_DATA,
  VEGA_DOCS_PALETTES,
  VEGA_CATEGORY_10,
  VEGA_CATEGORY_20,
  VEGA_CATEGORY_20_B,
  VEGA_CATEGORY_20_C,
  VEGA_TABLEAU_10,
  VEGA_TABLEAU_20,
  VEGA_ACCENT,
  VEGA_DARK_2,
  VEGA_PAIRED,
  VEGA_PASTEL_1,
  VEGA_PASTEL_2,
  VEGA_SET_1,
  VEGA_SET_2,
  VEGA_SET_3,
  VEGA_BLUES,
  VEGA_GREENS,
  VEGA_GREYS,
  VEGA_ORANGES,
  VEGA_PURPLES,
  VEGA_REDS,
  VEGA_BLUE_GREEN,
  VEGA_BLUE_PURPLE,
  VEGA_GREEN_BLUE,
  VEGA_ORANGE_RED,
  VEGA_PURPLE_BLUE,
  VEGA_PURPLE_BLUE_GREEN,
  VEGA_PURPLE_RED,
  VEGA_RED_PURPLE,
  VEGA_YELLOW_GREEN,
  VEGA_YELLOW_ORANGE_BROWN,
  VEGA_YELLOW_ORANGE_RED,
  VEGA_BLUE_ORANGE,
  VEGA_BROWN_BLUE_GREEN,
  VEGA_PURPLE_GREEN,
  VEGA_PURPLE_ORANGE,
  VEGA_RED_BLUE,
  VEGA_RED_GREY,
  VEGA_YELLOW_GREEN_BLUE,
  VEGA_RED_YELLOW_BLUE,
  VEGA_RED_YELLOW_GREEN,
  VEGA_PINK_YELLOW_GREEN,
  VEGA_SPECTRAL,
  VEGA_VIRIDIS,
  VEGA_MAGMA,
  VEGA_INFERNO,
  VEGA_PLASMA,
  VEGA_RAINBOW,
  VEGA_SINEBOW,
  VEGA_BROWNS,
  VEGA_TEAL_BLUES,
  VEGA_TEALS,
  VEGA_WARM_GREYS,
  VEGA_GOLD_GREEN,
  VEGA_GOLD_ORANGE,
  VEGA_GOLD_RED,
  VEGA_LIGHT_GREY_RED,
  VEGA_LIGHT_GREY_TEAL,
  VEGA_LIGHT_MULTI,
  VEGA_LIGHT_ORANGE,
  VEGA_LIGHT_TEAL_BLUE,
  VEGA_DARK_BLUE,
  VEGA_DARK_GOLD,
  VEGA_DARK_GREEN,
  VEGA_DARK_MULTI,
  VEGA_DARK_RED,
  VEGA_OBSERVABLE_10,
  VEGA_CIVIDIS,
  VEGA_TURBO
} from '../../data/vega-palettes.js';

export * from '../../data/vega-palettes.js';
export * from '../../data/bokeh-palettes.js';

export const BOKEH = 'bokeh';
export const VEGA = 'vega';

export const CATEGORICAL_PALETTE_VENDORS = [
  {[BOKEH]: BOKEH_ACCENT, [VEGA]: VEGA_ACCENT},
  {
    [BOKEH]: BOKEH_CATEGORY_10,

    [VEGA]: VEGA_CATEGORY_10
  },
  {
    [BOKEH]: BOKEH_CATEGORY_20,

    [VEGA]: VEGA_CATEGORY_20
  },
  {
    [BOKEH]: BOKEH_CATEGORY_20_B,

    [VEGA]: VEGA_CATEGORY_20_B
  },
  {
    [BOKEH]: BOKEH_CATEGORY_20_C,

    [VEGA]: VEGA_CATEGORY_20_C
  },
  {[BOKEH]: BOKEH_DARK_2, [VEGA]: VEGA_DARK_2},
  {[BOKEH]: BOKEH_PAIRED, [VEGA]: VEGA_PAIRED},
  {[BOKEH]: BOKEH_PASTEL_1, [VEGA]: VEGA_PASTEL_1},
  {[BOKEH]: BOKEH_PASTEL_2, [VEGA]: VEGA_PASTEL_2},
  {[BOKEH]: BOKEH_SET_1, [VEGA]: VEGA_SET_1},
  {[BOKEH]: BOKEH_SET_2, [VEGA]: VEGA_SET_2},
  {[BOKEH]: BOKEH_SET_3, [VEGA]: VEGA_SET_3},
  {[BOKEH]: undefined, [VEGA]: VEGA_TABLEAU_10},
  {[BOKEH]: undefined, [VEGA]: VEGA_TABLEAU_20},
  {[BOKEH]: undefined, [VEGA]: VEGA_OBSERVABLE_10},
  {[BOKEH]: BOKEH_COLORBLIND, [VEGA]: undefined}
];

export const DIVERGING_PALETTE_VENDORS = [
  {[BOKEH]: undefined, [VEGA]: VEGA_BLUE_ORANGE},
  {
    [BOKEH]: BOKEH_BROWN_BLUE_GREEN,

    [VEGA]: VEGA_BROWN_BLUE_GREEN
  },
  {
    [BOKEH]: BOKEH_PURPLE_GREEN,

    [VEGA]: VEGA_PURPLE_GREEN
  },
  {
    [BOKEH]: BOKEH_PINK_YELLOW_GREEN,

    [VEGA]: VEGA_PINK_YELLOW_GREEN
  },
  {
    [BOKEH]: BOKEH_PURPLE_ORANGE,

    [VEGA]: VEGA_PURPLE_ORANGE
  },
  {[BOKEH]: BOKEH_RED_BLUE, [VEGA]: VEGA_RED_BLUE},
  {[BOKEH]: BOKEH_RED_GREY, [VEGA]: VEGA_RED_GREY},
  {
    [BOKEH]: BOKEH_RED_YELLOW_BLUE,

    [VEGA]: VEGA_RED_YELLOW_BLUE
  },
  {
    [BOKEH]: BOKEH_RED_YELLOW_GREEN,

    [VEGA]: VEGA_RED_YELLOW_GREEN
  },
  {[BOKEH]: BOKEH_SPECTRAL, [VEGA]: VEGA_SPECTRAL}
];

export const SEQUENTIAL_PALETTE_VENDORS = [
  // Single hue
  {[BOKEH]: BOKEH_BLUES, [VEGA]: VEGA_BLUES},
  {[BOKEH]: undefined, [VEGA]: VEGA_TEAL_BLUES},
  {[BOKEH]: undefined, [VEGA]: VEGA_TEALS},
  {[BOKEH]: BOKEH_GREENS, [VEGA]: VEGA_GREENS},
  {[BOKEH]: undefined, [VEGA]: VEGA_BROWNS},
  {[BOKEH]: BOKEH_ORANGES, [VEGA]: VEGA_ORANGES},
  {[BOKEH]: BOKEH_REDS, [VEGA]: VEGA_REDS},
  {[BOKEH]: BOKEH_PURPLES, [VEGA]: VEGA_PURPLES},
  {[BOKEH]: undefined, [VEGA]: VEGA_WARM_GREYS},
  {[BOKEH]: BOKEH_GREYS, [VEGA]: VEGA_GREYS},
  // Multiple hues
  {[BOKEH]: BOKEH_VIRIDIS, [VEGA]: VEGA_VIRIDIS},
  {[BOKEH]: BOKEH_MAGMA, [VEGA]: VEGA_MAGMA},
  {[BOKEH]: BOKEH_INFERNO, [VEGA]: VEGA_INFERNO},
  {[BOKEH]: BOKEH_PLASMA, [VEGA]: VEGA_PLASMA},
  {[BOKEH]: undefined, [VEGA]: VEGA_CIVIDIS},
  {[BOKEH]: undefined, [VEGA]: VEGA_TURBO},
  {[BOKEH]: BOKEH_BLUE_GREEN, [VEGA]: VEGA_BLUE_GREEN},
  {
    [BOKEH]: BOKEH_BLUE_PURPLE,

    [VEGA]: VEGA_BLUE_PURPLE
  },
  {[BOKEH]: undefined, [VEGA]: VEGA_GOLD_GREEN},
  {[BOKEH]: undefined, [VEGA]: VEGA_GOLD_ORANGE},
  {[BOKEH]: undefined, [VEGA]: VEGA_GOLD_RED},
  {[BOKEH]: BOKEH_GREEN_BLUE, [VEGA]: VEGA_GREEN_BLUE},
  {[BOKEH]: BOKEH_ORANGE_RED, [VEGA]: VEGA_ORANGE_RED},
  {
    [BOKEH]: BOKEH_PURPLE_BLUE_GREEN,

    [VEGA]: VEGA_PURPLE_BLUE_GREEN
  },
  {
    [BOKEH]: BOKEH_PURPLE_BLUE,

    [VEGA]: VEGA_PURPLE_BLUE
  },
  {[BOKEH]: BOKEH_PURPLE_RED, [VEGA]: VEGA_PURPLE_RED},
  {[BOKEH]: BOKEH_RED_PURPLE, [VEGA]: VEGA_RED_PURPLE},
  {
    [BOKEH]: BOKEH_YELLOW_GREEN_BLUE,

    [VEGA]: VEGA_YELLOW_GREEN_BLUE
  },
  {
    [BOKEH]: BOKEH_YELLOW_GREEN,

    [VEGA]: VEGA_YELLOW_GREEN
  },
  {
    [BOKEH]: BOKEH_YELLOW_ORANGE_BROWN,

    [VEGA]: VEGA_YELLOW_ORANGE_BROWN
  },
  {
    [BOKEH]: BOKEH_YELLOW_ORANGE_RED,

    [VEGA]: VEGA_YELLOW_ORANGE_RED
  },
  // For dark backgrounds
  {[BOKEH]: undefined, [VEGA]: VEGA_DARK_BLUE},
  {[BOKEH]: undefined, [VEGA]: VEGA_DARK_GOLD},
  {[BOKEH]: undefined, [VEGA]: VEGA_DARK_GREEN},
  {[BOKEH]: undefined, [VEGA]: VEGA_DARK_MULTI},
  {[BOKEH]: undefined, [VEGA]: VEGA_DARK_RED},
  // For light backgrounds
  {[BOKEH]: undefined, [VEGA]: VEGA_LIGHT_GREY_RED},
  {[BOKEH]: undefined, [VEGA]: VEGA_LIGHT_GREY_TEAL},
  {[BOKEH]: undefined, [VEGA]: VEGA_LIGHT_MULTI},
  {[BOKEH]: undefined, [VEGA]: VEGA_LIGHT_ORANGE},
  {[BOKEH]: undefined, [VEGA]: VEGA_LIGHT_TEAL_BLUE}
];

export const CYCLICAL_PALETTE_VENDORS = [
  {[BOKEH]: undefined, [VEGA]: VEGA_RAINBOW},
  {[BOKEH]: undefined, [VEGA]: VEGA_SINEBOW}
];

const PALETTE_TO_VENDOR_MAP = {};
[
  DIVERGING_PALETTE_VENDORS,
  CATEGORICAL_PALETTE_VENDORS,
  SEQUENTIAL_PALETTE_VENDORS,
  CYCLICAL_PALETTE_VENDORS
].forEach((mappings) => {
  mappings.forEach((mapping) => {
    Object.keys(mapping).forEach((vendor) => {
      const name = mapping[vendor];
      if (name) {
        PALETTE_TO_VENDOR_MAP[name] = vendor;
      }
    });
  });
});

const BOKEH_CONTINUOUS_PALETTE_NAMES = Object.keys(BOKEH_PALETTE_DATA).filter(
  (name) => ~Object.keys(BOKEH_PALETTE_DATA[name]).indexOf(256)
);

const VEGA_CONTINUOUS_PALETTE_NAMES = Object.keys(VEGA_PALETTE_DATA).filter(
  (name) => ~Object.keys(VEGA_PALETTE_DATA[name]).indexOf(256)
);

export function parsePaletteName(name) {
  if (!Object.prototype.hasOwnProperty.call(PALETTE_TO_VENDOR_MAP, name)) {
    throw new Error(`Palette name "${name}" not recognized.`);
  }

  const vendor = PALETTE_TO_VENDOR_MAP[name];
  const palette = name.substring(vendor.length + 1);

  return {vendor, palette};
}

function getPalette(name) {
  const {vendor} = parsePaletteName(name);

  if (vendor === BOKEH) {
    return BOKEH_PALETTE_DATA[name];
  } else if (vendor === VEGA) {
    return VEGA_PALETTE_DATA[name];
  }

  throw new Error(`Vendor "${vendor}" no recognized.`);
}

function getDocsPalette(name) {
  const {vendor} = parsePaletteName(name);

  if (vendor === BOKEH) {
    return BOKEH_DOCS_PALETTE_DATA[name];
  } else if (vendor === VEGA) {
    return VEGA_DOCS_PALETTE_DATA[name];
  }

  throw new Error(`Vendor "${vendor}" no recognized.`);
}

function isContinuous(name) {
  const {vendor} = parsePaletteName(name);

  if (vendor === BOKEH) {
    return Object.prototype.hasOwnProperty.call(
      BOKEH_CONTINUOUS_PALETTE_NAMES,
      name
    );
  } else if (vendor === VEGA) {
    return Object.prototype.hasOwnProperty.call(
      VEGA_CONTINUOUS_PALETTE_NAMES,
      name
    );
  }

  throw new Error(`Vendor "${vendor}" no recognized.`);
}

/**
 * TODO Handle `asRgb`
 *
 * @param {Array} palette
 * @param {Number} n
 * @param {bool} asRgb
 */
export function toDiscretePalette(palette, n = 6, asRgb = false) {
  const sizes = Object.keys(palette).map(Number);
  const nClamped = Math.min(
    Math.max(...sizes),
    Math.max(Math.min(...sizes), n)
  );
  const result = palette[nClamped + ''].slice(0, n);

  return result;
}

// export function toContinuousPalette(palette, n = 6, asRgb = false) {}

export function discretePalette(name, n = 6, asRgb = false) {
  return toDiscretePalette(getPalette(name), n, asRgb);
}

// export function continuousPalette(name, n = 6, asRgb = false) {
//   if (!isContinuous(name)) {
//     throw new Error(
//       `Generating continuous palettes of "${name}" is not supported`
//     );
//   }

//   return toContinuousPalette(getPalette(name)[256], n, asRgb);
// }

/**
 * TODO Handle `asRgb`
 *
 * @param {string} name
 * @param {bool} asRgb
 */
export function docsPalette(name, asRgb = false) {
  const result = getDocsPalette(name);

  return result;
}
