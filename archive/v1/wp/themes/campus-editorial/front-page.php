<?php get_header();
$lead = get_posts( array( 'post_type' => array( 'campus_guide', 'campus_profile', 'campus_comparison' ), 'posts_per_page' => 4, 'orderby' => 'modified' ) );
$schools = get_posts( array( 'post_type' => 'campus_school', 'posts_per_page' => 20, 'orderby' => 'title', 'order' => 'ASC' ) );
$tools = get_posts( array( 'post_type' => 'campus_tool', 'posts_per_page' => 6 ) );
$first = $lead ? array_shift( $lead ) : null;
$first_img = $first && has_post_thumbnail( $first ) ? get_the_post_thumbnail_url( $first, 'large' ) : '';
?>
<div class="home">
<section class="hero"><div class="container">
<?php if ( $first ) : ?>
	<div class="hero__grid<?php echo $first_img ? '' : ' hero__grid--text'; ?>">
		<?php if ( $first_img ) : ?><a class="hero__media" href="<?php echo esc_url( get_permalink( $first ) ); ?>" tabindex="-1" aria-hidden="true"><img src="<?php echo esc_url( $first_img ); ?>" alt="" fetchpriority="high"></a><?php endif; ?>
		<div class="hero__text lead-story">
			<p class="eyebrow"><?php echo esc_html( get_post_type_object( $first->post_type )->label ); ?></p>
			<h2><a href="<?php echo esc_url( get_permalink( $first ) ); ?>"><?php echo esc_html( get_the_title( $first ) ); ?></a></h2>
			<p class="deck"><?php echo esc_html( get_the_excerpt( $first ) ); ?></p>
			<p class="meta"><?php echo esc_html( campus_meta( 'byline', $first ) ?: 'Publication desk' ); ?> · Verified <?php echo esc_html( get_the_modified_date( 'F j, Y', $first ) ); ?></p>
			<a class="btn" href="<?php echo esc_url( get_permalink( $first ) ); ?>">Read the guide</a>
		</div>
	</div>
<?php else : ?><div class="typographic-cover"><p class="big">Nothing published yet.</p><p class="small">The first verified guides appear here when they pass review. No placeholder stories are shown.</p></div><?php endif; ?>
</div></section>
<section class="band band--search" aria-labelledby="search-head"><div class="container">
	<h2 id="search-head" class="section-title">Start with your school</h2>
	<form class="search-form search-form--big" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>"><label class="visually-hidden" for="q">Search</label><input id="q" type="search" name="s" placeholder="School, building, program…"><button class="btn" type="submit">Search</button></form>
	<p class="coverage-note"><?php echo esc_html( count( $schools ) ); ?> <?php echo 1 === count( $schools ) ? 'school' : 'schools'; ?> with verified pages. Coverage is school-specific and labeled.</p>
</div></section>
<div class="container">
<?php if ( $lead ) : ?>
	<section class="home-section"><h2 class="section-title">Also verified recently</h2><div class="card-grid card-grid--3">
	<?php foreach ( $lead as $p ) : $img = has_post_thumbnail( $p ) ? get_the_post_thumbnail_url( $p, 'medium_large' ) : ''; ?>
		<article class="card"><?php if ( $img ) : ?><a href="<?php echo esc_url( get_permalink( $p ) ); ?>" tabindex="-1" aria-hidden="true"><img src="<?php echo esc_url( $img ); ?>" alt="" loading="lazy"></a><?php endif; ?><div class="card__body"><p class="eyebrow"><?php echo esc_html( get_post_type_object( $p->post_type )->label ); ?></p><h3><a href="<?php echo esc_url( get_permalink( $p ) ); ?>"><?php echo esc_html( get_the_title( $p ) ); ?></a></h3><p><?php echo esc_html( get_the_excerpt( $p ) ); ?></p></div></article>
	<?php endforeach; ?>
	</div></section>
<?php endif; ?>
	<section class="home-section two-up">
		<div><h2 class="section-title">Tools</h2><ul class="entry-points"><?php foreach ( $tools as $t ) : ?><li><a href="<?php echo esc_url( get_permalink( $t ) ); ?>"><?php echo esc_html( get_the_title( $t ) ); ?></a></li><?php endforeach; if ( ! $tools ) : ?><li><span class="coverage-note">No tools published yet.</span></li><?php endif; ?></ul></div>
		<div><h2 class="section-title">Schools with coverage</h2>
		<?php if ( $schools ) : ?><div class="card-grid"><?php foreach ( $schools as $s ) : $img = has_post_thumbnail( $s ) ? get_the_post_thumbnail_url( $s, 'medium_large' ) : ''; ?><a class="card" href="<?php echo esc_url( get_permalink( $s ) ); ?>"><?php if ( $img ) : ?><img src="<?php echo esc_url( $img ); ?>" alt="" loading="lazy"><?php endif; ?><span class="card__body"><span class="card__title"><?php echo esc_html( get_the_title( $s ) ); ?></span></span></a><?php endforeach; ?></div>
		<?php else : ?><p class="coverage-note">None yet.</p><?php endif; ?>
		</div>
	</section>
</div>
<section class="band band--how" aria-labelledby="how-head" style="margin-top:var(--s-8)"><div class="container">
	<h2 id="how-head" class="section-title">How this site works</h2>
	<div class="home-how__cols">
		<div><h3>Every number carries a date</h3><p>Facts show when we last verified them and the source we used. “Unknown” means no source states it, not that the answer is no.</p></div>
		<div><h3>Pages are school-specific</h3><p>Coverage is labeled by institution. We do not generalize from one campus to another, and we say when a topic does not apply.</p></div>
		<div><h3>Tools use the same records</h3><p>The calculator and comparisons are built from the verified fact tables, so a corrected rate updates the guide, the comparison and the total at once.</p></div>
	</div>
	<p class="home-how__more"><a href="<?php echo esc_url( home_url( '/about/methods/' ) ); ?>">How this site is made</a> · <a href="<?php echo esc_url( home_url( '/about/corrections/' ) ); ?>">Corrections</a></p>
</div></section>
</div>
<?php get_footer();
