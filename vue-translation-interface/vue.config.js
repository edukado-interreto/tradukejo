module.exports = {
  outputDir: '../traduko/static/traduko/vue-translation-interface',
  publicPath: '/static/traduko/vue-translation-interface/',
  css: {
    loaderOptions: {
      sass: {
        additionalData: '@import "@/assets/scss/_variables.scss";',
        sassOptions: {
          quietDeps: true
        }
      }
    }
  },
  productionSourceMap: false
}
