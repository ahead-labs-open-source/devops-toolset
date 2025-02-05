module.exports = {
    files: "../../../wordpress/wp-content/themes/{{theme-name}}",
    ghostMode: {
        clicks: false,
        forms: false,
        location: false,
        scroll: false
    },
    ignore: ["node_modules"],
    injectChanges: false,
    logLevel: "info",
    minify: false,
    notify: true,
    proxy: "{{development-environment-base-url}}",
    reloadOnRestart: true
}
