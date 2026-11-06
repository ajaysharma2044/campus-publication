<?php get_header();
$lead = get_posts( array( 'post_type' => array( 'campus_guide', 'campus_profile', 'campus_comparison' ), 'posts_per_page' => 4, 'orderby' => 'modified' ) );
$schools = get_posts( array( 'post_type' => 'campus_school', 'posts_per_page' => 20, 'orderby' => 'title', 'order' => 'ASC' ) );
$tools = get_posts( array( 'post_type' => 'campus_tool', 'posts_per_page' => 6 ) );
$first = $lead ? array_shift( $lead ) : null;
?>
<div class="container home"><div class="home-top<?php echo $lead ? "" : " home-top--single"; ?>">
<section class="home-lead lead-story">
<?php if ( $first ) : ?>
	<p class="eyebrow"><?php echo esc_html( get_post_type_object( $first->post_type )->label ); ?></p>
	<h2><a href="<?php echo esc_url( get_permalink( $first ) ); ?>"><?php echo esc_html( get_the_title( $first ) ); ?></a></h2>
	<p class="deck"><?php echo esc_html( get_the_excerpt( $first ) ); ?></p>
	<p class="meta"><?php echo esc_html( campus_meta( 'byline', $first ) ?: 'Publication desk' ); ?> · Verified <?php echo esc_html( get_the_modified_date( 'F j, Y', $first ) ); ?></p>
<?php else : ?><div class="typographic-cover"><p class="big">Nothing published yet.</p><p class="small">The first verified guides appear here when they pass review. No placeholder stories are shown.</p></div><?php endif; ?>
</section>
<?php if ( $lead ) : ?>
<section class="home-supporting"><h2 class="section-head">Also verified recently</h2><ul class="story-list story-list--compact"><?php foreach ( $lead as $p ) : ?><li><p class="eyebrow"><?php echo esc_html( get_post_type_object( $p->post_type )->label ); ?></p><h3><a href="<?php echo esc_url( get_permalink( $p ) ); ?>"><?php echo esc_html( get_the_title( $p ) ); ?></a></h3><p><?php echo esc_html( get_the_excerpt( $p ) ); ?></p></li><?php endforeach; ?></ul></section>
<?php endif; ?>
<aside class="home-rail">
	<h2 class="section-head">Start with your school</h2>
	<form class="search-form" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>"><label class="visually-hidden" for="q">Search</label><input id="q" type="search" name="s" placeholder="School, building, program…"><button class="btn" type="submit">Search</button></form>
	<p class="coverage-note"><?php echo esc_html( count( $schools ) ); ?> <?php echo 1 === count( $schools ) ? 'school' : 'schools'; ?> with verified pages. Coverage is school-specific and labeled.</p>
	<h2 class="section-head section-head--light">Tools</h2><ul class="entry-points"><?php foreach ( $tools as $t ) : ?><li><a href="<?php echo esc_url( get_permalink( $t ) ); ?>"><?php echo esc_html( get_the_title( $t ) ); ?></a></li><?php endforeach; if ( ! $tools ) : ?><li><span class="coverage-note">No tools published yet.</span></li><?php endif; ?></ul>
	<h2 class="section-head section-head--light">Schools with coverage</h2><ul class="entry-points"><?php foreach ( $schools as $s ) : ?><li><a href="<?php echo esc_url( get_permalink( $s ) ); ?>"><?php echo esc_html( get_the_title( $s ) ); ?></a></li><?php endforeach; if ( ! $schools ) : ?><li><span class="coverage-note">None yet.</span></li><?php endif; ?></ul>
</aside>
</div>
<section class="home-how" aria-labelledby="how-head">
	<h2 id="how-head" class="section-head">How this site works</h2>
	<div class="home-how__cols">
		<div><h3>Every number carries a date</h3><p>Facts show when we last verified them and the source we used. “Unknown” means no source states it, not that the answer is no.</p></div>
		<div><h3>Pages are school-specific</h3><p>Coverage is labeled by institution. We do not generalize from one campus to another, and we say when a topic does not apply.</p></div>
		<div><h3>Tools use the same records</h3><p>The calculator and comparisons are built from the verified fact tables, so a corrected rate updates the guide, the comparison and the total at once.</p></div>
	</div>
	<p class="home-how__more"><a href="<?php echo esc_url( home_url( '/about/methods/' ) ); ?>">How this site is made</a> · <a href="<?php echo esc_url( home_url( '/about/corrections/' ) ); ?>">Corrections</a></p>
</section>
</div>
<?php get_footer();
