"use strict";

const { merge } = require('webpack-merge');
const webpack = require('webpack');
const config = require('./webpack.common.config.js');
const reversePath = __dirname + '/assets/js/shim/reverse.js';

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
    devtool: 'source-map',
    module: {
        rules: [
            {
                include: reversePath,
                use: [
                    {
                        loader: 'exports-loader',
                        options: { exports: 'Urls' }
                    }
                ]
            }
        ]
    },
    optimization: {
        minimize: true
    }
});
