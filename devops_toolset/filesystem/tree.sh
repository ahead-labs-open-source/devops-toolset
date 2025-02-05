# Install tree tool
sudo apt-get install tree

# Show files of the directory passed as a parameter
echo "Script path (\$0): $0"
echo "Path being showed (\$1): $1"
tree $1
