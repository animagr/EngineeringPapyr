import svelte from "rollup-plugin-svelte";
import typescript from "@rollup/plugin-typescript";
import resolve from "@rollup/plugin-node-resolve";
import livereload from "rollup-plugin-livereload";
import terser from "@rollup/plugin-terser";
import json from "@rollup/plugin-json";
import css from "rollup-plugin-css-only";
import copy from "rollup-plugin-copy";
import del from "rollup-plugin-delete";
import bundleFonts from "rollup-plugin-bundle-fonts";
import { sveltePreprocess } from "svelte-preprocess";
import commonjs from "@rollup/plugin-commonjs";
import { optimizeImports } from "carbon-preprocess-svelte";
import replace from "@rollup/plugin-replace";
import url from "@rollup/plugin-url";

const production = !process.env.ROLLUP_WATCH;

export default [
  {
    input: "src/parser/parserWorker.ts",
    output: {
      format: "iife",
      file: "public/parserWorker.js",
    },
    plugins: [
      optimizeImports(),
      commonjs(),
      resolve({
        browser: true,
        exportConditions: [production ? "production" : "development"],
      }),
      typescript({ tsconfig: "tsconfig.json" }),
    ],
    watch: {
      clearScreen: false,
    },
  },
  {
    input: "src/main.js",
    output: {
      sourcemap: !production,
      format: "es",
      name: "app",
      dir: "public/build",
    },
    plugins: [
      del({ targets: "public/build/*", runOnce: true }),
      replace({
        __STANDALONE__: JSON.stringify(true),
        preventAssignment: true,
      }),
      url({
        include: ["**/*.wasm"],
        limit: 0,
        publicPath: "/build/",
        destDir: "public/build",
      }),
      copy({
        targets: [
          {
            src: "node_modules/mathlive/dist/fonts/*",
            dest: "public/build/mathlive/fonts",
          },
          {
            src: "node_modules/mathlive/dist/sounds/*",
            dest: "public/build/mathlive/sounds",
          },
          {
            src: "node_modules/mathjax/es5/tex-svg.js",
            dest: "public/build/mathjax",
          },
        ],
      }),

      json(),
      optimizeImports(),

      svelte({
        preprocess: sveltePreprocess(),
      }),

      bundleFonts({
        fontTargetDir: "public/fonts",
        cssBundleDir: "public/build",
      }),

      css({ output: "bundle.css" }),

      resolve({
        browser: true,
        dedupe: ["svelte"],
        exportConditions: [production ? "production" : "development"],
      }),
      commonjs(),
      typescript({ sourceMap: !production, resolveJsonModule: true }),

      production && terser(),

      !production && livereload("public"),
    ],
    watch: {
      clearScreen: false,
    },
  },
];
