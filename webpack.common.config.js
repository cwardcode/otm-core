"use strict";

const webpack = require("webpack");
const { globSync } = require("glob");
const path = require("path");
const _ = require("lodash");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const autoprefixer = require("autoprefixer");

const isProd = process.env.NODE_ENV === "production";

// Execute globs once per config evaluation to reduce startup I/O.
const GLOBAL_JS_FILES = globSync("opentreemap/*/js/src/*.js");
const GLOBAL_DIR_ALIASES = globSync("opentreemap/*/js/src/*/");
const GLOBAL_VENDOR_MODULES = globSync(path.resolve(__dirname, "opentreemap/*/js/vendor/"));

function d(p) {
  // Turns a relative path into an absolute path from the project root
  return path.resolve(__dirname, p);
}

function getEntries() {
  const entries = {};
  GLOBAL_JS_FILES.forEach(function (file) {
    // file = 'opentreemap/treemap/js/src/treeMap.js'
    // parts: ['opentreemap', 'treemap', 'js', 'src', 'treeMap.js']
    const parts = file.split(path.sep);
    const app = parts[1];
    const basename = path.basename(file, ".js");
    entries["js/" + app + "/" + basename] = "./" + file;
  });
  return entries;
}

function getAliases() {
  const aliases = {};
  GLOBAL_DIR_ALIASES.forEach(function (thePath) {
    const parts = thePath.split(path.sep);
    const app = parts[1]; // e.g. 'treemap'
    const dir = parts[4]; // e.g. 'lib', 'mapPage'
    const alias = app + path.sep + dir;
    const target = thePath.replace(/\/$/, ""); // strip trailing slash
    aliases[alias] = d(target);
  });
  return _.merge(aliases, shimmed);
}

const shimmed = {
  leafletbing: d("assets/js/shim/leaflet.bing.js"),
  utfgrid: d("assets/js/shim/leaflet.utfgrid.js"),
  typeahead: d("assets/js/shim/typeahead.jquery.js"),
  bootstrap: d("assets/js/shim/bootstrap.js"),
  jqueryFileUpload: d("assets/js/shim/jquery.fileupload.js"),
  jqueryIframeTransport: d("assets/js/shim/jquery.iframe-transport.js"),
  jqueryUiWidget: d("assets/js/shim/jquery.ui.widget.js"),
  ionRangeSlider: d("assets/js/shim/ion.rangeSlider.js"),
  "bootstrap-datepicker": d("assets/js/shim/bootstrap-datepicker.js"),
  "bootstrap-multiselect": d("assets/js/shim/bootstrap-multiselect.js"),
  jscolor: d("assets/js/shim/jscolor.js"),
};

module.exports = {
  cache: {
    type: "filesystem",
    cacheDirectory: d(".webpack-cache"),
    compression: false,
    buildDependencies: {
      config: [
        __filename,
        d("webpack.prod.config.js"),
        d("webpack.dev.config.js"),
        d("webpack.test.config.js"),
      ],
    },
  },
  entry: getEntries(),
  output: {
    filename: "[name].js",
    path: d("static"),
    sourceMapFilename: "[file].map",
  },
  module: {
    rules: [
      {
        // Import bootstrap shims before bootstrap-datepicker and bootstrap-multiselect
        include: [
          shimmed["bootstrap-datepicker"],
          shimmed["bootstrap-multiselect"],
        ],
        use: [
          {
            loader: "imports-loader",
            options: { imports: "default bootstrap bootstrap" },
          },
        ],
      },
      {
        test: /\.scss$/,
        use: [
          // Use style-loader in dev (injects CSS into DOM), MiniCssExtractPlugin in prod
          isProd ? MiniCssExtractPlugin.loader : "style-loader",
          "css-loader",
          {
            loader: "postcss-loader",
            options: {
              postcssOptions: {
                plugins: [autoprefixer],
              },
            },
          },
          {
            loader: "sass-loader",
            options: {
              api: "modern",
              sassOptions: {
                silenceDeprecations: ["import", "legacy-js-api"],
              },
            },
          },
        ],
      },
      {
        test: /\.woff($|\?)|\\.woff2($|\?)|\\.ttf($|\?)|\\.eot($|\?)|\\.svg($|\?)/,
        type: "asset/resource",
      },
      {
        test: /\.(jpg|png|gif)$/,
        type: "asset",
        parser: {
          dataUrlCondition: { maxSize: 25000 },
        },
      },
    ],
  },
  resolve: {
    alias: getAliases(),
    preferRelative: true,
    modules: [d("assets/js/vendor"), d("node_modules")].concat(
      GLOBAL_VENDOR_MODULES,
    ),
    // webpack 5 no longer auto-polyfills Node.js core modules.
    // These built-ins are only used by server-side dependencies; disable them for the browser bundle.
    fallback: {
      crypto: false,
      util: false,
      url: false,
      path: false,
      fs: false,
      stream: false,
      buffer: false,
      http: false,
      https: false,
      os: false,
      assert: false,
      zlib: false,
      querystring: false,
    },
  },
  plugins: [
    // Provide jquery and Leaflet as global variables, which gets rid of
    // most of our shimming needs
    new webpack.ProvidePlugin({
      jQuery: "jquery",
      "window.jQuery": "jquery",
      L: "leaflet",
    }),
    new BundleTracker({ path: d("static"), filename: "webpack-stats.json" }),
  ].concat(
    isProd
      ? [new MiniCssExtractPlugin({ filename: "css/main-[contenthash].css" })]
      : [],
  ),
  optimization: {
    splitChunks: {
      cacheGroups: {
        base: {
          name: "js/treemap/base",
          minChunks: 2,
          priority: -10,
          reuseExistingChunk: true,
        },
      },
    },
  },
};
