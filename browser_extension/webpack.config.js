const webpack = require('webpack');
const CopyPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const path = require('path');
const outputPath = 'dist';
const entryPoints = {
    main: [
        path.resolve(__dirname, 'src', 'sidePanelApp.tsx'),
        path.resolve(__dirname, 'scss', 'main.scss')
    ],
    background: path.resolve(__dirname, 'src', 'background.ts'),
    runOnceActions: path.resolve(__dirname, 'src', 'runOnceActions.ts')
};

module.exports = {
    entry: entryPoints,
    output: {
        path: path.join(__dirname, outputPath),
        filename: '[name].js',
    },
    resolve: {
        extensions: ['.ts', '.js', '.jsx', '.tsx'],
    },
    devtool: "cheap-module-source-map",
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                loader: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                test: /\.(sa|sc|c)ss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader'
                ]
            },
            {
                test: /\.(jpg|jpeg|png|gif|woff|woff2|eot|ttf|svg)$/i,
                use: 'url-loader?limit=1024'
            }
        ],
    },
    plugins: [
        new CopyPlugin({
            patterns: [{ from: '.', to: '.', context: 'public' }]
        }),
        new MiniCssExtractPlugin({
            filename: '[name].css',
        }),
        new webpack.DefinePlugin({
            'process.env.QUIZ_ONLY': JSON.stringify(process.env.QUIZ_ONLY || 'false')
        })
    ],
    cache: {
        type: 'filesystem'
    }
};