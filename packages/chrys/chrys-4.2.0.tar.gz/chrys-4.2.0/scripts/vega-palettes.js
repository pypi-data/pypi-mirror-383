import _ from 'lodash';
import fs from 'fs-extra';
import path from 'path';
import {fileURLToPath} from 'url';
import {color} from 'd3-color';
import {discrete, continuous} from 'vega-scale/src/palettes.js';
import {scheme} from 'vega-scale/src/schemes.js';
import {quantizeInterpolator} from 'vega-scale/src/interpolate.js';
import {continuousPalette, jsSerialize, pySerialize} from './utils.js';

function getColors(palette) {
  var n = (palette.length / 6) | 0;
  var c = new Array(n);
  var i = 0;
  while (i < n) c[i] = '#' + palette.slice(i * 6, ++i * 6);
  return c;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const basename = path.basename(__filename, path.extname(__filename));
const jsFile = path.join(__dirname, '../data/' + _.kebabCase(basename) + '.js');
const pyFile = path.join(
  __dirname,
  '../chrys/data/' + _.snakeCase(basename) + '.py'
);
const vars = {
  constantNames: {},
  vendorNames: {},
  palettes: {},
  docsPalettes: {}
};
let maxSize = 0;
const docsMaxSize = 11;

Object.keys(discrete).forEach((vendorName) => {
  const uniqueName = 'vega_' + vendorName.toLowerCase();
  const constantName = _.snakeCase('vega_' + vendorName).toUpperCase();

  vars.constantNames[constantName] = uniqueName;
  vars.vendorNames[vendorName.toLowerCase()] = constantName;
  vars.palettes[uniqueName] = {};
  maxSize = Math.max(maxSize, scheme(vendorName).length);

  for (let i = 1; i <= scheme(vendorName).length; i++) {
    vars.palettes[uniqueName][i] = scheme(vendorName).slice(0, i);
  }

  vars.docsPalettes[uniqueName] = scheme(vendorName);
});

Object.keys(continuous).forEach((vendorName) => {
  const uniqueName = 'vega_' + vendorName.toLowerCase();
  const constantName = _.snakeCase('vega_' + vendorName).toUpperCase();
  const docsPalette = getColors(continuous[vendorName]);

  vars.constantNames[constantName] = uniqueName;
  vars.vendorNames[vendorName.toLowerCase()] = constantName;
  vars.palettes[uniqueName] = {};
  maxSize = Math.max(maxSize, 9);

  for (let i = 1; i <= 9; i++) {
    vars.palettes[uniqueName][i] = quantizeInterpolator(
      scheme(vendorName),
      i
    ).map((d) => color(d).formatHex());
  }

  if (~['viridis', 'magma', 'inferno', 'plasma'].indexOf(vendorName)) {
    maxSize = Math.max(maxSize, 256);

    vars.palettes[uniqueName][256] = quantizeInterpolator(
      scheme(vendorName),
      256
    ).map((d) => color(d).formatHex());
  }

  vars.docsPalettes[uniqueName] = continuousPalette(docsPalette, docsMaxSize);
});

fs.outputFile(jsFile, jsSerialize('vega', vars, maxSize, docsMaxSize));
fs.outputFile(pyFile, pySerialize('vega', vars, maxSize, docsMaxSize));
