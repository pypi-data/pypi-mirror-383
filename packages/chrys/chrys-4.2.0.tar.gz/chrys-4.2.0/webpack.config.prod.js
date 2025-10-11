import TerserPlugin from 'terser-webpack-plugin';
import webpack from 'webpack';
import webpackConfigBase from './webpack.config.base.js';

export default {
  ...webpackConfigBase,
  mode: 'production',
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        cache: true,
        parallel: true,
        include: /\.min\.js$/,
        extractComments: false,
        terserOptions: {
          ecma: 5,
          output: {
            comments: false,
            indent_level: 2,
            semicolons: true
          }
        }
      })
    ]
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production')
    }),
    new webpack.NoEmitOnErrorsPlugin()
  ]
};
