REM Show files of the directory passed as a parameter

echo "Script path: " %~dp0
echo "Path being showed: " %1
tree /f /a %1
