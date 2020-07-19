const path = require('path');

module.exports = {
  entry: {
    voctoweb: './js/voctoweb.js',
    vendor: './js/vendor.js',
  },
  mode: 'development',
  output: {
    path: path.resolve(__dirname, 'static'),
    filename: '[name].bundle.js',
  },
};
