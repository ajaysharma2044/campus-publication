</main>
<footer class="site-footer"><div class="container">
	<p class="disclosure"><b><?php bloginfo( 'name' ); ?></b> is an independent publication and is not affiliated with any college or university. Pages are produced by an automated research and writing system with deterministic fact checks and a model-based verification pass; where a human reviewed a page, the correction history says so. Facts carry the date we last verified them and the source we used.</p>
	<?php wp_nav_menu( array( 'theme_location' => 'footer', 'container' => false, 'depth' => 1, 'fallback_cb' => function () { echo '<ul><li><a href="' . esc_url( home_url( '/about/methods/' ) ) . '">Editorial methods & automation</a></li><li><a href="' . esc_url( home_url( '/about/corrections/' ) ) . '">Corrections</a></li><li><a href="' . esc_url( home_url( '/about/privacy/' ) ) . '">Privacy</a></li><li><a href="' . esc_url( home_url( '/about/independence/' ) ) . '">Sponsorship & independence</a></li></ul>'; } ) ); ?>
</div></footer>
<?php if ( campus_ads_enabled() && ! isset( $_COOKIE['campus_consent'] ) ) : ?>
<div class="notice notice--consent" role="dialog" aria-labelledby="consent-h"><p id="consent-h" style="margin:0">This site shows advertising only with your consent. Without it, pages work exactly the same.</p><div><button class="btn" type="button" onclick="document.cookie='campus_consent=ads;path=/;max-age=15552000;SameSite=Lax';location.reload()">Allow ads</button> <button class="btn btn--secondary" type="button" style="color:#fff;border-color:#fff" onclick="document.cookie='campus_consent=none;path=/;max-age=15552000;SameSite=Lax';this.closest('.notice').remove()">No thanks</button></div></div>
<?php endif; ?>
<?php wp_footer(); ?>
</body></html>
