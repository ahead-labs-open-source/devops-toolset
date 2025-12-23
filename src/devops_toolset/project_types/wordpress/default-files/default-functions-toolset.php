<?php
/**
 * @param $relativeFontPath string Font relative path
 * @return string Image URI
 */
function {{theme-name}}_get_font_path(string $relativeFontPath): string
{
    return get_stylesheet_directory_uri() . '/assets/font/' . $relativeFontPath;
}

/**
 * @param $relativeImagePath string Image relative path
 * @return string Image URI
 */
function {{theme-name}}_get_image_path(string $relativeImagePath): string
{
    return get_stylesheet_directory_uri() . '/assets/images/' . $relativeImagePath;
}
