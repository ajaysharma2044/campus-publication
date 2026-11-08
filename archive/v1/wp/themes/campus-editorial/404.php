<?php get_header(); ?>
<div class="container"><article class="article measure"><div class="typographic-cover"><p class="big" aria-hidden="true">404</p><h1 style="font-size:var(--fs-h2)">Page not found</h1><p class="small">That page does not exist or was removed.</p></div>
<p>If a school renamed a building or program, the old address usually redirects. <a href="<?php echo esc_url( home_url( '/schools/' ) ); ?>">Browse schools with coverage</a> · <a href="<?php echo esc_url( home_url( '/?s=' ) ); ?>">Search</a></p></article></div>
<?php get_footer();
