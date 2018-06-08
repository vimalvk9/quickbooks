const webpackMerge = require('webpack-merge');
const ExtractTextPlugin = require("extract-text-webpack-plugin");

const commonConfig = require('./webpack.common.js');
const helpers = require('./helpers.js');


module.exports = function() {
  return webpackMerge(commonConfig(), {
    output: {
      publicPath: '/static/frontend/onboarding/dist/',
    },
    module: {
      rules: [
        {
          test: /\.s?css$/,
          include: [ /^node_modules\/yellowant-common-client\/src\/styles$/ , helpers.srcPath ],
          use: ExtractTextPlugin.extract({
            use: [{
              loader: "css-loader"
            }, {
              loader: "sass-loader"
            }],
            // use style-loader in development
            fallback: "style-loader"
          })
        }
      ]
    },
    plugins: [
      new ExtractTextPlugin({
        filename: "[name].css",
        disable: process.env.NODE_ENV === "development"
      })
    ]
  })
}
