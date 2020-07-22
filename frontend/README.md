# voctovue

This JS app is built out of [Vue.js][vue] with [Vuex][vuex].

[vue]: https://vuejs.org/v2/
[vuex]: https://vuex.vuejs.org/

## Project setup

Install the dependencies with `npm install` or `yarnpkg install`.

### Dev server with live-reload

The source isn't directly testable in a browser, so the easiest way to
develop is to use the built-in dev server.

Run it with `npm run serve`.

It will monitor changes to the source files, re-build, and re-load the
app in your browser.

By default, it will proxy requests for the backend URLs to
`http://127.0.0.1:8080/`, you can customize this in `vue.config.js`.
See the [Vue CLI Configuration Reference][vue-cli-config]

Vue has an optional [browser plugins][vue-devtools] to inspect Vue
components and state. It can be useful.

[vue-cli-config]: https://cli.vuejs.org/config/
[vue-devtools]: https://github.com/vuejs/vue-devtools

### Production build

To build, run `npm run build`. It will build into the `dist` directory.

### Lints and fixes files

```
npm run lint
```
