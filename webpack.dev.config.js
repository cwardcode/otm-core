"use strict";

const { merge } = require('webpack-merge');
const webpack = require('webpack');
const config = require('./webpack.common.config.js');

const host = process.env.WEBPACK_DEV_SERVER || 'http://localhost:6062/';

module.exports = merge(config, {
    mode: 'development',
    output: {
        publicPath: host + 'static/'
    },
    devtool: 'eval-source-map',
    plugins: [
        new webpack.HotModuleReplacementPlugin()
    ],
    // Allows require-ing the global variable created by django-js-reverse
    externals: {
        reverse: "Urls"
    },
    watchOptions: {
        poll: 1000
    },
    devServer: {
        host: '0.0.0.0',
        port: 6062,
        hot: true,
        static: {
            directory: './static'
        },
        proxy: {
            '/static': {
                target: 'http://localhost',
                secure: false
            }
        }
    }
});
