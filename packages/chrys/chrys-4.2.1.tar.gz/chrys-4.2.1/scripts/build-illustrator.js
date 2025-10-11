import _ from 'lodash';
import {illustratorSwatches} from 'chrys-cli';
import chroma from 'chroma-js';
import path from 'path';
import Promise from 'bluebird';
import {config} from '../config/index.js';
import {
  BOKEH_PALETTE_DATA,
  BOKEH_PALETTE_NAMES
} from '../data/bokeh-palettes.js';
import {VEGA_PALETTE_DATA, VEGA_PALETTE_NAMES} from '../data/vega-palettes.js';

function buildIllustrator() {
  const illustratorPalettes = [];

  Object.keys(BOKEH_PALETTE_NAMES).forEach((varName) => {
    const sassName = _.kebabCase(varName);

    Object.values(BOKEH_PALETTE_DATA[BOKEH_PALETTE_NAMES[varName]]).forEach(
      (values) => {
        const group = sassName + '-' + values.length;

        illustratorPalettes.push({
          name: group,
          colors: values.map((color, index) => ({
            group: group,
            name: group + '-' + (index + 1),
            rgb: chroma(color).rgb()
          }))
        });
      }
    );
  });

  Object.keys(VEGA_PALETTE_NAMES).forEach((varName) => {
    const sassName = _.kebabCase(varName);

    Object.values(VEGA_PALETTE_DATA[VEGA_PALETTE_NAMES[varName]]).forEach(
      (values) => {
        const group = sassName + '-' + values.length;

        illustratorPalettes.push({
          name: group,
          colors: values.map((color, index) => ({
            group: group,
            name: group + '-' + (index + 1),
            rgb: chroma(color).rgb()
          }))
        });
      }
    );
  });

  return Promise.each(illustratorPalettes, (palette) => {
    const illustratorConfig = _.cloneDeep(config.illustratorTasks.swatches);
    illustratorConfig.document.mode = 'rgb';
    illustratorConfig.colors = palette.colors;

    const dist = path.resolve('illustrator/' + palette.name + '.js');

    return illustratorSwatches(illustratorConfig, dist);
  });
}

Promise.each([buildIllustrator], (task) => task());
