import _ from 'lodash';
import fs from 'fs-extra';
import globby from 'globby';
import nunjucks from 'nunjucks';
import path from 'path';
import {fileURLToPath} from 'url';
import Promise from 'bluebird';
import {
  BOKEH,
  VEGA,
  BOKEH_PALETTE_NAMES,
  VEGA_PALETTE_NAMES,
  CATEGORICAL_PALETTE_VENDORS,
  DIVERGING_PALETTE_VENDORS,
  SEQUENTIAL_PALETTE_VENDORS,
  CYCLICAL_PALETTE_VENDORS,
  bestColorContrast,
  docsPalette,
  parsePaletteName,
  discretePalette
} from '../src/js/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const env = new nunjucks.Environment(new nunjucks.FileSystemLoader('.'));

env.addFilter('best_color_contrast', bestColorContrast);

export function buildDemo() {
  const rootPath = path.resolve(__dirname, '..');
  const demoDest = path.join(rootPath, 'demo');

  const copyFiles = [
    {
      patterns: [path.join(rootPath, 'node_modules/jquery/dist/*.js')],
      base: 'node_modules',
      destBase: 'vendor'
    },
    {
      patterns: [path.join(rootPath, 'node_modules/normalize-css/*.css')],
      base: 'node_modules',
      destBase: 'vendor'
    },
    {
      patterns: [
        path.join(rootPath, 'node_modules/prismjs/**/*.js'),
        path.join(rootPath, 'node_modules/prismjs/themes/*.css')
      ],
      base: 'node_modules',
      destBase: 'vendor'
    },
    {
      patterns: [path.join(rootPath, 'node_modules/prism-themes/themes/*.css')],
      base: 'node_modules',
      destBase: 'vendor'
    },
    {
      patterns: [path.join(rootPath, 'css/**/*.css')],
      base: 'css'
    },
    {
      patterns: [path.join(rootPath, 'src/demo/**/*.css')],
      base: 'src/demo',
      destBase: ''
    },
    {
      patterns: [path.join(rootPath, 'src/demo/**/*.js')],
      base: 'src/demo',
      destBase: ''
    }
  ];

  const BOKEH_PALETTE_NAMES_MAP = _.zipObject(
    Object.keys(BOKEH_PALETTE_NAMES).map((k) => BOKEH_PALETTE_NAMES[k]),
    Object.keys(BOKEH_PALETTE_NAMES)
  );

  const VEGA_PALETTE_NAMES_MAP = _.zipObject(
    Object.keys(VEGA_PALETTE_NAMES).map((k) => VEGA_PALETTE_NAMES[k]),
    Object.keys(VEGA_PALETTE_NAMES)
  );

  function getItem(name, discreteSizes) {
    if (!name) {
      return undefined;
    }

    const {vendor, palette: vendorName} = parsePaletteName(name);
    let jsVar;
    let discretePalettes;

    if (vendor === BOKEH) {
      jsVar = BOKEH_PALETTE_NAMES_MAP[name];
    } else if (vendor === VEGA) {
      jsVar = VEGA_PALETTE_NAMES_MAP[name];
    }

    const pythonVar = jsVar;
    const sassVar = _.kebabCase(jsVar);

    if (discreteSizes) {
      discretePalettes = discreteSizes.map((i) => discretePalette(name, i));
    }

    const palette = docsPalette(name);

    return {
      jsVar,
      pythonVar,
      sassVar,
      name,
      vendorName,
      palette,
      discretePalettes
    };
  }

  const categoricalPalettes = CATEGORICAL_PALETTE_VENDORS.filter(
    (x) => x[BOKEH] || x[VEGA]
  ).map((x) => ({
    [BOKEH]: getItem(x[BOKEH]),
    [VEGA]: getItem(x[VEGA])
  }));

  const divergingPalettes = DIVERGING_PALETTE_VENDORS.filter(
    (x) => x[BOKEH] || x[VEGA]
  ).map((x) => ({
    [BOKEH]: getItem(x[BOKEH], [3, 5, 7, 9]),
    [VEGA]: getItem(x[VEGA], [3, 5, 7, 9])
  }));

  const sequentialPalettes = SEQUENTIAL_PALETTE_VENDORS.filter(
    (x) => x[BOKEH] || x[VEGA]
  ).map((x) => ({
    [BOKEH]: getItem(x[BOKEH], [3, 4, 5, 6, 7, 8, 9]),
    [VEGA]: getItem(x[VEGA], [3, 4, 5, 6, 7, 8, 9])
  }));

  const cyclicalPalettes = CYCLICAL_PALETTE_VENDORS.filter(
    (x) => x[BOKEH] || x[VEGA]
  ).map((x) => ({
    [BOKEH]: getItem(x[BOKEH]),
    [VEGA]: getItem(x[VEGA])
  }));

  const context = {
    categoricalPalettes,
    divergingPalettes,
    sequentialPalettes,
    cyclicalPalettes
  };

  return Promise.each(copyFiles, (d) =>
    globby(d.patterns).then((files) =>
      Promise.each(files, (file) => {
        const x = file.substring(path.join(rootPath, d.base).length);
        const y = path.join(demoDest, _.get(d, 'destBase', d.base), x);
        const z = path.dirname(y);

        return fs.mkdirp(z).then(() => fs.copy(file, y));
      })
    )
  )
    .then(() => fs.readFile(path.join(rootPath, 'src/demo/index.njk'), 'utf-8'))
    .then(
      (data) =>
        new Promise((resolve, reject) => {
          env.renderString(data, context, (err, res) => {
            if (err) {
              reject(err);
            } else {
              fs.outputFile(
                path.join(demoDest, 'index.html'),
                res,
                'utf-8'
              ).then(resolve);
            }
          });
        })
    );
}
