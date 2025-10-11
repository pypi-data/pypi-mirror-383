import _ from 'lodash';
import fs from 'fs-extra';
import path from 'path';
import {fileURLToPath} from 'url';
import {
  YlGn,
  YlGnBu,
  GnBu,
  BuGn,
  PuBuGn,
  PuBu,
  BuPu,
  RdPu,
  PuRd,
  OrRd,
  YlOrRd,
  YlOrBr,
  Purples,
  Blues,
  Greens,
  Oranges,
  Reds,
  Greys,
  PuOr,
  BrBG,
  PRGn,
  PiYG,
  RdBu,
  RdGy,
  RdYlBu,
  Spectral,
  RdYlGn,
  Inferno,
  Magma,
  Plasma,
  Viridis,
  Accent,
  Dark2,
  Paired,
  Pastel1,
  Pastel2,
  Set1,
  Set2,
  Set3,
  Category10,
  Category20,
  Category20b,
  Category20c,
  Colorblind
} from '@bokeh/bokehjs/build/js/lib/api/palettes.js';
import {
  continuousPalette,
  bokehToVega,
  jsSerialize,
  pySerialize
} from './utils.js';

const discrete = {
  Category10,
  Category20,
  Category20b,
  Category20c,
  Colorblind,
  Accent,
  Dark2,
  Paired,
  Pastel1,
  Pastel2,
  Set1,
  Set2,
  Set3
};

const continuous = {
  YlGn,
  YlGnBu,
  GnBu,
  BuGn,
  PuBuGn,
  PuBu,
  BuPu,
  RdPu,
  PuRd,
  OrRd,
  YlOrRd,
  YlOrBr,
  Purples,
  Blues,
  Greens,
  Oranges,
  Reds,
  Greys,
  PuOr,
  BrBG,
  PRGn,
  PiYG,
  RdBu,
  RdGy,
  RdYlBu,
  Spectral,
  RdYlGn,
  Inferno,
  Magma,
  Plasma,
  Viridis
};

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

_.forEach(discrete, (palettes, vendorName) => {
  const uniqueName = 'bokeh_' + vendorName;
  const constantName = _.snakeCase(
    'bokeh_' + bokehToVega(vendorName)
  ).toUpperCase();

  vars.constantNames[constantName] = uniqueName;
  vars.vendorNames[vendorName] = constantName;
  vars.palettes[uniqueName] = {};

  _.forEach(palettes, (palette) => {
    maxSize = Math.max(maxSize, palette.length);
    vars.palettes[uniqueName][palette.length] = palette.map(
      (d) => '#' + _.padStart(d.toString(16), 8, '0').substring(0, 6)
    );
  });

  const x = _.max(_.values(palettes).map((p) => p.length));
  const docsPalette = _.first(
    _.values(palettes).filter((p) => p.length === x)
  ).map((d) => '#' + _.padStart(d.toString(16), 8, '0').substring(0, 6));
  vars.docsPalettes[uniqueName] = docsPalette;
});

_.forEach(continuous, (palettes, vendorName) => {
  const uniqueName = 'bokeh_' + vendorName;
  const constantName = _.snakeCase(
    'bokeh_' + bokehToVega(vendorName)
  ).toUpperCase();

  vars.constantNames[constantName] = uniqueName;
  vars.vendorNames[vendorName] = constantName;
  vars.palettes[uniqueName] = {};

  _.forEach(palettes, (palette) => {
    maxSize = Math.max(maxSize, palette.length);
    vars.palettes[uniqueName][palette.length] = palette.map(
      (d) => '#' + _.padStart(d.toString(16), 8, '0').substring(0, 6)
    );
  });

  const x = _.max(_.values(palettes).map((p) => p.length));
  const docsPalette = _.first(
    _.values(palettes).filter((p) => p.length === x)
  ).map((d) => '#' + _.padStart(d.toString(16), 8, '0').substring(0, 6));
  vars.docsPalettes[uniqueName] = continuousPalette(docsPalette, docsMaxSize);
});

fs.outputFile(jsFile, jsSerialize('bokeh', vars, maxSize, docsMaxSize));
fs.outputFile(pyFile, pySerialize('bokeh', vars, maxSize, docsMaxSize));
