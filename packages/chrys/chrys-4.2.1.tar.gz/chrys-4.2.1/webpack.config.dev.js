import webpack from 'webpack';
import webpackConfigBase from './webpack.config.base.js';

export default {
  ...webpackConfigBase,
  mode: 'development',
  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('development')
    }),
    new webpack.NamedModulesPlugin(),
    new webpack.NoEmitOnErrorsPlugin()
  ]
};
