const backend = 'http://127.0.0.1:8080/';

module.exports = {
  devServer: {
    proxy: {
      '^/(action|login|preview|state)': {
        target: backend,
        changeOrigin: true,
      },
    },
  },
};
