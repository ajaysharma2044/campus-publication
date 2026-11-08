<?php
// Non-interactive install + activation for the local staging WordPress. Run from wp-local/wordpress: php ../../scripts/wp_install.php
define( 'WP_INSTALLING', true );
require_once getcwd() . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/upgrade.php';
require_once ABSPATH . 'wp-admin/includes/plugin.php';
if ( ! is_blog_installed() ) {
	$r = wp_install( 'Footnote Daily (staging)', 'campusadmin', 'admin@example.invalid', false, '', 'local-dev-password-only' );
	echo "installed user_id={$r['user_id']}\n";
}
activate_plugin( 'campus-core/campus-core.php' );
switch_theme( 'campus-editorial' );
update_option( 'permalink_structure', '/%postname%/' );
update_option( 'blog_public', 1 ); // sitemaps need this; staging still sends noindex via WP_ENVIRONMENT_TYPE
update_option( 'blogdescription', 'Independent guidance for college decisions · working masthead' );
flush_rewrite_rules( false );
$user = get_user_by( 'login', 'campusadmin' );
$pw = WP_Application_Passwords::create_new_application_password( $user->ID, array( 'name' => 'campus-worker-local' ) );
echo "app_password=" . $pw[0] . "\n";
echo "plugin_active=" . ( is_plugin_active( 'campus-core/campus-core.php' ) ? 'yes' : 'no' ) . " theme=" . wp_get_theme()->get( 'Name' ) . "\n";
