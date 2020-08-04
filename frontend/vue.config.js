const backend = process.env.BACKEND || 'http://127.0.0.1:8080/';

module.exports = {
  devServer: {
    proxy: {
      '^/(login|ws)': {
        target: backend,
        changeOrigin: true,
      },
    },
  },
};
