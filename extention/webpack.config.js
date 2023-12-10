const webpack = require('webpack');
const path = require('path');
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
    // mode: 'production',
    mode: 'development',
    entry: {
        bg: './background.js',
        cs: './content.js',
    },
    // devtool: false,
    devtool: 'cheap-source-map',
    output: {
        filename: '[name].js',
        charset: true
    },
    externals: {
        jquery: 'jQuery'
    },
    resolve: {
        extensions: ['.js']
    },
    module: {
        rules: [
            // {test: /\.json$/, use: 'raw-loader'}
            //         {
            //             test: /\.js$/,
            //             use: {
            //                 loader: 'babel-loader',
            //                 options: {
            //                     presets: ['es2015', 'stage-0']
            //                 },
            //             },
            //             exclude: /node_modules/
            //         }
        ]
    },
    plugins: [
        new CopyPlugin({
            patterns: [
                {from: "./source", to: "./"},
            ],
        }),
        // new webpack.optimize.UglifyJsPlugin()
    ]
};