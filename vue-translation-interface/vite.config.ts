import { fileURLToPath } from "node:url"
import vue from "@vitejs/plugin-vue"
import AutoImport from "unplugin-auto-import/vite"
import Components from "unplugin-vue-components/vite"
import { defineConfig } from "vite"
import vueDevTools from "vite-plugin-vue-devtools"

const absolute = (path: string) => fileURLToPath(import.meta.resolve(path))

// https://vite.dev/config/
export default defineConfig({
  base: "/static/vue-ui",
  build: {
    outDir: absolute("../src/traduko/static/vue-ui"),
    emptyOutDir: true,
    manifest: "manifest.json",
    rollupOptions: { input: { app: "src/main.ts" } },
  },
  clearScreen: false,
  plugins: [
    vue(),
    vueDevTools(),
    AutoImport({ imports: ["vue"], dts: true }),
    Components(),
  ],
  resolve: { alias: { "@": absolute("./src") } },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "${absolute("./src/assets/scss/_variables.scss")}" as *;`,
      },
    },
  },
  server: { host: "0.0.0.0", port: 5173 },
})
