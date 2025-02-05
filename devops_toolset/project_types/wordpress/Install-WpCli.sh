# Download PHAR file
curl https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar -o "$1/wp-cli.phar"

# Grant it execution permission and move it to user's execution path
chmod +x "$1/wp-cli.phar"
sudo mv "$1/wp-cli.phar" /usr/local/bin/wp

# Show WP CLI information
wp --info
