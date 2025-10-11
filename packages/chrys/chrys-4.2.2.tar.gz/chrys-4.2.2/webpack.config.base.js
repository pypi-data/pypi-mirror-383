import pkg from './package.json' with {type: 'json'};

export default {
  resolve: {
    extensions: ['.js', '.jsx'],
    modules: ['node_modules/']
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        loader: 'babel-loader?cacheDirectory',
        options: {
          babelrc: false,
          comments: false,
          env: {
            development: {
              plugins: [
                [
                  '@babel/plugin-transform-runtime',
                  {
                    helpers: false
                  }
                ],
                ['@babel/plugin-proposal-class-properties', {loose: true}],
                [
                  '@babel/plugin-proposal-object-rest-spread',
                  {useBuiltIns: false}
                ],
                '@babel/plugin-transform-object-assign' // For IE
              ]
            },
            production: {
              plugins: [
                [
                  '@babel/plugin-transform-runtime',
                  {
                    helpers: false
                  }
                ],
                ['@babel/plugin-proposal-class-properties', {loose: true}],
                [
                  '@babel/plugin-proposal-object-rest-spread',
                  {useBuiltIns: false}
                ],
                '@babel/plugin-transform-object-assign' // For IE
              ]
            }
          },
          presets: [
            [
              '@babel/preset-env',
              {
                loose: true,
                modules: 'commonjs',
                targets: {
                  browsers: pkg.browserslist
                },
                useBuiltIns: false
              }
            ]
          ]
        }
      }
    ]
  }
};
