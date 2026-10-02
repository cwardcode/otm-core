"use strict";

const { merge } = require('webpack-merge');
const webpack = require('webpack');
const { EsbuildPlugin } = require('esbuild-loader');

// Ensure common config sees production mode while deciding loaders/plugins.
process.env.NODE_ENV = process.env.NODE_ENV || 'production';

const config = require('./webpack.common.config.js');
const reversePath = __dirname + '/assets/js/shim/reverse-shim.js';
const shouldUseSourceMap = process.env.GENERATE_SOURCEMAP === 'true';

module.exports = merge(config, {
    mode: 'production',
    plugins: [
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify('production')
        })
    ],
    output: {
        filename: '[name]-[contenthash].js',
        publicPath: '/static/'
    },
    resolve: {
        alias: Object.assign({}, config.resolve.alias, { reverse: reversePath })
    },
    // Source maps are expensive in production builds.
    // Enable only when explicitly requested.
    devtool: shouldUseSourceMap ? 'source-map' : false,
    optimization: {
        minimize: true,
        minimizer: [
            new EsbuildPlugin({
                target: 'es2015',
                css: true
            })
        ]
    }
});
