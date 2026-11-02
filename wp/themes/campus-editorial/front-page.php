<?php get_header();
$lead = get_posts( array( 'post_type' => array( 'campus_guide', 'campus_profile', 'campus_comparison' ), 'posts_per_page' => 4, 'orderby' => 'modified' ) );
$schools = get_posts( array( 'post_type' => 'campus_school', 'posts_per_page' => 20, 'orderby' => 'title', 'order' => 'ASC' ) );
$tools = get_posts( array( 'post_type' => 'campus_tool', 'posts_per_page' => 6 ) );
?>
<div class="container"><div class="grid" style="margin-top:var(--s-6)">
<section class="col-12 col-lg-8 lead-story">
<?php if ( $lead ) : $first = array_shift( $lead ); ?>
	<p class="eyebrow"><?php echo esc_html( get_post_type_object( $first->post_type )->label ); ?></p>
	<h2><a href="<?php echo esc_url( get_permalink( $first ) ); ?>"><?php echo esc_html( get_the_title( $first ) ); ?></a></h2>
	<p class="deck"><?php echo esc_html( get_the_excerpt( $first ) ); ?></p>
	<p class="meta"><?php echo esc_html( campus_meta( 'byline', $first ) ?: 'Publication desk' ); ?> · Verified <?php echo esc_html( get_the_modified_date( 'F j, Y', $first ) ); ?></p>
	<?php if ( $lead ) : ?><h2 class="section-head">Also verified recently</h2><ul class="story-list"><?php foreach ( $lead as $p ) : ?><li><p class="eyebrow"><?php echo esc_html( get_post_type_object( $p->post_type )->label ); ?></p><h3><a href="<?php echo esc_url( get_permalink( $p ) ); ?>"><?php echo esc_html( get_the_title( $p ) ); ?></a></h3><p><?php echo esc_html( get_the_excerpt( $p ) ); ?></p></li><?php endforeach; ?></ul><?php endif; ?>
<?php else : ?><div class="typographic-cover"><p class="big">Nothing published yet.</p><p class="small">The first verified guides appear here when they pass review. No placeholder stories are shown.</p></div><?php endif; ?>
</section>
<aside class="col-12 col-lg-4">
	<h2 class="section-head" style="margin-top:0">Find your school</h2>
	<form class="search-form" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>"><label class="visually-hidden" for="q">Search</label><input id="q" type="search" name="s" placeholder="School, building, program…"><button class="btn" type="submit">Search</button></form>
	<h2 class="section-head">Tools</h2><ul class="entry-points"><?php foreach ( $tools as $t ) : ?><li><a href="<?php echo esc_url( get_permalink( $t ) ); ?>"><?php echo esc_html( get_the_title( $t ) ); ?></a></li><?php endforeach; if ( ! $tools ) : ?><li><span class="coverage-note">No tools published yet.</span></li><?php endif; ?></ul>
	<h2 class="section-head">Schools with coverage</h2><ul class="entry-points"><?php foreach ( $schools as $s ) : ?><li><a href="<?php echo esc_url( get_permalink( $s ) ); ?>"><?php echo esc_html( get_the_title( $s ) ); ?></a></li><?php endforeach; if ( ! $schools ) : ?><li><span class="coverage-note">None yet.</span></li><?php endif; ?></ul>
</aside>
</div></div>
<?php get_footer();
