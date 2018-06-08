const webpackMerge = require('webpack-merge');

const commonConfig = require('./webpack.common.js');
const helpers = require('./helpers.js');

const port = 3011;
const publicPath = 'http://localhost:' + 3011 + '/bundle/'

module.exports = function (env) {
  return webpackMerge(commonConfig(), {
    output: {
      publicPath: publicPath,
      crossOriginLoading: "anonymous",
    },

    module: {
      rules: [
        {
          test: /\.s?css$/,
          include: [ /^node_modules\/yellowant-common-client\/src\/styles$/ , helpers.srcPath ],
          use: [{
              loader: "style-loader" // creates style nodes from JS strings
            }, {
              loader: "css-loader" // translates CSS into CommonJS
            }, {
              loader: "sass-loader" // compiles Sass to CSS
            }
          ]
        }
      ]
    },

    devtool: 'cheap-module-source-map',
    devServer: {
      headers: {
        'Access-Control-Allow-Origin': '*'
      },
      publicPath: publicPath,
      contentBase: helpers.appPath,
      hot: true,
      inline: true,
      port: port
    }
  })
}