const path = require("path");
module.exports = {
    devtool: "source-map",
    entry: {
        "GenerateKey": "./bunny/components/GenerateKey.js",
        "Unlock": "./bunny/components/Unlock.js",
        "Check": "./bunny/utils/Check.js",
        "Sent": "./bunny/components/Sent.js",
    },
    output: {
        path: path.resolve(__dirname, "static"),
        filename: "js/bundles/[name].js"
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader?cacheDirectory=/tmp/"
                }
            },
            {
                test: /\.css$/,
                use: [ 'style-loader', 'css-loader' ]
            }
        ]
    },
    optimization: {
        splitChunks: {
            cacheGroups: {
                default: false,
                commons: {
                    test: /[\\/]node_modules[\\/]/,
                    name: "vendor",
                    chunks: "all"
                }
            }
        }
    },
};
