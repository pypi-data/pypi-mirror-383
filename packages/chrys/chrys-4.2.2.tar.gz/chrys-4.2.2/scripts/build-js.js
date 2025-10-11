import globby from 'globby';
import log from 'fancy-log';
import path from 'path';
import Promise from 'bluebird';
import webpack from 'webpack';
import {config} from '../config/index.js';
import webpackConfig from '../webpack.config.prod.js';
import pkg from '../package.json' with {type: 'json'};

function _buildJs(buildConfig) {
  return new Promise((resolve, reject) => {
    webpack(buildConfig, function (err, stats) {
      if (err) {
        log('[webpack]', err);
        reject();
      } else {
        log(
          '[webpack]',
          stats.toString({
            cached: false,
            cachedAssets: false,
            children: true,
            chunks: false,
            chunkModules: false,
            chunkOrigins: true,
            colors: true,
            entrypoints: false,
            errorDetails: false,
            hash: false,
            modules: false,
            performance: true,
            reasons: true,
            source: false,
            timings: true,
            version: true,
            warnings: true
          })
        );
        resolve();
      }
    });
  });
}

function buildJsModules() {
  return globby([path.join(config.module.src, 'js/*.js')])
    .then((files) =>
      files.reduce((result, file) => {
        const basename = path.basename(file, path.extname(file));

        return result.concat([
          {
            ...webpackConfig,
            entry: {
              [basename]: path.join(config.module.src, 'js', basename + '.js'),
              [basename + '.min']: path.join(
                config.module.src,
                'js',
                basename + '.js'
              )
            },
            output: {
              filename: '[name].cjs',
              path: path.resolve(config.module.dist.cjs),
              libraryTarget: 'commonjs'
            }
          },
          {
            ...webpackConfig,
            entry: {
              [basename]: path.join(config.module.src, 'js', basename + '.js'),
              [basename + '.min']: path.join(
                config.module.src,
                'js',
                basename + '.js'
              )
            },
            output: {
              filename: '[name].js',
              path: path.resolve(config.module.dist.umd),
              library: pkg.name,
              libraryTarget: 'umd'
            }
          }
        ]);
      }, [])
    )
    .then((buildConfigs) =>
      Promise.each(buildConfigs, (buildConfig) => _buildJs(buildConfig))
    );
}

Promise.each([buildJsModules], (task) => task());
