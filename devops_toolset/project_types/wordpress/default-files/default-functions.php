<?php
/**
 * Add functions.php split files from <theme>/functions_php
 */
$directory_iterator = new DirectoryIterator(get_stylesheet_directory() . DIRECTORY_SEPARATOR . 'functions_php');
foreach ($directory_iterator as $functions_file){
    if ($functions_file -> isFile()){
        require_once $functions_file -> getPathname();
    }
}
