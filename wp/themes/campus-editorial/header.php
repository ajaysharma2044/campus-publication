<!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link" href="#main">Skip to main content</a>
<?php if ( campus_is_staging() ) : ?><div class="staging-banner" role="note">Staging — <?php echo esc_html( wp_get_environment_type() ); ?> environment. Not the published site. No ads or analytics are emitted here.</div><?php endif; ?>
<div class="utility"><div class="container"><span><?php echo esc_html( wp_date( 'l, F j, Y' ) ); ?></span><span><a href="<?php echo esc_url( home_url( '/?s=' ) ); ?>">Search</a> · <a href="<?php echo esc_url( home_url( '/about/methods/' ) ); ?>">How this site is made</a></span></div></div>
<header class="masthead <?php echo is_front_page() ? '' : 'masthead--compact container'; ?>">
	<?php if ( is_front_page() ) : ?><div class="container"><h1 class="masthead__name"><a href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php bloginfo( 'name' ); ?></a></h1><p class="masthead__tag"><?php bloginfo( 'description' ); ?></p></div>
	<?php else : ?><p class="masthead__name"><a href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php bloginfo( 'name' ); ?></a></p><p class="masthead__tag"><?php bloginfo( 'description' ); ?></p><?php endif; ?>
</header>
<nav class="nav" aria-label="Sections"><div class="container"><?php wp_nav_menu( array( 'theme_location' => 'sections', 'container' => false, 'fallback_cb' => 'campus_nav_fallback', 'depth' => 1 ) ); ?></div></nav>
<main id="main" tabindex="-1">
<?php
function campus_nav_fallback() {
	echo '<ul>';
	foreach ( array( '/schools/' => 'Schools', '/topic/housing/' => 'Housing', '/topic/costs-aid/' => 'Costs & aid', '/topic/transfer/' => 'Transfer', '/tools/' => 'Tools', '/about/methods/' => 'Methods' ) as $href => $label ) {
		echo '<li><a href="' . esc_url( home_url( $href ) ) . '">' . esc_html( $label ) . '</a></li>';
	}
	echo '</ul>';
}
