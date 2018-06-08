const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');

const helpers = require('./helpers.js');

module.exports = function() {
  return {
    entry: path.resolve(helpers.appPath, 'app.js'),
    externals: {
      'angular': 'angular',
      'angular-material': '"ngMaterial"',
      'angular-ui-router': '"ui.router"',
      'angular-messages': ' "ngMessages" ',
      'angular-aria': '"ngAria"',
      'angular-animate': '"ngAnimate"'
    },
    output: {
      path: helpers.distPath,
      filename: '[name].js',
      sourceMapFilename: '[name].map'
    },

    resolve: {
      extensions: ['.js'],
//      modules: [path.resolve(helpers.rootPath, 'node_modules')]
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          include: /(node_modules\/yellowant-common-client\/src|src\/app)/,
          loader: 'babel-loader',
          options: {
            plugins: ['transform-runtime'],
            presets: [['env', { 'modules': false }], 'stage-0']
//            presets: ["es2015-native-modules"]
          }
        },

        {
          test: /\.html$/,
          use: [
            {
              loader: 'html-loader'
            }
          ]

        },

        {
          test: /\.(jpg|png|gif)$/,
          loader: 'file-loader',
          options: {
            name: '[name].[hash].[ext]'
          }
        }
      ]
    },

    plugins: [
      new BundleTracker({path: helpers.rootPath, filename: 'webpack-stats.json'})
    ]
  }
}