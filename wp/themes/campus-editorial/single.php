<?php
/** Article / profile / comparison / tool / policy renderer (mirrors worker templates). */
get_header();
while ( have_posts() ) : the_post();
	$type = get_post_type();
	$byline = campus_meta( 'byline' ) ?: 'Publication desk';
	$updated = campus_meta( 'material_updated_at' );
	$structured = campus_meta_json( 'structured' );
	$section = campus_meta( 'topic_key' ) ? ucfirst( str_replace( '_', ' ', campus_meta( 'topic_key' ) ) ) : get_post_type_object( $type )->label;
?>
<div class="container"><div class="grid">
<article class="article col-12 <?php echo in_array( $type, array( 'campus_guide', 'campus_profile' ), true ) ? 'col-lg-8' : ''; ?>">
	<p class="eyebrow"><?php echo esc_html( $section ); ?></p>
	<h1><?php the_title(); ?></h1>
	<?php if ( has_excerpt() ) : ?><p class="deck measure"><?php echo esc_html( get_the_excerpt() ); ?></p><?php endif; ?>
	<div class="byline"><span><b><?php echo esc_html( $byline ); ?></b></span><span>Published <time datetime="<?php echo esc_attr( get_the_date( 'c' ) ); ?>"><?php echo esc_html( get_the_date( 'F j, Y' ) ); ?></time></span><?php if ( $updated && substr( $updated, 0, 10 ) !== get_the_date( 'Y-m-d' ) ) : ?><span>Substantively updated <time datetime="<?php echo esc_attr( $updated ); ?>"><?php echo esc_html( wp_date( 'F j, Y', strtotime( $updated ) ) ); ?></time></span><?php endif; ?><?php if ( campus_meta( 'audience' ) ) : ?><span>For: <?php echo esc_html( str_replace( '_', ' ', campus_meta( 'audience' ) ) ); ?></span><?php endif; ?></div>
	<?php
	$content = apply_filters( 'the_content', get_the_content() );
	$parts = explode( '[[fact-table]]', $content, 2 );
	echo '<div class="prose measure">' . $parts[0] . '</div>';
	campus_fact_table();
	if ( isset( $parts[1] ) ) { echo '<div class="prose measure">' . $parts[1] . '</div>'; }
	echo campus_ad_slot( 'campus_profile' === $type ? 'after_facts' : 'after_essentials' );
	campus_next_actions();
	campus_sources();
	?>
</article>
<?php if ( in_array( $type, array( 'campus_guide', 'campus_profile' ), true ) ) : ?><aside class="col-12 col-lg-4"><?php echo campus_ad_slot( 'desktop_sidebar' ); ?></aside><?php endif; ?>
</div></div>
<?php endwhile; get_footer();
