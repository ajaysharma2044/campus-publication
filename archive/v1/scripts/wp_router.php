<?php
// Router for php -S: serve existing files, otherwise WordPress front controller (pretty permalinks).
$path = urldecode( parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH ) );
$file = __DIR__ === '' ? '' : getcwd() . $path;
if ( $path !== '/' && file_exists( $file ) && ! is_dir( $file ) ) { return false; }
if ( is_dir( $file ) && file_exists( $file . '/index.php' ) ) { chdir( $file ); require $file . '/index.php'; return true; }
$_SERVER['SCRIPT_NAME'] = '/index.php'; $_SERVER['PHP_SELF'] = '/index.php';
require getcwd() . '/index.php';
