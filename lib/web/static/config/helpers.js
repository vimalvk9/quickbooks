const path = require('path');

const rootPath = path.resolve(__dirname, '..');
const distPath = path.resolve(rootPath, 'dist');
const publicPath = 'http://localhost:3011/bundle/';
const srcPath = path.resolve(rootPath, 'src');
const appPath = path.resolve(srcPath, 'app');
const stylePath = path.resolve(srcPath, 'style');

module.exports = {
  rootPath,
  distPath,
  srcPath,
  appPath,
  stylePath
}