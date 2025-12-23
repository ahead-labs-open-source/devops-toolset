/*
Call this script passing the following parameters in strict order:
    gulp build --theme-slug="<theme slug>" --wordpress-path="<directory path>"
    gulp watch --theme-slug="<theme slug>" --dev-proxy="<local web server>" --wordpress-path="<directory path>"
*/

'use strict';

// Add theme directory to the argument array
process.argv.push(`--theme-path="${__dirname}"`);

// Gulp and plugins
const
w74 = require('@aheadlabs/gulp-w74framework')
;
exports.build = w74.build;
exports.watch = w74.watch;
