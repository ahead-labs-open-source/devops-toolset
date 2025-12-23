const
    CopyWebpackPlugin = require("copy-webpack-plugin"),
    FileManagerPlugin = require("filemanager-webpack-plugin"),
    MiniCssExtractPlugin = require("mini-css-extract-plugin"),
    packageJson = require("./package.json"),
    path = require("path"),
    siteConfig = require("../../../site.json"),
    version = "{{project-version}}";

module.exports = (env) => {
    // Parse parameters
    env.environment = !env.environment ? "localhost" : env.environment;
    let mode = env.environment === "localhost" ? "development" : "production";
    let environmentConfig = siteConfig.environments.find(e => e.name === env.environment);
    let relativeDistPath = 'dist';
    let wordpressDistPath = `../../../wordpress${environmentConfig.wp_config.content_url.value}/themes/aheadlabs`;
    let distJsPath = "assets/js";

    // Log values
    console.log("Webpack configuration version", version)
    console.log("Environment: ", env.environment);
    console.log("Mode: ", mode);

    // Config object
    let config = {
        entry: [
            "./src/assets/ts/main"
        ],
        mode: mode,
        module: {
            rules: [
                {
                    test: /\.ts$/,
                    exclude: /node_modules/,
                    use: "ts-loader"
                },
                {
                    test: /\.s[ac]ss$/i,
                    exclude: /node_modules/,
                    use: [
                        MiniCssExtractPlugin.loader,
                        "css-loader",
                        {
                            loader: "postcss-loader",
                            options: {
                                postcssOptions: {
                                    plugins: [["postcss-preset-env", {}]]
                                }
                            }
                        },
                        "sass-loader"
                    ]
                },
                {
                    test: /style\.s[ac]ss$/i,
                    exclude: /node_modules/,
                    use: {
                        loader: "string-replace-loader",
                        options: {
                            search: "{{version}}",
                            replace: packageJson.version
                        }
                    }
                },
            ]
        },
        output: {
            filename: `${distJsPath}/main.js`,
            path: path.resolve(__dirname, relativeDistPath),
            clean: true
        },
        plugins: [
            new MiniCssExtractPlugin({filename: "style.css"}),
            new CopyWebpackPlugin({
                patterns: [
                    {
                        from: "src/composer.json",
                        to({context, absoluteFilename}) {
                            return path.relative(context, absoluteFilename).replace(/src[\\\/]/g, "");
                        }
                    },
                    {
                        from: "src/**/*.php",
                        to({context, absoluteFilename}) {
                            return path.relative(context, absoluteFilename).replace(/src[\\\/]/g, "");
                        }
                    },
                    {
                        from: "screenshot.png"
                    },
                    {
                        from: "src/assets/images/**/*.@(png|jpg|jpeg|gif|svg|webp)",
                        to({context, absoluteFilename}) {
                            return path.relative(context, absoluteFilename).replace(/src[\\\/]/g, "");
                        },
                        noErrorOnMissing: true
                    },
                    {
                        from: "src/assets/fonts/**/*.@(ttf|otf|eot|woff|woff2|svg)",
                        to({context, absoluteFilename}) {
                            return path.relative(context, absoluteFilename).replace(/src[\\\/]/g, "");
                        },
                        noErrorOnMissing: true
                    },
                ]
            }),
            new FileManagerPlugin({
                events: {
                    onEnd: {
                        copy: [
                            {
                                source: path.resolve(__dirname, relativeDistPath),
                                destination: path.resolve(__dirname, wordpressDistPath)
                            }
                        ]
                    }
                }
            }),
        ],
        resolve: {
            extensions: [".ts", ".js"]
        },
        watchOptions: {
            ignored: /node_modules/
        }
    }

    // Source map
    if(mode === "development") {
        config.devtool = "inline-source-map";
    }

    return config;
}
