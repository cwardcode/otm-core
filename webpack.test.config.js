"use strict";

const { merge } = require('webpack-merge');
const config = require('./webpack.common.config.js');
const webpack = require('webpack');

module.exports = merge(config, {
    mode: 'development',
    entry: {
        'js/testRunner': __dirname + '/assets/tests/testRunner.js'
    },
    // Put a dummy value in place of the django reverse module in test mode
    externals: {
        reverse: "undefined"
    },
    // We only want the ProvidePlugin for tests (first plugin in common config)
    plugins: [
        new webpack.ProvidePlugin({
            jQuery: "jquery",
            "window.jQuery": "jquery",
            L: "leaflet"
        })
    ]
});
