import _ from 'lodash';
import {scaleQuantile} from 'd3-scale';
import {BOKEH_TO_VEGA, VEGA_TO_BOKEH} from '../config/index.js';

export function continuousPalette(colors, count) {
  const scale = scaleQuantile(
    _.times(count, (i) => i),
    colors
  );
  return _.times(count, (i) => scale(i));
}

export function bokehToVega(name) {
  return BOKEH_TO_VEGA[name];
}

export function vegaToBokeh(name) {
  return VEGA_TO_BOKEH[name];
}

export function jsSerialize(vendor, vars, maxSize, docsMaxSize) {
  const VENDOR_PALETTES = `${vendor.toUpperCase()}_PALETTES`;
  const VENDOR_PALETTE_DATA = `${vendor.toUpperCase()}_PALETTE_DATA`;
  const VENDOR_PALETTE_NAMES = `${vendor.toUpperCase()}_PALETTE_NAMES`;
  const VENDOR_DOCS_PALETTES = `${vendor.toUpperCase()}_DOCS_PALETTES`;
  const VENDOR_DOCS_PALETTE_DATA = `${vendor.toUpperCase()}_DOCS_PALETTE_DATA`;

  let result = '';

  result +=
    'export const ' +
    VENDOR_PALETTE_DATA +
    ' = ' +
    JSON.stringify(vars.palettes, null, 2) +
    '\n';
  _.times(maxSize, (i) => {
    result = result.replace(new RegExp('"' + (i + 1) + '"', 'g'), i + 1);
  });
  result += '\n';

  result +=
    'export const ' +
    VENDOR_DOCS_PALETTE_DATA +
    ' = ' +
    JSON.stringify(vars.docsPalettes, null, 2) +
    '\n';
  _.times(docsMaxSize, (i) => {
    result = result.replace(new RegExp('"' + (i + 1) + '"', 'g'), i + 1);
  });
  result += '\n';

  _.forEach(vars.constantNames, (v, k) => {
    result += 'export const ' + k + ' = "' + v + '"\n';
  });
  result += '\n';

  result += `const _${VENDOR_PALETTE_NAMES} = {}\n`;
  _.forEach(vars.constantNames, (v, k) => {
    result += `_${VENDOR_PALETTE_NAMES}['${k}'] = '${v}'\n`;
  });
  result += `export const ${VENDOR_PALETTE_NAMES} = _${VENDOR_PALETTE_NAMES}\n`;
  result += '\n';

  result += `const _${VENDOR_PALETTES} = {}\n`;
  _.forEach(vars.vendorNames, (v, k) => {
    result += `_${VENDOR_PALETTES}['${k}'] = ${VENDOR_PALETTE_DATA}[${v}]\n`;
  });
  result += `export const ${VENDOR_PALETTES} = _${VENDOR_PALETTES}\n`;
  result += '\n';

  result += `const _${VENDOR_DOCS_PALETTES} = {}\n`;
  _.forEach(vars.vendorNames, (v, k) => {
    result += `_${VENDOR_DOCS_PALETTES}['${k}'] = ${VENDOR_DOCS_PALETTE_DATA}[${v}]\n`;
  });
  result += `export const ${VENDOR_DOCS_PALETTES} = _${VENDOR_DOCS_PALETTES}\n`;

  return result;
}

export function pySerialize(vendor, vars, maxSize, docsMaxSize) {
  const VENDOR_PALETTES = `${vendor.toUpperCase()}_PALETTES`;
  const VENDOR_PALETTE_DATA = `${vendor.toUpperCase()}_PALETTE_DATA`;
  const VENDOR_PALETTE_NAMES = `${vendor.toUpperCase()}_PALETTE_NAMES`;
  const VENDOR_DOCS_PALETTES = `${vendor.toUpperCase()}_DOCS_PALETTES`;
  const VENDOR_DOCS_PALETTE_DATA = `${vendor.toUpperCase()}_DOCS_PALETTE_DATA`;

  let result = '';

  result +=
    VENDOR_PALETTE_DATA + ' = ' + JSON.stringify(vars.palettes, null, 2) + '\n';
  _.times(maxSize, (i) => {
    result = result.replace(new RegExp('"' + (i + 1) + '"', 'g'), i + 1);
  });
  result += '\n';

  result +=
    VENDOR_DOCS_PALETTE_DATA +
    ' = ' +
    JSON.stringify(vars.docsPalettes, null, 2) +
    '\n';
  _.times(docsMaxSize, (i) => {
    result = result.replace(new RegExp('"' + (i + 1) + '"', 'g'), i + 1);
  });
  result += '\n';

  _.forEach(vars.constantNames, (v, k) => {
    result += k + ' = "' + v + '"\n';
  });
  result += '\n';

  result += `${VENDOR_PALETTE_NAMES} = {}\n`;
  _.forEach(vars.constantNames, (v, k) => {
    result += `${VENDOR_PALETTE_NAMES}['${k}'] = '${v}'\n`;
  });
  result += '\n';

  result += `${VENDOR_PALETTES} = {}\n`;
  _.forEach(vars.vendorNames, (v, k) => {
    result += `${VENDOR_PALETTES}['${k}'] = ${VENDOR_PALETTE_DATA}[${v}]\n`;
  });
  result += '\n';

  result += `${VENDOR_DOCS_PALETTES} = {}\n`;
  _.forEach(vars.vendorNames, (v, k) => {
    result += `${VENDOR_DOCS_PALETTES}['${k}'] = ${VENDOR_DOCS_PALETTE_DATA}[${v}]\n`;
  });

  return result;
}
