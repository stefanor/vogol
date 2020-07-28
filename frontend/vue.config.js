const backend = process.env.BACKEND || 'http://127.0.0.1:8080/';

module.exports = {
  devServer: {
    proxy: {
      '^/(action|login|playback|preview|state)': {
        target: backend,
        changeOrigin: true,
      },
    },
  },
};
